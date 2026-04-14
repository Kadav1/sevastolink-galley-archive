"""
LM Studio HTTP client.

Wraps the OpenAI-compatible LM Studio API.  All errors are captured and
returned as (None, LMStudioError) tuples so callers never have to guard
against unexpected exceptions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx


# ── Error model ───────────────────────────────────────────────────────────────

class LMStudioErrorKind(str, Enum):
    unavailable = "unavailable"      # connect / DNS failure
    timeout = "timeout"              # request exceeded timeout
    http_error = "http_error"        # non-2xx HTTP response
    parse_error = "parse_error"      # response body is not valid JSON / unexpected shape
    no_content = "no_content"        # model returned empty / whitespace content


@dataclass(frozen=True)
class LMStudioError:
    kind: LMStudioErrorKind
    message: str

    def __str__(self) -> str:
        return f"LMStudioError({self.kind.value}): {self.message}"


# ── Client ────────────────────────────────────────────────────────────────────

# Reasonable defaults for a local model that may be slow to start generating.
# Keep the read timeout generous enough for larger local instruct models.
_DEFAULT_CONNECT_TIMEOUT = 5.0    # seconds — fast fail if LM Studio is off
_DEFAULT_READ_TIMEOUT = 240.0     # seconds — tolerate cold starts / slower local inference


class LMStudioClient:
    """Thin HTTP client for the LM Studio OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str,
        connect_timeout: float = _DEFAULT_CONNECT_TIMEOUT,
        read_timeout: float = _DEFAULT_READ_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=10.0,
                pool=5.0,
            )
        )

    # ── Availability check ────────────────────────────────────────────────────

    def check_availability(self) -> tuple[bool, LMStudioError | None]:
        """
        GET /models — returns (True, None) if LM Studio is reachable,
        or (False, LMStudioError) on any failure.
        """
        try:
            response = self._client.get(f"{self._base_url}/models")
            response.raise_for_status()
            return True, None
        except httpx.ConnectError as exc:
            return False, LMStudioError(LMStudioErrorKind.unavailable, str(exc))
        except httpx.TimeoutException as exc:
            return False, LMStudioError(LMStudioErrorKind.timeout, str(exc))
        except httpx.HTTPStatusError as exc:
            return False, LMStudioError(
                LMStudioErrorKind.http_error,
                f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
            )

    # ── Chat completion ───────────────────────────────────────────────────────

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        response_format: dict[str, Any] | None = None,
    ) -> tuple[str | None, LMStudioError | None]:
        """
        POST /chat/completions — returns (content_string, None) on success
        or (None, LMStudioError) on any failure.

        The caller is responsible for parsing the returned string as JSON.
        """
        payload: dict[str, Any] = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if model:
            payload["model"] = model
        if response_format is not None:
            payload["response_format"] = response_format

        try:
            response = self._client.post(
                f"{self._base_url}/chat/completions",
                content=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            return None, LMStudioError(LMStudioErrorKind.unavailable, str(exc))
        except httpx.TimeoutException as exc:
            return None, LMStudioError(LMStudioErrorKind.timeout, str(exc))
        except httpx.HTTPStatusError as exc:
            return None, LMStudioError(
                LMStudioErrorKind.http_error,
                f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
            )

        # Parse response body
        try:
            body = response.json()
            message = body["choices"][0]["message"]
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                content = message.get("reasoning_content")
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            return None, LMStudioError(
                LMStudioErrorKind.parse_error,
                f"Unexpected response shape: {exc}",
            )

        if not content or not content.strip():
            return None, LMStudioError(
                LMStudioErrorKind.no_content,
                "Model returned empty content",
            )

        return content, None
