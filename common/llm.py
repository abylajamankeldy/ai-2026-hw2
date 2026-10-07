"""Shared plumbing for all three sublabs: one model, one call helper, JSON parsing,
the answer contract, and a place to save results.

Nothing in here is specific to a sublab. The interesting decisions (prompts,
state, rules) live in the sublab files themselves.
"""
from __future__ import annotations
# Импорты: стандартные библиотеки Python + dotenv для чтения файла .env
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
# load_dotenv читает файл .env, где лежит ключ API
from dotenv import load_dotenv
# Пути: корень проекта, папка с данными и папка, куда сохраняем результаты
ROOT = Path(__file__).resolve().parent.parent  # папка ai-2026-hw2
DATA = ROOT / "data"  # data/ — данные от агая
RESULTS = ROOT / "results"  # results/ — сюда код пишет таблицы и ответы
# Кладём ключ из .env в переменные окружения (сам ключ в коде не хранится)
load_dotenv(ROOT / ".env")
# Выбор провайдера: берём первый, для которого в .env есть ключ (у нас это Groq)
# Provider. The assignment's model is OpenAI gpt-5.6-luna. Without an OpenAI key
# the same code can talk to a free OpenAI-compatible endpoint instead - the
# program sends exactly the same messages either way; only the model differs.
# The first key found in .env wins, in this order:
#   name       env var             base url                                            default model          pause between calls
PROVIDERS = [
    ("openai",  "OPENAI_API_KEY",  None,                                               "gpt-5.6-luna",        0.0),
    ("groq",    "GROQ_API_KEY",    "https://api.groq.com/openai/v1",                   "openai/gpt-oss-120b", 2.5),
    ("gemini",  "GEMINI_API_KEY",  "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.8-flash", 6.5),
]
PROVIDER, API_KEY, BASE_URL, MODEL, MIN_INTERVAL = None, None, None, "gpt-5.6-luna", 0.0
for _name, _env, _url, _model, _pause in PROVIDERS:  # идём по списку сверху вниз
    _key = os.environ.get(_env, "").strip()
    if _key and _key not in ("sk-...", "..."):  # ключ есть и это не заглушка
        PROVIDER, API_KEY, BASE_URL, MODEL, MIN_INTERVAL = _name, _key, _url, _model, _pause
        break  # нашли — дальше не ищем
MODEL = os.environ.get("HW2_MODEL") or MODEL  # модель можно поменять через .env
MIN_INTERVAL = float(os.environ.get("HW2_MIN_INTERVAL", MIN_INTERVAL))  # пауза между вызовами, секунд
# Консоль Windows не умеет печатать казахские буквы — переключаем вывод на UTF-8
# Windows consoles default to cp1251/cp866 and would crash on Kazakh letters and ✓/→.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ===== Чтение и сохранение файлов =====
# --------------------------------------------------------------------------- data
def load_json(name: str) -> Any:  # читает JSON-файл из data/
    return json.loads((DATA / name).read_text(encoding="utf-8"))

# Сохраняет результат в results/: строку как текст, всё остальное как JSON
def save_result(name: str, obj: Any) -> Path:
    RESULTS.mkdir(exist_ok=True)  # создать папку, если её нет
    path = RESULTS / name
    if isinstance(obj, str):
        path.write_text(obj, encoding="utf-8")
    else:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

# ===== Контракт: единая форма ответа из 6 полей =====
# ----------------------------------------------------------------------- contract
# The fixed shape every grant-office answer must take (README, section 2).
CONTRACT_SCHEMA = {  # JSON Schema: по ней validate() проверяет форму ответа
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
    "additionalProperties": False,  # лишние поля запрещены
}
# Тот же формат словами: этот текст вставляется в промпт, чтобы модель знала, что писать
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

# ===== Клиент API =====
# --------------------------------------------------------------------- the client
_client = None  # создаётся один раз, при первом вызове

# Возвращает объект для запросов к модели (библиотека openai, адрес — Groq или OpenAI)
def client():
    global _client
    if _client is None:
        from openai import OpenAI
        # нет ключа — сразу выходим с понятной ошибкой
        if PROVIDER is None:
            sys.exit("No API key in .env. Set one of: " + ", ".join(p[1] for p in PROVIDERS) + " (see .env.example).")
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)  # base_url = адрес Groq, формат запросов как у OpenAI
        print(f"[provider: {PROVIDER}, model: {MODEL}]", flush=True)
    return _client

# ===== Пауза между запросами (лимит бесплатного Groq) =====
_last_call = 0.0  # время последнего вызова

# Ждём, пока с прошлого вызова не пройдёт MIN_INTERVAL секунд
def _throttle() -> None:
    global _last_call
    wait = MIN_INTERVAL - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()

