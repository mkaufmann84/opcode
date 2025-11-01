"""LangChain-based LLM utility supporting multiple providers with retries.

Available Models (Updated October 2025):

OpenAI models:
    - gpt-4o (current flagship multimodal)
    - gpt-5 (newest, August 2025)
    - o3, o3-mini (latest reasoning models)
    - o4-mini, o4-mini-high

Grok models (xAI):
    - grok-4-fast (40% fewer thinking tokens, 2M context)
    - grok-4 (most intelligent)
    - grok-4-heavy (flagship)

Gemini models (Google):
    - gemini-2.5-pro (most powerful)
    - gemini-2.5-flash (default)
    - gemini-2.5-flash-lite (most cost-effective)

Claude models (Anthropic):
    - claude-sonnet-4.5 (frontier model, best coding)
    - claude-opus-4.1 (advanced reasoning)
    - claude-haiku-4.5 (fast and efficient)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

try:  # Optional dependency
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore

try:  # Optional dependency
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - optional dependency
    ChatGoogleGenerativeAI = None  # type: ignore

try:  # Optional dependency
    from langchain_anthropic import ChatAnthropic
except ImportError:  # pragma: no cover - optional dependency
    ChatAnthropic = None  # type: ignore

try:  # Optional dependency
    from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        HumanMessage,
        SystemMessage,
    )
except ImportError:  # pragma: no cover - optional dependency
    AIMessage = BaseMessage = HumanMessage = SystemMessage = None  # type: ignore


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def load_env_file(path: str = ".env.local") -> None:
    """Load environment variables from a simple .env file if present."""
    # If path is relative, look for it in the script's directory
    if not os.path.isabs(path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, path)

    if not os.path.exists(path):
        return

    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
    except OSError as exc:
        eprint(f"⚠️  Could not read {path}: {exc}")


load_env_file()
@dataclass
class LangChainLLMConfig:
    model: str
    temperature: float = 0.2
    max_tokens: int = 2048
    thinking_budget: int = 0


class LangChainLLMClient:
    """Minimal LangChain wrapper supporting OpenAI, Gemini, Grok, and Claude."""

    def __init__(self, config: LangChainLLMConfig):
        self.config = config
        self.model = config.model
        lower_model = self.model.lower()

        self.provider = "openai"
        if "gemini" in lower_model:
            self.provider = "gemini"
        elif "grok" in lower_model:
            self.provider = "grok"
        elif "claude" in lower_model or "anthropic" in lower_model:
            self.provider = "anthropic"

        self.client = self._create_client()

    def _create_client(self):
        if self.provider == "gemini":
            if ChatGoogleGenerativeAI is None:
                raise RuntimeError(
                    "Install `langchain-google-genai` to use Gemini models."
                )
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise RuntimeError("GOOGLE_API_KEY is required for Gemini models.")
            return ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                google_api_key=api_key,
            )

        if self.provider == "grok":
            if ChatOpenAI is None:
                raise RuntimeError("Install `langchain-openai` to use Grok models.")
            api_key = os.environ.get("XAI_API_KEY")
            if not api_key:
                raise RuntimeError("XAI_API_KEY is required for Grok models.")
            return ChatOpenAI(
                model=self.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=api_key,
                base_url="https://api.x.ai/v1",
            )

        if self.provider == "anthropic":
            if ChatAnthropic is None:
                raise RuntimeError(
                    "Install `langchain-anthropic` to use Claude models."
                )
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is required for Claude models.")
            return ChatAnthropic(
                model=self.model,
                temperature=self.config.temperature,
                max_tokens_to_sample=self.config.max_tokens,
                api_key=api_key,
            )

        if ChatOpenAI is None:
            raise RuntimeError("Install `langchain-openai` to use OpenAI models.")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI-compatible models.")
        return ChatOpenAI(
            model=self.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=api_key,
        )

    def chat(self, messages: List[Dict[str, str]], response_format_json: bool = False) -> str:
        """Send chat messages and return the assistant response text."""
        payload = self._convert_messages(messages, response_format_json)
        backoff = 1.0
        for attempt in range(7):
            try:
                response = self._invoke(payload, response_format_json)
                return self._extract_text(response)
            except Exception as exc:  # pragma: no cover - network / SDK errors
                if attempt == 6:
                    raise
                eprint(f"⚠️  Request failed: {exc}. Retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff = min(backoff * 2, 16.0)
        return ""

    def _invoke(self, payload: Iterable[Any], response_format_json: bool):
        call_kwargs: Dict[str, Any] = {}
        if response_format_json and self.provider in {"openai", "grok"}:
            call_kwargs["response_format"] = {"type": "json_object"}
        return self.client.invoke(payload, **call_kwargs)

    def _convert_messages(
        self, messages: List[Dict[str, str]], response_format_json: bool
    ) -> List[Any]:
        if SystemMessage is None or HumanMessage is None or AIMessage is None:
            raise RuntimeError("Install `langchain` to build LangChain message objects.")
        converted: List[Any] = []
        appended_json_instruction = False
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if response_format_json and role == "user" and self.provider in {"gemini", "anthropic"}:
                content = f"{content}\n\nIMPORTANT: Return valid JSON only, no other text."
                appended_json_instruction = True
            if role == "system":
                converted.append(SystemMessage(content=content))
            elif role == "assistant":
                converted.append(AIMessage(content=content))
            else:
                converted.append(HumanMessage(content=content))

        if (
            response_format_json
            and self.provider in {"gemini", "anthropic"}
            and not appended_json_instruction
            and converted
        ):
            last = converted[-1]
            if hasattr(last, "content"):
                last.content = f"{last.content}\n\nIMPORTANT: Return valid JSON only, no other text."

        return converted

    def _extract_text(self, response: Any) -> str:
        if BaseMessage is not None and isinstance(response, BaseMessage):
            return getattr(response, "content", "") or ""
        if isinstance(response, dict):
            return str(response)
        return str(response)


def build_messages(system: str | None, user: str) -> List[Dict[str, str]]:
    convo: List[Dict[str, str]] = []
    if system:
        convo.append({"role": "system", "content": system})
    convo.append({"role": "user", "content": user})
    return convo


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LangChain-based multi-provider chat client",
    )
    parser.add_argument("--model", required=True, help="Model name to use")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--thinking-budget", type=int, default=0)
    parser.add_argument("--system", help="Optional system prompt")
    parser.add_argument("--user", help="User message. If omitted, read stdin")
    parser.add_argument("--user-file", help="Read user message from file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Request JSON-formatted response when provider supports it",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def resolve_user_message(args: argparse.Namespace) -> str:
    if args.user_file:
        try:
            with open(args.user_file, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except OSError as exc:
            raise RuntimeError(f"Failed to read user file {args.user_file}: {exc}")
    if args.user is not None:
        return args.user
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise RuntimeError("User message is required via --user, --user-file, or stdin")


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    user_content = resolve_user_message(args)

    config = LangChainLLMConfig(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        thinking_budget=args.thinking_budget,
    )

    client = LangChainLLMClient(config)
    messages = build_messages(args.system, user_content)
    response = client.chat(messages, response_format_json=args.json)
    print(response)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    try:
        raise SystemExit(main())
    except Exception as exc:
        eprint(f"❌  {exc}")
        raise SystemExit(1)
