"""
Extract English text from ipc-english.pdf into structured JSON (same schema as constitution).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import sys

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plain_language import build_simple_summary

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "ipc-english.pdf"
OUT_PATH = ROOT / "web" / "public" / "data" / "ipc.json"

CHAPTER_LINE = re.compile(r"^CHAPTER\s+([IVXLC]+|\d+)\b", re.I)
SECTION_LINE = re.compile(r"^(\d+[A-Z]?)\.\s*(.*)$")


def parse_arrangement(doc: fitz.Document) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Return section order, titles, and section -> chapter title."""
    order: list[str] = []
    titles: dict[str, str] = {}
    section_chapter: dict[str, str] = {}
    seen: set[str] = set()
    current_chapter = "Introduction"

    for page_idx in range(0, min(13, doc.page_count)):
        lines = [ln.strip() for ln in doc[page_idx].get_text("text").splitlines() if ln.strip()]
        idx = 0
        while idx < len(lines):
            line = lines[idx]
            if line.upper() in {"SECTIONS", "ARRANGEMENT OF SECTIONS", "PREAMBLE"}:
                idx += 1
                continue
            if line.startswith("THE INDIAN PENAL CODE") or line.startswith("_"):
                idx += 1
                continue
            ch = CHAPTER_LINE.match(line)
            if ch:
                title_bits = [line]
                idx += 1
                while idx < len(lines) and not CHAPTER_LINE.match(lines[idx]):
                    if SECTION_LINE.match(lines[idx]) or lines[idx].upper() == "SECTIONS":
                        break
                    if lines[idx].upper() not in {"PREAMBLE"}:
                        title_bits.append(lines[idx])
                    idx += 1
                current_chapter = re.sub(r"\s+", " ", " ".join(title_bits))
                continue

            m = SECTION_LINE.match(line)
            if m:
                num = m.group(1)
                rest = m.group(2).strip()
                title_parts = [rest] if rest else []
                idx += 1
                while idx < len(lines):
                    nxt = lines[idx]
                    if SECTION_LINE.match(nxt) or CHAPTER_LINE.match(nxt):
                        break
                    if nxt.upper() == "SECTIONS":
                        idx += 1
                        break
                    title_parts.append(nxt)
                    idx += 1
                title = re.sub(r"\s+", " ", " ".join(title_parts)).strip(" .")
                if num not in seen:
                    order.append(num)
                    seen.add(num)
                titles[num] = title
                section_chapter[num] = current_chapter
                continue
            idx += 1

    return order, titles, section_chapter


def find_body_start_page(doc: fitz.Document) -> int:
    for i in range(10, min(20, doc.page_count)):
        text = doc[i].get_text("text")
        if "ACT NO." in text and "Preamble.—" in text:
            return i
    return 13


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r" \.", ".", text)
    return text


def is_section_anchor(body: str, anchor: int, num: str) -> bool:
    window = body[anchor : anchor + 280].lstrip()
    if not window.startswith(num + "."):
        return False
    if re.match(rf"{re.escape(num)}\.\s+\[", window):
        return True
    head = window[:220]
    if ".—" in head or ".\u2014" in head:
        return True
    if re.search(r"\b(Omitted|Repealed|Rep\.)\b", head[:140]):
        return True
    return False


def find_section_start(body: str, num: str, search_from: int) -> int | None:
    pattern = re.compile(rf"(?:^|\n){re.escape(num)}\.\s+")
    pos = search_from
    while True:
        m = pattern.search(body, pos)
        if not m:
            return None
        anchor = m.start() + (1 if body[m.start()] == "\n" else 0)
        if is_section_anchor(body, anchor, num):
            return anchor
        pos = m.end()


