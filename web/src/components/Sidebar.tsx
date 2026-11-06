import type { LawMeta, Part, Provision } from "../types";

type Props = {
  parts: Part[];
  articles: Provision[];
  selectedId: string;
  meta: LawMeta;
  onSelect: (id: string) => void;
};

export function Sidebar({ parts, articles, selectedId, meta, onSelect }: Props) {
  const partWord = meta.partLabel ?? "Part";
  const byPart = new Map<string, Provision[]>();
  for (const a of articles) {
    const list = byPart.get(a.partId) ?? [];
    list.push(a);
    byPart.set(a.partId, list);
  }

  return (
    <nav className="sidebar" aria-label="Document outline">
      {parts.map((part) => {
        const items = byPart.get(part.id) ?? [];
        if (!items.length) return null;
        return (
          <details key={part.id} open={items.some((a) => a.id === selectedId)}>
            <summary>
              {part.number ? `${partWord} ${part.number}` : part.title}
              <span className="part-sub">{part.title}</span>
            </summary>
            <ul>
              {items.map((a) => (
                <li key={a.id}>
                  <button
                    type="button"
                    className={a.id === selectedId ? "active" : undefined}
                    onClick={() => onSelect(a.id)}
                  >
                    {a.number ? `${a.number}.` : "—"}{" "}
                    <span>{a.title || "Preamble"}</span>
                    {a.status === "omitted" && (
                      <em className="badge">omitted</em>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </details>
        );
      })}
    </nav>
  );
}
