"""
Extract English text from the official Constitution of India PDF into structured JSON.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

import sys

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plain_language import build_simple_summary

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "20240716890312078.pdf"
OUT_PATH = ROOT / "web" / "public" / "data" / "constitution.json"

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
OMITTED = re.compile(r"Omitted\.?\]?$", re.I)


def is_english_line(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if DEVANAGARI.search(t):
        return False
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return True
    latin = sum(1 for c in letters if ord(c) < 128)
    return latin / len(letters) > 0.85


def page_english_text(page: fitz.Page, x_max: float = 330.0) -> str:
    lines_out: list[str] = []
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            if line["bbox"][0] > x_max:
                continue
            text = "".join(span["text"] for span in line.get("spans", []))
            if is_english_line(text):
                lines_out.append(text.rstrip())
    return "\n".join(lines_out)


def clean_boilerplate(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(
        r"^\s*\d+\s*\n\s*THE CONSTITUTION OF INDIA[^\n]*\n",
        "",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    text = re.sub(r"\(Part [^)]+\)\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def article_sort_key(num: str) -> tuple[int, str]:
    m = re.fullmatch(r"(\d+)([A-Z]?)", num)
    if not m:
        return (9999, num)
    return (int(m.group(1)), m.group(2))


def parse_contents(doc: fitz.Document) -> tuple[list[str], dict[str, str]]:
    order: list[str] = []
    titles: dict[str, str] = {}
    seen: set[str] = set()

    for i in range(2, min(31, doc.page_count)):
        lines = [
            ln.strip()
            for ln in doc[i].get_text("text").splitlines()
            if ln.strip() and not DEVANAGARI.search(ln)
        ]
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            m = re.match(r"^\[?(\d+[A-Z]?)\.\s*(.*)$", line)
            if m:
                num = m.group(1)
                rest = m.group(2).strip()
                title_parts: list[str] = []
                if rest and not rest.endswith("]") and "Omitted" not in rest:
                    title_parts.append(rest)
                elif rest:
                    title_parts.append(rest)
                idx += 1
                while idx < len(lines):
                    nxt = lines[idx]
                    if re.match(r"^\[?(\d+[A-Z]?)\.", nxt):
                        break
                    if nxt.upper().startswith("PART "):
                        break
                    if nxt.upper() in {"ARTICLES", "CONTENTS", "PREAMBLE"}:
                        idx += 1
                        continue
                    title_parts.append(nxt)
                    idx += 1
                    if "Omitted" in nxt or nxt.endswith("]"):
                        break
                title = re.sub(r"\s+", " ", " ".join(title_parts)).strip(" .[]")
                if num not in seen:
                    order.append(num)
                    seen.add(num)
                titles[num] = title
                continue
            idx += 1

    return order, titles


def is_constitution_article_anchor(body: str, anchor: int, num: str) -> bool:
    window = body[anchor : anchor + 240].lstrip()
    if not window.startswith(num + "."):
        return False
    if re.match(rf"{re.escape(num)}\.\s+\[", window):
        return True
    head = window[:200]
    return ".—" in head or ".\u2014" in head or ". ---" in head


def find_body_pages(doc: fitz.Document) -> tuple[int, int]:
    start_page = 31
    for i in range(28, min(45, doc.page_count)):
        if "WE, THE PEOPLE" in page_english_text(doc[i]).upper():
            start_page = i
            break
    end_page = doc.page_count - 1
    for i in range(start_page, doc.page_count):
        t = page_english_text(doc[i])
        if re.search(r"\b395\.\s+Short title", t, re.I):
            end_page = i + 2
            break
    return start_page, min(end_page, doc.page_count - 1)


def extract_preamble_and_body(raw: str) -> tuple[str, str]:
    raw = clean_boilerplate(raw)
    marker = "WE, THE PEOPLE"
    pos = raw.upper().find(marker)
    if pos == -1:
        return "", raw
    part = re.search(r"\nPART\s+I\s*\n", raw[pos:], re.I)
    if not part:
        return raw[pos:].strip(), ""
    preamble = raw[pos : pos + part.start()].strip()
    body = raw[pos + part.start() :].strip()
    return preamble, body


def normalize_official(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r" \.", ".", text)
    return text


def draft_simple_explainer(num: str, title: str, official: str) -> str:
    status = "omitted" if OMITTED.search(official) or re.search(r"—Omitted", official, re.I) else "active"
    return build_simple_summary(
        official,
        title,
        unit_label="Article",
        number=num,
        status=status,
    )


@dataclass
class Article:
    id: str
    number: str
    title: str
    partId: str
    partTitle: str
    officialText: str
    simpleText: str
    status: str
    explainerReviewed: bool


def find_article_start(body: str, num: str, search_from: int) -> int | None:
    pattern = re.compile(rf"(?:^|\n){re.escape(num)}\.\s+")
    pos = search_from
    while True:
        m = pattern.search(body, pos)
        if not m:
            return None
        anchor = m.start() + (1 if body[m.start()] == "\n" else 0)
        if is_constitution_article_anchor(body, anchor, num):
            return anchor
        pos = m.end()


def split_by_contents(body: str, order: list[str]) -> list[tuple[str, int, int]]:
    starts: list[tuple[str, int]] = []
    search_from = 0
    for num in order:
        anchor = find_article_start(body, num, search_from)
        if anchor is None:
            continue
        if starts and anchor <= starts[-1][1]:
            anchor = find_article_start(body, num, starts[-1][1] + 8)
            if anchor is None:
                continue
        starts.append((num, anchor))
        search_from = anchor + 8

    spans: list[tuple[str, int, int]] = []
    schedule_start = len(body)
    sched_match = re.search(r"(?:^|\n)\d*\[?FIRST SCHEDULE\b", body)
    if sched_match:
        schedule_start = sched_match.start()
    body_limit = schedule_start

    for idx, (num, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else body_limit
        spans.append((num, start, end))
    return spans


def assign_parts(body: str, spans: list[tuple[str, int, int]]) -> dict[str, tuple[str, str]]:
    part_header = re.compile(
        r"PART\s+([IVXLC]+|\d+)\s*\n([^\n]+)",
        re.IGNORECASE,
    )
    mapping: dict[str, tuple[str, str]] = {}
    current = ("part-i", "THE UNION AND ITS TERRITORY")
    for num, start, end in spans:
        chunk_head = body[max(0, start - 120) : start + 80]
        headers = list(part_header.finditer(chunk_head))
        if headers:
            h = headers[-1]
            part_num = h.group(1).upper()
            part_title = re.sub(r"\s+", " ", h.group(2).strip())
            current = (f"part-{part_num.lower()}", part_title)
        mapping[num] = current
    return mapping


def main() -> None:
    doc = fitz.open(PDF_PATH)
    order, titles = parse_contents(doc)
    start_p, end_p = find_body_pages(doc)

    chunks = [page_english_text(doc[i]) for i in range(start_p, end_p + 1)]
    raw = "\n\n".join(chunks)
    preamble, body = extract_preamble_and_body(raw)

    meta = {
        "source": PDF_PATH.name,
        "editionNote": "Plain-language summaries appear beside official text; summaries are AI-assisted drafts for learning.",
        "lawName": "Constitution of India",
        "unitLabel": "Article",
        "partLabel": "Part",
    }
    m = re.search(r"As on (\d+[a-z]{2}\s+\w+\s+\d{4})", doc[0].get_text("text"), re.I)
    if m:
        meta["asOn"] = m.group(1)

    spans = split_by_contents(body, order)
    part_for = assign_parts(body, spans)

    parts_meta: list[dict] = [{"id": "preamble", "number": "", "title": "Preamble"}]
    seen_parts: set[str] = {"preamble"}
    articles: list[Article] = []

    if preamble:
        articles.append(
            Article(
                id="preamble",
                number="",
                title="Preamble",
                partId="preamble",
                partTitle="Preamble",
                officialText=normalize_official(preamble),
                simpleText=(
                    "India’s Constitution opens with a promise: we the people adopt "
                    "this document to secure justice, liberty, equality, and dignity "
                    "for all, and to build a sovereign, socialist, secular, democratic "
                    "republic where everyone can live with fraternity."
                ),
                status="active",
                explainerReviewed=True,
            )
        )

    for num, start, end in spans:
        chunk = body[start:end].strip()
        part_id, part_title = part_for.get(num, ("part-i", "Constitution"))
        if part_id not in seen_parts:
            parts_meta.append(
                {
                    "id": part_id,
                    "number": part_id.replace("part-", "").upper(),
                    "title": part_title,
                }
            )
            seen_parts.add(part_id)

        title = titles.get(num, "")
        if not title:
            head = re.match(r"^\d+[A-Z]?\.\s+([^.—\n]+)", chunk)
            title = head.group(1).strip() if head else f"Article {num}"

        official = normalize_official(chunk)
        status = "omitted" if re.search(r"Omitted", chunk[:100], re.I) else "active"

        articles.append(
            Article(
                id=f"article-{num.lower()}",
                number=num,
                title=title,
                partId=part_id,
                partTitle=part_title,
                officialText=official,
                simpleText=draft_simple_explainer(num, title, official),
                status=status,
                explainerReviewed=False,
            )
        )

    payload = {"meta": meta, "parts": parts_meta, "articles": [asdict(a) for a in articles]}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Articles: {len(articles)} (from {len(spans)} spans, {len(order)} in contents)")


if __name__ == "__main__":
    main()
