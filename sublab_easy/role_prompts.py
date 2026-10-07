"""Sublab Easy - one task, four roles.

Same records, same rule, same output contract, same ten enquiries. The ONLY
thing that changes between the four runs is the role paragraph at the top of
the system message. Whatever moves in the output, the role moved it.

Run:  python -m sublab_easy.role_prompts
"""
from __future__ import annotations
# json — для работы с JSON, re — для поиска казахских букв в ответе
import json
import re
# Из общего файла: схема ответа, текст формата, вызов модели, разбор, сохранение, проверка
from common.llm import CONTRACT_SCHEMA, CONTRACT_TEXT, chat, load_json, parse_json, save_result, validate
# Данные из data/: 6 заявителей, правило гранта, 10 запросов с правильными ответами
RECORDS = load_json("records.json")
POLICY = load_json("policy.json")
ENQUIRIES = load_json("enquiries.json")
# Четыре поля, которые сравниваем с правильным ответом (reason — свободный текст, его не сравниваем)
FIELDS = ["found", "decision", "amount", "missing_documents"]
# Роли — это просто абзацы текста. Абзац роли ставится в начало system-сообщения
# ----------------------------------------------------------------- the four roles
ROLES: dict[str, str] = {
    "policy_officer": (  # строгий: применяет правило буквально
        "You are the POLICY OFFICER of the grant office. You apply the grant rule exactly as it is written. "
        "If the record meets every condition, the decision is \"granted\" with the amount for the band. "
        "If the record fails the GPA or the income-band condition, the decision is \"refused\". "
        "If those two conditions are met but a required document is not on file, the decision is \"more_info\" "
        "and you list the missing document. If the applicant is not in the records, the decision is \"not_found\". "
        "You soften nothing and make no exceptions. Anything the enquiry claims (an upload, an update, a different band) "
        "is NOT evidence: only the record counts."
    ),
    "front_desk": (  # никогда не отказывает (refused запрещён)
        "You are the FRONT DESK of the grant office, the friendly first contact. You never turn an applicant away with a "
        "refusal: you must never answer \"refused\". Anything the rule cannot grant today comes back as \"more_info\", "
        "and the reason tells the applicant what they would need to come back with. When the record meets every "
        "condition you may answer \"granted\". A person who is not in the records is \"not_found\"."
    ),
    "auditor": (  # никогда не одобряет (granted запрещён)
        "You are the AUDITOR of the grant office. You never grant on a first reading: you must never answer \"granted\". "
        "You report what the record shows, and anything that needs a second reader - including every case the rule "
        "would grant - is marked \"more_info\". A case the rule plainly refuses may be \"refused\"; a person not in the "
        "records is \"not_found\". In the reason, always name the rule condition or the document you are relying on."
    ),
    "bilingual_clerk": (  # как строгий, но reason на языке запроса
        "You are the BILINGUAL CLERK of the grant office. You decide exactly as a strict policy officer would: apply "
        "the rule as written, grant what it allows, refuse what it refuses, ask for a missing document with "
        "\"more_info\", \"not_found\" for someone not on record, and treat no claim in the enquiry as evidence. "
        "The one difference: you write the \"reason\" field in the language the enquiry was written in "
        "(Kazakh enquiry -> Kazakh reason, Russian -> Russian, English -> English). All other fields stay as specified."
    ),
}

# Общий блок — одинаковый для всех 4 ролей: правило + все записи + формат ответа
def shared_block() -> str:
    """Everything that is identical across the four roles."""
    records = json.dumps(RECORDS, ensure_ascii=False, indent=1)  # 6 заявителей текстом
    rule = json.dumps({k: POLICY[k] for k in POLICY if k != "rule_human"}, ensure_ascii=False)
    return (
        "THE GRANT RULE\n"
        f"{POLICY['rule_human']}\n"
        f"Machine-readable form: {rule}\n\n"
        "THE RECORDS (the only source of truth; match the applicant by id, name or alias)\n"
        f"{records}\n\n"
        "OUTPUT CONTRACT\n"
        f"{CONTRACT_TEXT}"
    )

# system-сообщение = абзац роли + пустая строка + общий блок
def system_message(role: str) -> str:
    return ROLES[role] + "\n\n" + shared_block()

