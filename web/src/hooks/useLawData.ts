import { useEffect, useMemo, useState } from "react";
import Fuse from "fuse.js";
import type { LawData, Provision } from "../types";

export function useLawData(jsonPath: string) {
  const [data, setData] = useState<LawData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(jsonPath)
      .then((r) => {
        if (!r.ok) throw new Error("Could not load content.");
        return r.json();
      })
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [jsonPath]);

  const fuse = useMemo(() => {
    if (!data) return null;
    return new Fuse(data.articles, {
      keys: [
        { name: "number", weight: 0.4 },
        { name: "title", weight: 0.35 },
        { name: "simpleText", weight: 0.2 },
        { name: "officialText", weight: 0.05 },
      ],
      threshold: 0.35,
      ignoreLocation: true,
    });
  }, [data]);

  const search = (query: string, limit = 12): Provision[] => {
    if (!data || !query.trim()) return [];
    const q = query.trim().toLowerCase();

    if (/^\d+[a-z]?$/.test(q)) {
      const exact = data.articles.find(
        (a) => a.number.toLowerCase() === q,
      );
      if (exact) return [exact];
    }

    if (/^\d+[a-z]?$/.test(q)) {
      const prefix = data.articles
        .filter((a) => a.number && a.number.toLowerCase().startsWith(q))
        .slice(0, limit);
      if (prefix.length) return prefix;
    }

    return fuse?.search(q, { limit }).map((r) => r.item) ?? [];
  };

  return { data, error, loading, search };
}
