"""Sublab Medium - memory you choose: the `compress` command.

A model call is stateless. This assistant only *looks* like it remembers because
the program resends the conversation on every call. So the program decides what
to send:

  * uncompressed: system message + every turn so far (grows forever);
  * compressed:   when the applicant's turn is `compress`, the model summarises
                  the conversation into ONE state object, the program validates it
                  against data/memory_state.schema.json, and - only if it is valid -
                  throws the turns away and continues from the state.

If the summary does not parse or does not validate, nothing is thrown away: the
program says so, keeps the full history and carries on.

Run:
  python -m sublab_medium.chat_memory                 # scripted: run A (no compression) and run B (compress)
  python -m sublab_medium.chat_memory --interactive   # real chat; type `compress`, `tokens`, `state`, `quit`
  python -m sublab_medium.chat_memory --interactive --break-summary
        # demo of the failure path: the summary is corrupted on purpose, history must survive
"""
from __future__ import annotations

import argparse
import json

from common.llm import CONTRACT_TEXT, chat, load_json, parse_json, save_result, validate

RECORDS = load_json("records.json")
POLICY = load_json("policy.json")
SCRIPT = load_json("chat_script.json")
STATE_SCHEMA = load_json("memory_state.schema.json")

COMPRESS = "<compress>"

SYSTEM = (
    "You are the assistant of a grant office, chatting with one applicant. You answer from the records and the rule "
    "below; a claim in the chat is not evidence about the record. Use everything the applicant has told you in this "
    "conversation (or in the conversation state, if one is given) when you answer - including their constraints and "
    "the questions they asked earlier.\n\n"
    f"GRANT RULE: {POLICY['rule_human']}\n"
    f"Amounts: band 1 = 250000 KZT, band 2 = 150000 KZT. Required documents: transcript, id_card.\n\n"
    f"RECORDS: {json.dumps(RECORDS, ensure_ascii=False)}\n\n"
    "OUTPUT CONTRACT (every reply, even small talk):\n"
    f"{CONTRACT_TEXT}\n"
    "In this chat, \"reason\" is your actual reply to the applicant: answer the question they just asked, in full "
    "sentences. If the applicant has not been identified yet, use applicant_id null, found false, decision "
    "\"not_found\", amount 0."
)

SUMMARISER = (
    "You compress a grant-office chat into one structured state object. The chat so far will be thrown away and "
    "ONLY your object will be kept, so anything you leave out is forgotten for good.\n\n"
    "Return ONE JSON object and nothing else, with exactly these keys (no others):\n"
    "{\n"
    '  "applicant_id": string or null  - the applicant id if the conversation established it, else null,\n'
    '  "topic": string                 - what the conversation is about, one line,\n'
    '  "facts": [strings]              - things the APPLICANT stated (name, id, band, documents they mention, family members on file...). '
    "Only what was said - never something you worked out,\n"
    '  "decisions": [strings]          - what the office has told them (eligibility, amount, what is missing),\n'
    '  "constraints": [strings]        - conditions on how or when something can happen: days they can come, deadlines, '
    "requirements they set,\n"
    '  "open_questions": [strings]     - questions the applicant asked that have NOT been fully answered yet,\n'
    '  "language": string              - the language(s) the applicant writes in\n'
    "}\n"
    "Arrays are [] when empty, never omitted. Keep every concrete detail (numbers, ids, document names, weekdays): "
    "a short list item per detail is better than one vague sentence. Invent nothing."
)