def split_sections(body: str, order: list[str]) -> list[tuple[str, int, int]]:
    starts: list[tuple[str, int]] = []
    search_from = 0
    for num in order:
        anchor = find_section_start(body, num, search_from)
        if anchor is None:
            continue
        if starts and anchor <= starts[-1][1]:
            anchor = find_section_start(body, num, starts[-1][1] + 5)
            if anchor is None:
                continue
        starts.append((num, anchor))
        search_from = anchor + 5

    end_limit = len(body)
    footnote_cut = body.find("\n\n\n\n")
    if footnote_cut == -1:
        for marker in ("\n1. Subs. by Act", "\n1. Ins. by Act"):
            idx = body.rfind(marker)
            if idx > len(body) * 0.85:
                end_limit = idx
                break

    spans: list[tuple[str, int, int]] = []
    for idx, (num, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else end_limit
        spans.append((num, start, end))
    return spans


def section_status(text: str) -> str:
    head = text[:160]
    if re.search(r"\b(Omitted|Repealed|Rep\.)\b", head, re.I):
        return "omitted"
    return "active"


def draft_simple(num: str, title: str, official: str, status: str) -> str:
    return build_simple_summary(
        official,
        title,
        unit_label="Section",
        number=num,
        status=status,
    )


@dataclass
class Entry:
    id: str
    number: str
    title: str
    partId: str
    partTitle: str
    officialText: str
    simpleText: str
    status: str
    explainerReviewed: bool


def chapter_id(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]
    return f"chapter-{slug or 'intro'}"


def main() -> None:
    doc = fitz.open(PDF_PATH)
    order, titles, section_chapter = parse_arrangement(doc)
    start_page = find_body_start_page(doc)
    body = "\n\n".join(doc[i].get_text("text") for i in range(start_page, doc.page_count))
    body = re.sub(r"\n{3,}", "\n\n", body)

    preamble_match = re.search(
        r"Preamble\.—(.+?)(?=\n1\.\s+Title and extent)",
        body,
        re.DOTALL | re.I,
    )
    preamble_text = normalize(preamble_match.group(0)) if preamble_match else ""

    meta = {
        "source": PDF_PATH.name,
        "editionNote": "Plain-language summaries appear beside official text; summaries are AI-assisted drafts for learning.",
        "lawName": "Indian Penal Code",
        "unitLabel": "Section",
        "partLabel": "Chapter",
    }
    act = re.search(r"ACT NO\.\s*(\d+\s+OF\s+\d+)", body, re.I)
    if act:
        meta["actNumber"] = act.group(1)

    parts_meta: list[dict] = []
    part_ids: dict[str, str] = {}
    entries: list[Entry] = []

    if preamble_text:
        parts_meta.append({"id": "preamble", "number": "", "title": "Preamble"})
        entries.append(
            Entry(
                id="preamble",
                number="",
                title="Preamble",
                partId="preamble",
                partTitle="Preamble",
                officialText=preamble_text,
                simpleText=(
                    "The IPC was enacted to create one general criminal code for India, "
                    "replacing a patchwork of separate laws so offences and punishments "
                    "could be defined clearly and applied consistently."
                ),
                status="active",
                explainerReviewed=True,
            )
        )

    spans = split_sections(body, order)
    for num, start, end in spans:
        chunk = body[start:end].strip()
        ch_title = section_chapter.get(num, "Indian Penal Code")
        pid = part_ids.get(ch_title)
        if not pid:
            pid = chapter_id(ch_title)
            part_ids[ch_title] = pid
            ch_num_match = re.search(r"CHAPTER\s+([IVXLC]+|\d+)", ch_title, re.I)
            parts_meta.append(
                {
                    "id": pid,
                    "number": ch_num_match.group(1).upper() if ch_num_match else "",
                    "title": re.sub(r"^CHAPTER\s+[IVXLC\d]+\s*", "", ch_title, flags=re.I).strip()
                    or ch_title,
                }
            )

        title = titles.get(num, "")
        if not title:
            head = re.match(r"^\d+[A-Z]?\.\s+([^.—\n]+)", chunk)
            title = head.group(1).strip() if head else f"Section {num}"

        official = normalize(chunk)
        status = section_status(chunk)
        entries.append(
            Entry(
                id=f"section-{num.lower()}",
                number=num,
                title=title,
                partId=pid,
                partTitle=parts_meta[-1]["title"] if parts_meta else ch_title,
                officialText=official,
                simpleText=draft_simple(num, title, official, status),
                status=status,
                explainerReviewed=False,
            )
        )

    payload = {
        "meta": meta,
        "parts": parts_meta,
        "articles": [asdict(e) for e in entries],
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"IPC: {len(entries)} entries from {len(spans)} sections ({len(order)} in contents)")


if __name__ == "__main__":
    main()