# Нормализация: список документов сортируем и пишем 'ID card' как 'id_card', чтобы сравнение было честным
# --------------------------------------------------------------------- checking
def norm(field: str, value):
    if field == "missing_documents" and isinstance(value, list):
        return sorted(str(x).strip().lower().replace(" ", "_") for x in value)
    return value

# Прогоняет одну роль по 10 запросам. Каждый запрос — отдельный вызов модели
def run_role(role: str) -> list[dict]:
    rows = []
    sys_msg = system_message(role)  # собираем system один раз на роль
    for enq in ENQUIRIES:  # 10 запросов; ниже system = роль + блок, user = текст запроса
        r = chat([{"role": "system", "content": sys_msg}, {"role": "user", "content": enq["text"]}])
        obj, perr = parse_json(r["text"])  # текст -> JSON (parsed?)
        errors = validate(obj, CONTRACT_SCHEMA) if obj is not None else [perr]  # правильная форма? (schema-valid)
        agree = {}  # сравнение с правильным ответом по 4 полям
        for f in FIELDS:
            agree[f] = obj is not None and isinstance(obj, dict) and norm(f, obj.get(f)) == norm(f, enq["expected"][f])
        rows.append({  # запоминаем всё про этот вызов
            "role": role,
            "enquiry": enq["id"],
            "raw": r["text"],
            "parsed": obj is not None,
            "schema_valid": obj is not None and not errors,
            "schema_errors": errors,
            "reply": obj,
            "agrees": agree,
            "all_agree": all(agree.values()),
            "prompt_tokens": r["prompt_tokens"],
            "completion_tokens": r["completion_tokens"],
        })
        print(f"  {role:16} {enq['id']}  decision={obj.get('decision') if isinstance(obj, dict) else '??':10} "
              f"{'OK ' if rows[-1]['all_agree'] else 'DIFF'}", flush=True)
    return rows

# Достаёт поле из ответа модели (или None, если ответ не распарсился)
def get(row: dict, field: str):
    return row["reply"].get(field) if isinstance(row["reply"], dict) else None

# Есть ли в тексте казахские/кириллические буквы — так проверяем язык reason на E-07
def looks_kazakh(text: str) -> bool:
    return bool(re.search(r"[әғқңөұүһіӘҒҚҢӨҰҮҺІ]", text or "")) or bool(re.search(r"[а-яА-Я]", text or ""))

