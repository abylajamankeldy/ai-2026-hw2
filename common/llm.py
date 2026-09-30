"""Shared plumbing for all three sublabs: one model, one call helper, JSON parsing,
the answer contract, and a place to save results.

Nothing in here is specific to a sublab. The interesting decisions (prompts,
state, rules) live in the sublab files themselves.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"

MODEL = os.environ.get("HW2_MODEL", "gpt-5.6-luna")

load_dotenv(ROOT / ".env")

# Windows consoles default to cp1251/cp866 and would crash on Kazakh letters and ✓/→.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


# --------------------------------------------------------------------------- data
def load_json(name: str) -> Any:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save_result(name: str, obj: Any) -> Path:
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / name
    if isinstance(obj, str):
        path.write_text(obj, encoding="utf-8")
    else:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


# ----------------------------------------------------------------------- contract
# The fixed shape every grant-office answer must take (README, section 2).
CONTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "applicant_id": {"type": ["string", "null"]},
        "found": {"type": "boolean"},
        "decision": {"enum": ["granted", "refused", "more_info", "not_found"]},
        "amount": {"type": "integer", "minimum": 0},
        "missing_documents": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["applicant_id", "found", "decision", "amount", "missing_documents", "reason"],
    "additionalProperties": False,
}

CONTRACT_TEXT = """Reply with ONE JSON object and nothing else - no prose before or after it, no markdown fences.
It must have exactly these six keys:
{
  "applicant_id": string or null   - the record id, e.g. "A-201"; if the person is not on the record, the id they gave (or null if they gave none),
  "found": true | false            - whether the applicant exists in the records,
  "decision": "granted" | "refused" | "more_info" | "not_found",
  "amount": integer                - tenge granted; 0 unless decision is "granted",
  "missing_documents": [strings]   - required documents NOT on file, using the record's names ("transcript", "id_card"); [] if none,
  "reason": string                 - one or two sentences for a human
}"""


# --------------------------------------------------------------------- the client
_client = None


def client():
    global _client
    if _client is None:
        if not os.environ.get("OPENAI_API_KEY"):
            sys.exit("OPENAI_API_KEY is not set. Copy .env.example to .env and put your key in it.")
        from openai import OpenAI

        _client = OpenAI()
    return _client


# Parameters that some models reject. If the API says a parameter is unsupported
# we drop it and retry once, and remember not to send it again.
_dropped: set[str] = set()


def chat(messages: list[dict], *, json_mode: bool = True, max_tokens: int = 4000) -> dict:
    """One stateless call. Returns {"text", "prompt_tokens", "completion_tokens", "total_tokens"}.

    prompt_tokens is what the API says we SENT - the number Sublab Medium tables use.
    """
    kwargs: dict[str, Any] = {"model": MODEL, "messages": messages}
    optional = {
        "max_completion_tokens": max_tokens,
        "reasoning_effort": "low",
    }
    if json_mode:
        optional["response_format"] = {"type": "json_object"}
    for k, v in optional.items():
        if k not in _dropped:
            kwargs[k] = v

    from openai import BadRequestError, APIConnectionError, RateLimitError, APITimeoutError

    for attempt in range(6):
        try:
            resp = client().chat.completions.create(**kwargs)
            break
        except BadRequestError as e:
            msg = str(e)
            bad = [k for k in list(kwargs) if k in optional and k in msg]
            if not bad:
                raise
            for k in bad:
                _dropped.add(k)
                kwargs.pop(k, None)
        except (APIConnectionError, RateLimitError, APITimeoutError):
            time.sleep(2 * (attempt + 1))
    else:
        raise RuntimeError("model call failed after retries")

    u = resp.usage
    return {
        "text": resp.choices[0].message.content or "",
        "prompt_tokens": getattr(u, "prompt_tokens", None),
        "completion_tokens": getattr(u, "completion_tokens", None),
        "total_tokens": getattr(u, "total_tokens", None),
    }


# ------------------------------------------------------------------------ parsing
def parse_json(text: str) -> tuple[Any | None, str | None]:
    """Parse a reply as JSON. Tolerates ```json fences, nothing more.
    Returns (object, None) or (None, error message)."""
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    if m:
        t = m.group(1)
    try:
        return json.loads(t), None
    except json.JSONDecodeError as e:
        return None, f"not JSON: {e}"


def validate(obj: Any, schema: dict) -> list[str]:
    """Return a list of schema errors ([] means valid)."""
    from jsonschema import Draft202012Validator

    v = Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in v.iter_errors(obj)]


def count_tokens(text: str) -> int:
    """Local estimate with tiktoken (used only where the API gives no usage)."""
    try:
        import tiktoken

        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4