# ===== Главная функция: один вызов модели =====
# Parameters that some models reject. If the API says a parameter is unsupported
# we drop it and retry once, and remember not to send it again.
_dropped: set[str] = set()

# chat() — единственное место, где программа говорит с моделью. Её вызывают все три саба
def chat(messages: list[dict], *, json_mode: bool = True, max_tokens: int = 4000) -> dict:
    """One stateless call. Returns {"text", "prompt_tokens", "completion_tokens", "total_tokens"}.

    prompt_tokens is what the API says we SENT - the number Sublab Medium tables use.
    """
    kwargs: dict[str, Any] = {"model": MODEL, "messages": messages}  # что отправим на сервер
    optional = {
        ("max_completion_tokens" if PROVIDER == "openai" else "max_tokens"): max_tokens,
    }
    if PROVIDER == "openai":
        optional["reasoning_effort"] = "low"
    if json_mode:  # просим сервер вернуть строго JSON
        optional["response_format"] = {"type": "json_object"}
    for k, v in optional.items():
        if k not in _dropped:
            kwargs[k] = v
    # типы ошибок библиотеки openai — каждую обрабатываем по-своему
    from openai import BadRequestError, APIConnectionError, RateLimitError, APITimeoutError
    # до 8 попыток: при ошибке ждём и пробуем снова
    for attempt in range(8):
        _throttle()  # пауза перед запросом
        try:
            resp = client().chat.completions.create(**kwargs)  # ВОТ ЗДЕСЬ запрос уходит на сервер
            break  # успех — выходим из цикла
        except BadRequestError as e:  # сервер не знает какой-то параметр
            msg = str(e)
            bad = [k for k in list(kwargs) if k in optional and k in msg]
            if not bad:
                raise
            for k in bad:
                _dropped.add(k)  # запоминаем и больше не отправляем
                kwargs.pop(k, None)
        except RateLimitError as e:  # слишком много запросов
            if "quota" in str(e).lower() and "day" in str(e).lower():
                sys.exit(f"Daily quota exhausted: {e}")
            print(f"  (rate limited, waiting {15 * (attempt + 1)}s)", flush=True)
            time.sleep(15 * (attempt + 1))  # ждём 15, 30, 45... секунд
        except (APIConnectionError, APITimeoutError):  # нет связи или таймаут
            time.sleep(3 * (attempt + 1))
    else:  # все 8 попыток провалились
        raise RuntimeError("model call failed after retries")
    # защита: при неправильном адресе или модели сервер может вернуть не то
    if isinstance(resp, str) or not getattr(resp, "choices", None):
        sys.exit(f"The API at {BASE_URL or 'api.openai.com'} returned something that is not a chat completion "
                 f"(wrong endpoint or model?): {str(resp)[:300]}")
    u = resp.usage  # сколько токенов посчитал сервер
    return {
        "text": resp.choices[0].message.content or "",  # текст ответа модели
        "prompt_tokens": getattr(u, "prompt_tokens", None),  # сколько токенов МЫ отправили
        "completion_tokens": getattr(u, "completion_tokens", None),
        "total_tokens": getattr(u, "total_tokens", None),
    }

# ===== Разбор ответа модели =====
# ------------------------------------------------------------------------ parsing
def parse_json(text: str) -> tuple[Any | None, str | None]:
    """Parse a reply as JSON. Tolerates ```json fences, nothing more.
    Returns (object, None) or (None, error message)."""
    t = text.strip()  # убираем пробелы по краям
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    if m:  # ответ обёрнут в ```json ... ``` — снимаем обёртку
        t = m.group(1)
    try:
        return json.loads(t), None  # текст -> объект Python
    except json.JSONDecodeError as e:  # это не JSON
        return None, f"not JSON: {e}"

# Проверка формы по JSON Schema: возвращает список ошибок, пустой список = всё хорошо
def validate(obj: Any, schema: dict) -> list[str]:
    """Return a list of schema errors ([] means valid)."""
    from jsonschema import Draft202012Validator
    # каждую ошибку превращаем в короткую строку
    v = Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in v.iter_errors(obj)]

# Примерный подсчёт токенов (нужен, только если сервер не прислал usage)
def count_tokens(text: str) -> int:
    """Local estimate with tiktoken (used only where the API gives no usage)."""
    try:
        import tiktoken

        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except Exception:
        return len(text) // 4

# Запуск файла напрямую: python -m common.llm — проверка, что ключ работает
if __name__ == "__main__":
    # python -m common.llm         -> one test call
    # python -m common.llm models  -> list the models your key can use
    if sys.argv[1:] == ["models"]:
        for m in client().models.list():
            print(m.id)
    else:
        r = chat([{"role": "user", "content": 'Reply with {"ok": true} and nothing else.'}])
        print(r)