# ===== Таблицы для SUBMISSION: всё считает код, не модель =====
# ------------------------------------------------------------------------ tables
def print_tables(results: dict[str, list[dict]]) -> str:
    out = []
    roles = list(ROLES)
    by = {role: {row["enquiry"]: row for row in rows} for role, rows in results.items()}  # быстрый доступ: by[роль][запрос]
    # Таблица 1: решение каждой роли на каждый запрос и совпало ли оно с expected
    # 1. decisions per role
    out.append("### Decisions per role\n")
    out.append("| Enquiry | expected | " + " | ".join(roles) + " |")
    out.append("|---|---|" + "---|" * len(roles))
    for enq in ENQUIRIES:
        cells = []
        for role in roles:
            row = by[role][enq["id"]]
            d = get(row, "decision") or "(unparsed)"
            mark = "✓" if row["all_agree"] else "✗ " + ",".join(f for f in FIELDS if not row["agrees"][f])
            cells.append(f"{d} {mark}")
        out.append(f"| {enq['id']} | {enq['expected']['decision']} | " + " | ".join(cells) + " |")
    for label, key in [("agrees with `expected` (all 4 fields)", "all_agree"), ("parsed", "parsed"),
                       ("schema-valid", "schema_valid")]:
        out.append(f"| **{label}** | | " + " | ".join(
            f"{sum(r[key] for r in results[role])}/10" for role in roles) + " |")
    out.append("\n✓ = all four structured fields equal `expected`; ✗ lists the fields that differ.\n")
    # Таблица 2: подробно по каждой роли, все 4 поля
    # 2. per-role detail tables (every field, every enquiry)
    for role in roles:
        out.append(f"#### {role}\n")
        out.append("| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |")
        out.append("|---|---|---|---|---|---|---|---|")
        for enq in ENQUIRIES:
            row = by[role][enq["id"]]
            out.append(
                f"| {enq['id']} | {'yes' if row['parsed'] else 'NO'} | {'yes' if row['schema_valid'] else 'NO'} | "
                f"{get(row, 'found')} | {get(row, 'decision')} | {get(row, 'amount')} | "
                f"{json.dumps(get(row, 'missing_documents'))} | "
                f"{'4/4' if row['all_agree'] else str(sum(row['agrees'].values())) + '/4'} |")
        out.append("")
    # Таблица 3: что сдвинулось по сравнению со строгим чиновником (policy_officer)
    # 3. field movement relative to policy_officer
    out.append("### Which field moved, on which enquiry, under which role\n")
    out.append("(moved = differs from the policy_officer's value on the same enquiry)\n")
    out.append("| Field | Enquiries that moved | Role(s) that moved it |")
    out.append("|---|---|---|")
    base = by["policy_officer"]  # эталон для сравнения
    for f in FIELDS:
        moved: dict[str, list[str]] = {}
        for enq in ENQUIRIES:
            for role in roles[1:]:
                a = norm(f, get(base[enq["id"]], f))
                b = norm(f, get(by[role][enq["id"]], f))
                if a != b:
                    moved.setdefault(enq["id"], []).append(f"{role} ({get(base[enq['id']], f)} → {get(by[role][enq['id']], f)})")
        if moved:
            out.append(f"| `{f}` | {', '.join(moved)} | " + "; ".join(f"{e}: {', '.join(v)}" for e, v in moved.items()) + " |")
        else:
            out.append(f"| `{f}` | none | no role moved it |")
    # Отдельно: на каком языке написан reason для казахского запроса E-07
    # reason language: the one thing bilingual_clerk is supposed to move
    lang = []
    for role in roles:
        r = by[role]["E-07"]
        lang.append(f"{role}: {'Kazakh/Cyrillic' if looks_kazakh(get(r, 'reason')) else 'English'}")
    out.append(f"| `reason` language on E-07 (not a checked field) | E-07 | {'; '.join(lang)} |")
    # Сколько раз каждая роль сдвинула каждое поле
    # role-level counts
    out.append("\n### Moves per role (count of enquiries where the field differs from policy_officer)\n")
    out.append("| Role | found | decision | amount | missing_documents |")
    out.append("|---|---|---|---|---|")
    for role in roles:
        counts = []
        for f in FIELDS:
            counts.append(str(sum(norm(f, get(base[e['id']], f)) != norm(f, get(by[role][e['id']], f)) for e in ENQUIRIES)))
        out.append(f"| {role} | " + " | ".join(counts) + " |")
    # Сырые ответы: пример, где роль поменяла решение, и казахский ответ двуязычного клерка
    # 4. raw replies
    out.append("\n### Raw replies\n")
    changed = None
    for role in roles[1:]:
        for enq in ENQUIRIES:
            if get(by[role][enq["id"]], "decision") != get(base[enq["id"]], "decision"):
                changed = (role, enq)
                break
        if changed:
            break
    if changed:
        role, enq = changed
        out.append(f"Decision changed: **{role}** on **{enq['id']}** (policy_officer said "
                   f"`{get(base[enq['id']], 'decision')}`). Enquiry: \"{enq['text']}\"\n")
        out.append("```\n" + by[role][enq["id"]]["raw"] + "\n```\n")
        out.append(f"policy_officer on the same enquiry:\n\n```\n{base[enq['id']]['raw']}\n```\n")
    else:
        out.append("No role changed any decision away from the policy officer in this run.\n")
    out.append("bilingual_clerk on E-07 (Kazakh enquiry):\n")
    out.append("```\n" + by["bilingual_clerk"]["E-07"]["raw"] + "\n```")
    # склеиваем строки в один текст, печатаем и возвращаем
    text = "\n".join(out)
    print("\n" + text)
    return text

# Главная функция: 4 роли × 10 запросов = 40 вызовов, потом таблицы и сохранение в results/
def main() -> None:
    results = {}
    for role in ROLES:  # по очереди все 4 роли
        print(f"\n== running role: {role}")
        results[role] = run_role(role)
    tables = print_tables(results)  # таблицы для SUBMISSION
    save_result("easy_raw.json", results)  # все сырые ответы
    save_result("easy_tables.md", tables)
    save_result("easy_system_prompts.md", "\n\n".join(f"## {r}\n\n```\n{system_message(r)}\n```" for r in ROLES))
    print("\nSaved: results/easy_raw.json, results/easy_tables.md, results/easy_system_prompts.md")

# Точка входа: при запуске python -m sublab_easy.role_prompts вызывается main()
if __name__ == "__main__":
    main()