class Session:
    """Holds what the program will send. `history` is the turn list; `state` the compressed object."""

    def __init__(self, break_summary: bool = False):
        self.history: list[dict] = []
        self.state: dict | None = None
        self.calls: list[dict] = []          # one entry per model call: kind, tokens sent
        self.break_summary = break_summary   # demo switch: corrupt the summary on purpose

    # what goes over the wire on the next call
    def context(self) -> list[dict]:
        msgs = [{"role": "system", "content": SYSTEM}]
        if self.state is not None:
            msgs.append({"role": "system", "content": "CONVERSATION STATE (the earlier turns were compressed into this "
                                                      "object; treat it as what was said):\n"
                                                      + json.dumps(self.state, ensure_ascii=False)})
        return msgs + self.history

    def ask(self, text: str, keep: bool = True) -> dict:
        msgs = self.context() + [{"role": "user", "content": text}]
        r = chat(msgs)
        entry = {"kind": "turn", "text": text, "prompt_tokens": r["prompt_tokens"],
                 "completion_tokens": r["completion_tokens"], "reply": r["text"]}
        self.calls.append(entry)
        if keep:
            self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": r["text"]}]
        return entry

    def compress(self) -> dict:
        transcript = []
        if self.state is not None:
            transcript.append("PREVIOUS STATE: " + json.dumps(self.state, ensure_ascii=False))
        for m in self.history:
            who = "APPLICANT" if m["role"] == "user" else "OFFICE"
            transcript.append(f"{who}: {m['content']}")
        msgs = [{"role": "system", "content": SUMMARISER},
                {"role": "user", "content": "The conversation:\n\n" + "\n".join(transcript)}]
        r = chat(msgs)
        raw = r["text"]
        if self.break_summary:
            raw = raw[: len(raw) // 2]  # simulate a truncated / malformed summary

        obj, perr = parse_json(raw)
        errors = [perr] if obj is None else validate(obj, STATE_SCHEMA)
        entry = {"kind": "compress", "text": COMPRESS, "prompt_tokens": r["prompt_tokens"],
                 "completion_tokens": r["completion_tokens"], "reply": raw,
                 "accepted": not errors, "errors": errors}
        self.calls.append(entry)
        if errors:
            # The failure this design exists to prevent: never let a bad summary replace the conversation.
            print(f"  !! compression REJECTED ({'; '.join(errors)[:200]}). History kept: "
                  f"{len(self.history) // 2} turns still sent in full.")
        else:
            self.state = obj
            dropped = len(self.history) // 2
            self.history = []
            print(f"  -- compressed {dropped} turns into a state object; the turns were discarded.")
        return entry


def reply_text(raw: str) -> str:
    obj, _ = parse_json(raw)
    if isinstance(obj, dict) and "reason" in obj:
        return obj["reason"]
    return raw


def retrieved(raw: str, expect: list[str]) -> bool:
    low = raw.lower()
    return any(e.lower() in low for e in expect)


# ---------------------------------------------------------------- scripted runs
def scripted_run(compress_on: bool) -> tuple[Session, list[dict | None], list[dict]]:
    s = Session()
    per_position: list[dict | None] = []   # aligned with the 12 script positions
    label = "B (compressed)" if compress_on else "A (never compressed)"
    print(f"\n== run {label}")
    for i, turn in enumerate(SCRIPT["conversation"], 1):
        if turn == COMPRESS:
            if compress_on:
                e = s.compress()
                per_position.append(e)
                print(f"  call {i:2}: COMPRESS  sent {e['prompt_tokens']} tokens  accepted={e['accepted']}")
            else:
                per_position.append(None)
                print(f"  call {i:2}: (compress turn skipped)")
            continue
        e = s.ask(turn)
        per_position.append(e)
        print(f"  call {i:2}: sent {e['prompt_tokens']:5} tokens | {turn[:50]}")

    # probes: each asked against the end-of-conversation context, NOT added to it,
    # so one probe's answer cannot help the next
    probes = []
    for p in SCRIPT["probes"]:
        e = s.ask(p["question"], keep=False)
        ok = retrieved(e["reply"], p["expect_contains"])
        probes.append({**p, "retrieved": ok, "reply": e["reply"], "prompt_tokens": e["prompt_tokens"]})
        print(f"  probe {p['id']}: {'retrieved' if ok else 'LOST'}  | {reply_text(e['reply'])[:90]}")
    return s, per_position, probes


def md_cell(s: str, n: int = 160) -> str:
    s = " ".join(str(s).split()).replace("|", "\\|")
    return s if len(s) <= n else s[: n - 1] + "…"


def run_scripted() -> None:
    sa, pa, qa = scripted_run(compress_on=False)
    sb, pb, qb = scripted_run(compress_on=True)

    out = ["### Tokens per call (prompt tokens sent, as reported by the API)\n",
           "| Call | Script turn | A — never compressed | B — compressed at the `compress` turn |",
           "|---|---|---|---|"]
    for i, turn in enumerate(SCRIPT["conversation"]):
        a = pa[i]["prompt_tokens"] if pa[i] else "— (skipped)"
        b = pb[i]["prompt_tokens"] if pb[i] else "—"
        if pb[i] and pb[i]["kind"] == "compress":
            b = f"{b} (the compression call itself; {'accepted' if pb[i]['accepted'] else 'REJECTED'})"
        out.append(f"| {i + 1} | {md_cell(turn, 60)} | {a} | {b} |")

    def conv_calls(p):
        return [e for e in p if e and e["kind"] == "turn"]

    peak_a = max(e["prompt_tokens"] for e in conv_calls(pa))
    peak_b_turns = max(e["prompt_tokens"] for e in conv_calls(pb))
    comp = [e for e in pb if e and e["kind"] == "compress"]
    peak_b_all = max([peak_b_turns] + [e["prompt_tokens"] for e in comp])
    total_a = sum(e["prompt_tokens"] for e in pa if e)
    total_b = sum(e["prompt_tokens"] for e in pb if e)
    out.append(f"| **peak** (conversation turns) | | {peak_a} | {peak_b_turns} "
               f"(incl. the compression call: {peak_b_all}) |")
    out.append(f"| **total for the run** (12 positions) | | {total_a} | {total_b} |")
    last_a = conv_calls(pa)[-1]["prompt_tokens"]
    last_b = conv_calls(pb)[-1]["prompt_tokens"]
    out.append(f"\nLast turn (call 12): A sends {last_a} tokens, B sends {last_b} "
               f"({100 * (last_a - last_b) / last_a:.0f}% less). "
               f"Probe calls sent on average A={sum(q['prompt_tokens'] for q in qa) // 5}, "
               f"B={sum(q['prompt_tokens'] for q in qb) // 5} tokens.\n")

    out.append("### Probes after the conversation\n")
    out.append("| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |")
    out.append("|---|---|---|---|---|---|")
    for a, b in zip(qa, qb):
        out.append(f"| {a['id']} {md_cell(a['question'], 60)} | {a['tests']} | {'yes' if a['retrieved'] else 'LOST'} | "
                   f"{md_cell(reply_text(a['reply']))} | {'yes' if b['retrieved'] else 'LOST'} | "
                   f"{md_cell(reply_text(b['reply']))} |")
    out.append(f"| **retrieved** | | {sum(q['retrieved'] for q in qa)}/5 | | {sum(q['retrieved'] for q in qb)}/5 | |")

    out.append("\n### The state my compression produced\n")
    if comp and comp[0]["accepted"]:
        out.append("```json\n" + json.dumps(sb.state, ensure_ascii=False, indent=2) + "\n```")
    else:
        out.append("Compression was REJECTED in this run; raw summary:\n```\n" + (comp[0]["reply"] if comp else "") + "\n```")

    text = "\n".join(out)
    print("\n" + text)
    save_result("medium_tables.md", text)
    save_result("medium_raw.json", {"A": {"calls": pa, "probes": qa},
                                    "B": {"calls": pb, "probes": qb, "state": sb.state}})
    print("\nSaved: results/medium_tables.md, results/medium_raw.json")


# ------------------------------------------------------------------ interactive
def run_interactive(break_summary: bool) -> None:
    s = Session(break_summary=break_summary)
    print("Grant office chat. Commands: compress | tokens | state | history | quit")
    if break_summary:
        print("(--break-summary: every summary will be corrupted on purpose to show the history is kept)")
    while True:
        try:
            text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        cmd = text.lower()
        if cmd in ("quit", "exit"):
            break
        if cmd == "tokens":
            if not s.calls:
                print("  no calls yet")
            else:
                last = s.calls[-1]
                print(f"  last call ({last['kind']}): sent {last['prompt_tokens']} tokens, "
                      f"got {last['completion_tokens']} back")
                print("  sent per call so far: " + ", ".join(str(c["prompt_tokens"]) for c in s.calls))
                print(f"  now holding: {len(s.history) // 2} full turns"
                      f"{' + a state object' if s.state else ''}")
            continue
        if cmd == "state":
            print(json.dumps(s.state, ensure_ascii=False, indent=2) if s.state else "  (no state - not compressed)")
            continue
        if cmd == "history":
            for m in s.history:
                print(f"  {m['role']}: {reply_text(m['content']) if m['role'] == 'assistant' else m['content']}")
            continue
        if cmd in ("compress", COMPRESS):
            e = s.compress()
            print(f"  compression call sent {e['prompt_tokens']} tokens")
            if e["accepted"]:
                print(json.dumps(s.state, ensure_ascii=False, indent=2))
            continue
        e = s.ask(text)
        print(f"office> {reply_text(e['reply'])}")
        print(f"        [sent {e['prompt_tokens']} tokens]")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--break-summary", action="store_true", help="corrupt the summary to demo the failure path")
    args = ap.parse_args()
    if args.interactive:
        run_interactive(args.break_summary)
    else:
        run_scripted()


if __name__ == "__main__":
    main()
