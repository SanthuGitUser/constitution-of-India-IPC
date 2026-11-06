import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { LawMeta, Provision } from "../types";

type Props = {
  meta: LawMeta;
  onSearch: (query: string) => Provision[];
  onSelect: (article: Provision) => void;
};

function cleanTitle(title: string, max = 100): string {
  const t = title.replace(/\s+/g, " ").trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1).trim()}…`;
}

export function SearchBar({ meta, onSearch, onSelect }: Props) {
  const unit = meta.unitLabel ?? "Section";
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Provision[]>([]);
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const [menuRect, setMenuRect] = useState<DOMRect | null>(null);

  const updateMenuPosition = () => {
    const el = inputRef.current ?? rootRef.current;
    if (!el) return;
    setMenuRect(el.getBoundingClientRect());
  };

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 1) {
      setResults([]);
      setOpen(false);
      return;
    }
    if (trimmed.length === 1 && !/^\d$/.test(trimmed)) {
      setResults([]);
      setOpen(false);
      return;
    }
    setResults(onSearch(trimmed));
    setOpen(true);
  }, [query, onSearch]);

  useLayoutEffect(() => {
    if (!open) return;
    updateMenuPosition();
    const onScroll = () => updateMenuPosition();
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("resize", onScroll);
    };
  }, [open, results.length, query]);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      const t = e.target as Node;
      if (rootRef.current?.contains(t)) return;
      if ((t as Element).closest?.(".search-results-portal")) return;
      setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const showMenu = open && query.trim().length > 0;
  const menu =
    showMenu && menuRect
      ? createPortal(
          <div
            className="search-results-portal"
            style={{
              position: "fixed",
              top: menuRect.bottom + 6,
              left: menuRect.left,
              width: menuRect.width,
            }}
            role="presentation"
          >
            {results.length === 0 ? (
              <p className="search-empty">No matching {unit.toLowerCase()}s.</p>
            ) : (
              <ul className="search-results" role="listbox" aria-label="Search results">
                {results.map((a) => (
                  <li key={a.id}>
                    <button
                      type="button"
                      role="option"
                      onClick={() => {
                        onSelect(a);
                        setOpen(false);
                        setQuery("");
                      }}
                    >
                      <span className="search-num">
                        {a.number ? `${unit} ${a.number}` : "Preamble"}
                      </span>
                      <span className="search-title">
                        {cleanTitle(a.title || "Untitled")}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>,
          document.body,
        )
      : null;

  return (
    <div className="search" ref={rootRef}>
      <label className="visually-hidden" htmlFor="law-search">
        Search
      </label>
      <div className="search-input-wrap">
        <input
          ref={inputRef}
          id="law-search"
          type="search"
          placeholder={`Search ${unit.toLowerCase()} (e.g. 302) or keyword…`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            updateMenuPosition();
            if (query.trim()) setOpen(true);
          }}
          autoComplete="off"
          aria-autocomplete="list"
          aria-expanded={showMenu}
        />
      </div>
      {menu}
    </div>
  );
}
