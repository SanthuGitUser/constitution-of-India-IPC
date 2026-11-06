"""Heuristic plain-language drafts from official legal text (for learning, not legal advice)."""
from __future__ import annotations

import re

EM_DASH = re.compile(r"\.[\s]*(?:—|\u2014|-)\s*")
ILLUSTRATIONS = re.compile(r"\bIllustrations?\b", re.I)
FOOTNOTES = re.compile(r"\s+\d+\.\s+(?:Subs\.|Ins\.|Added|The)\s", re.I)


def _normalize_space(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r" \.", ".", text)
    return text


def extract_operative(official: str) -> str:
    body = re.sub(r"^\d+[A-Z]?\.\s+", "", official.strip(), count=1)
    if re.match(r"^\[", body):
        return _normalize_space(body)

    m = EM_DASH.search(body)
    if m:
        body = body[m.end() :]
    else:
        # Preamble or heading-only lines
        if ".—" in body:
            body = body.split(".—", 1)[-1]

    body = ILLUSTRATIONS.split(body)[0]
    body = FOOTNOTES.split(body)[0]
    body = re.split(r"\s+\d+\[\d+[A-Z]?\.\s", body)[0]
    body = re.sub(r"\d+\[(.*?)\]", r" \1 ", body)
    body = re.sub(r"\[([^\]]+)\]", r" \1 ", body)
    return _normalize_space(body)


def simplify_phrasing(text: str) -> str:
    subs: list[tuple[str, str]] = [
        (r"\bWhoever commits murder\b", "If someone commits murder"),
        (r"\bWhoever\b", "If someone"),
        (r"\bNo person shall be deprived of his life or personal liberty except according to procedure established by law\b",
         "Nobody may be deprived of life or personal liberty except through procedure established by law"),
        (r"\bNo person shall\b", "Nobody may"),
        (r"\bshall be punished with death\b", "can be sentenced to death"),
        (r"\bshall be punished with\b", "can be punished with"),
        (r"\bimprisonment of either description for a term which may extend to\b", "jail for up to"),
        (r"\bfor a term which may extend to\b", "for up to"),
        (r"\bimprisonment for life\b", "life imprisonment"),
        (r"\bthe State shall\b", "the State should"),
        (r"\bParliament may\b", "Parliament can"),
        (r"\bconverts to his own use\b", "uses as their own"),
        (r"\bdishonestly misappropriates\b", "dishonestly takes or keeps"),
        (r"\bwrongful gain\b", "wrongful gain"),
    ]
    out = text
    for pattern, repl in subs:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def _sentences(text: str, max_count: int = 2) -> list[str]:
    picked: list[str] = []
    for part in re.split(r"(?<=[.!?])\s+", text):
        part = part.strip()
        if len(part) < 15:
            continue
        if re.match(r"^\([a-z]\)", part, re.I):
            continue
        if part.lower().startswith("illustration"):
            break
        picked.append(part)
        if len(picked) >= max_count:
            break
    return picked


def build_simple_summary(
    official: str,
    title: str,
    *,
    unit_label: str,
    number: str,
    status: str,
) -> str:
    if status == "omitted" or re.search(
        r"\b(Omitted|Repealed|Rep\.)\b", official[:220], re.I
    ):
        label = f"{unit_label} {number}".strip() or title
        return (
            f"{label} is no longer in force (omitted or repealed). "
            "It is kept in the code only for historical reference."
        )

    operative = extract_operative(official)
    operative = simplify_phrasing(operative)

    sents = _sentences(operative, 2)
    if not sents:
        sents = _sentences(operative + " " + operative, 1) or [operative[:420]]

    summary = " ".join(sents)
    title_norm = title.strip().rstrip(".").lower()
    if summary.strip().rstrip(".").lower() == title_norm and len(operative) > len(title) + 20:
        sents = _sentences(operative, 3)
        summary = " ".join(sents) if sents else operative[:480]

    if title_norm and title_norm not in summary.lower()[:80]:
        summary = f"{title.rstrip('.')}: {summary}"

    if len(summary) > 560:
        summary = summary[:557].rsplit(" ", 1)[0] + "…"
    return summary
