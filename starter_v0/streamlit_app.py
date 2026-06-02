from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ROOT,
    ARTIFACTS_DIR,
    load_lab_env,
    run_model_tool_loop,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "ui_messages" not in st.session_state:
        st.session_state.ui_messages = []
    if "turn_index" not in st.session_state:
        st.session_state.turn_index = 0
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "transcript_path" not in st.session_state:
        st.session_state.transcript_path = None


def reset_chat() -> None:
    st.session_state.history = []
    st.session_state.ui_messages = []
    st.session_state.turn_index = 0
    st.session_state.transcript = None
    st.session_state.transcript_path = None


def build_transcript(version: str, provider_name: str, model: str | None, system_prompt: Path, tools_path: Path) -> None:
    artifact_version = build_artifact_version(version, system_prompt, tools_path)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{version}_{provider_name}_{ts}"
    transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    st.session_state.transcript_path = transcript_path
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt),
        "tools": str(tools_path),
        "history_window": 5,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def append_turn(
    user_text: str,
    result: dict[str, Any],
    error: str | None = None,
) -> None:
    turn = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "assistant_text": result.get("assistant_text") if result else None,
        "status": result.get("status") if result else "provider_error",
        "rounds": result.get("rounds", []) if result else [],
        "tool_events": result.get("tool_events", []) if result else [],
    }
    if error:
        turn["status"] = "provider_error"
        turn["error"] = error
    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


def main() -> None:
    st.set_page_config(page_title="Research Agent Chatbot", page_icon="🤖", layout="wide")
    ensure_state()

    st.title("Research Agent Chatbot")
    st.caption("Simple Streamlit UI for Day04 agent")

    with st.sidebar:
        st.header("Settings")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        version = st.text_input("Version", value="v5")
        model_override = st.text_input("Model override (optional)", value="")
        history_window = st.slider("History window (pairs)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=8, value=4)

        if st.button("New conversation", use_container_width=True):
            reset_chat()
            st.rerun()

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)

    provider = make_provider(provider_name)
    selected_model = model_override.strip() or getattr(provider, "default_model", None)

    st.info(
        f"Using `{provider_name}` | model `{selected_model}` | artifacts: "
        f"`{system_prompt_path.name}`, `{tools_path.name}`"
    )

    for msg in st.session_state.ui_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tool_events"):
                with st.expander("Tool events", expanded=False):
                    st.code(json.dumps(msg["tool_events"], ensure_ascii=False, indent=2), language="json")

    user_text = st.chat_input("Nhập câu hỏi...")
    if not user_text:
        return

    if st.session_state.transcript is None:
        build_transcript(version, provider_name, selected_model, system_prompt_path, tools_path)

    st.session_state.turn_index += 1
    st.session_state.ui_messages.append({"role": "user", "content": user_text})
    st.session_state.history.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model_override.strip() or None,
                    max_tool_rounds=max_tool_rounds,
                )
                assistant_text = result.get("assistant_text", "")
                st.markdown(assistant_text or "(No response)")
                if result.get("tool_events"):
                    with st.expander("Tool events", expanded=False):
                        st.code(json.dumps(result["tool_events"], ensure_ascii=False, indent=2), language="json")

                st.session_state.ui_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_text or "(No response)",
                        "tool_events": result.get("tool_events", []),
                    }
                )
                st.session_state.history.append({"role": "assistant", "content": assistant_text or ""})
                append_turn(user_text, result)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                st.error(error)
                st.session_state.ui_messages.append({"role": "assistant", "content": f"ERROR: {error}"})
                append_turn(user_text, {}, error=error)


if __name__ == "__main__":
    main()
