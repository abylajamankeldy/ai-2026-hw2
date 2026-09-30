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

load_dotenv(ROOT / ".env")

# Provider. The assignment's model is OpenAI gpt-5.6-luna. If only a GEMINI_API_KEY
# is set (free tier, no card), the same code talks to Google's OpenAI-compatible
# endpoint instead - the program sends exactly the same messages either way.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
if os.environ.get("OPENAI_API_KEY", "").startswith("sk-") and os.environ["OPENAI_API_KEY"] != "sk-...":
    PROVIDER = "openai"
    MODEL = os.environ.get("HW2_MODEL", "gpt-5.6-luna")
    MIN_INTERVAL = float(os.environ.get("HW2_MIN_INTERVAL", "0"))
elif os.environ.get("GEMINI_API_KEY"):
    PROVIDER = "gemini"
    MODEL = os.environ.get("HW2_MODEL", "gemini-3.8-flash")
    # free tier allows ~10-15 requests per minute: space the calls out
    MIN_INTERVAL = float(os.environ.get("HW2_MIN_INTERVAL", "6.5"))
else:
    PROVIDER = None
    MODEL = os.environ.get("HW2_MODEL", "gpt-5.6-luna")
    MIN_INTERVAL = 0.0

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
        from openai import OpenAI

        if PROVIDER == "openai":
            _client = OpenAI()
        elif PROVIDER == "gemini":
            _client = OpenAI(api_key=os.environ["GEMINI_API_KEY"], base_url=GEMINI_BASE_URL)
        else:
            sys.exit("No API key. Put OPENAI_API_KEY=sk-... or GEMINI_API_KEY=... in .env (see .env.example).")
        print(f"[provider: {PROVIDER}, model: {MODEL}]", flush=True)
    return _client


_last_call = 0.0


def _throttle() -> None:
    global _last_call
    wait = MIN_INTERVAL - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


# Parameters that some models reject. If the API says a parameter is unsupported
# we drop it and retry once, and remember not to send it again.
_dropped: set[str] = set()


def chat(messages: list[dict], *, json_mode: bool = True, max_tokens: int = 4000) -> dict:
    """One stateless call. Returns {"text", "prompt_tokens", "completion_tokens", "total_tokens"}.

    prompt_tokens is what the API says we SENT - the number Sublab Medium tables use.
    """
    kwargs: dict[str, Any] = {"model": MODEL, "messages": messages}
    optional = {
        ("max_tokens" if PROVIDER == "gemini" else "max_completion_tokens"): max_tokens,
        "reasoning_effort": "low",
    }
    if json_mode:
        optional["response_format"] = {"type": "json_object"}
    for k, v in optional.items():
        if k not in _dropped:
            kwargs[k] = v

    from openai import BadRequestError, APIConnectionError, RateLimitError, APITimeoutError

    for attempt in range(8):
        _throttle()
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
        except RateLimitError as e:
            if "quota" in str(e).lower() and "day" in str(e).lower():
                sys.exit(f"Daily quota exhausted: {e}")
            print(f"  (rate limited, waiting {15 * (attempt + 1)}s)", flush=True)
            time.sleep(15 * (attempt + 1))
        except (APIConnectionError, APITimeoutError):
            time.sleep(3 * (attempt + 1))
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


if __name__ == "__main__":
    # python -m common.llm         -> one test call
    # python -m common.llm models  -> list the models your key can use
    if sys.argv[1:] == ["models"]:
        for m in client().models.list():
            print(m.id)
    else:
        r = chat([{"role": "user", "content": 'Reply with {"ok": true} and nothing else.'}])
        print(r)
