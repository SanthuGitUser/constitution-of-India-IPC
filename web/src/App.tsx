import { useCallback, useEffect, useMemo, useState } from "react";
import { ProvisionView } from "./components/ProvisionView";
import { SearchBar } from "./components/SearchBar";
import { Sidebar } from "./components/Sidebar";
import { useLawData } from "./hooks/useLawData";
import { LAW_CONFIG, type LawTab, type Provision } from "./types";
import "./App.css";

function tabFromSearch(): LawTab {
  const t = new URLSearchParams(window.location.search).get("law");
  return t === "ipc" ? "ipc" : "constitution";
}

function provisionFromHash(articles: Provision[], tab: LawTab): Provision | undefined {
  const hash = window.location.hash.replace(/^#/, "");
  if (!hash) return undefined;
  const prefix = `${tab}-`;
  const id = hash.startsWith(prefix) ? hash.slice(prefix.length) : hash;
  return articles.find((a) => a.id === id);
}

type WorkspaceProps = {
  tab: LawTab;
  onTabChange: (tab: LawTab) => void;
};

function LawWorkspace({ tab, onTabChange }: WorkspaceProps) {
  const config = LAW_CONFIG[tab];
  const { data, error, loading, search } = useLawData(config.path);
  const [selectedId, setSelectedId] = useState(config.defaultId);

  const articles = data?.articles ?? [];
  const selected = useMemo(
    () => articles.find((a) => a.id === selectedId) ?? articles[0],
    [articles, selectedId],
  );

  useEffect(() => {
    if (!articles.length) return;
    const fromHash = provisionFromHash(articles, tab);
    if (fromHash) setSelectedId(fromHash.id);
    else setSelectedId(config.defaultId);
  }, [articles, tab, config.defaultId]);

  const selectProvision = useCallback(
    (id: string) => {
      setSelectedId(id);
      window.location.hash = `${tab}-${id}`;
    },
    [tab],
  );

  const handleSearch = useCallback(
    (query: string) => search(query),
    [search],
  );

  return (
    <>
      <header className="app-header">
        <div className="topbar-row">
          <div className="brand">
            <span className="brand-mark" aria-hidden="true" />
            <div>
              <p className="brand-title">Indian Law — Plain Guide</p>
              <p className="brand-sub">Constitution &amp; IPC · English</p>
            </div>
          </div>
          <nav className="law-tabs" aria-label="Choose law">
            <button
              type="button"
              className={tab === "constitution" ? "active" : undefined}
              onClick={() => onTabChange("constitution")}
            >
              Constitution
            </button>
            <button
              type="button"
              className={tab === "ipc" ? "active" : undefined}
              onClick={() => onTabChange("ipc")}
            >
              IPC
            </button>
          </nav>
        </div>

        <div className="toolbar-row">
          {loading ? (
            <div className="toolbar-loading">Loading search…</div>
          ) : data ? (
            <>
              <SearchBar
                meta={data.meta}
                onSearch={handleSearch}
                onSelect={(p) => selectProvision(p.id)}
              />
              <p className="subbar-meta">
                {data.meta.lawName ?? config.shortName}
                {data.meta.asOn ? ` · as on ${data.meta.asOn}` : ""}
              </p>
            </>
          ) : null}
        </div>
      </header>

      {loading && (
        <div className="panel-loading">Loading {config.shortName}…</div>
      )}

      {!loading && (error || !data || !selected) && (
        <div className="panel-loading">{error ?? "Unable to load content."}</div>
      )}

      {!loading && data && selected && (
        <>
          <div className="layout">
            <Sidebar
              parts={data.parts}
              articles={articles}
              selectedId={selectedId}
              meta={data.meta}
              onSelect={selectProvision}
            />
            <main>
              <ProvisionView provision={selected} meta={data.meta} />
            </main>
          </div>
          <footer className="site-footer">
            <p>{data.meta.editionNote}</p>
            <p>
              Source file: {data.meta.source}
              {data.meta.actNumber ? ` · ${data.meta.actNumber}` : ""}. For legal
              proceedings, rely on the official Gazette / government publication.
            </p>
          </footer>
        </>
      )}
    </>
  );
}

function App() {
  const [tab, setTab] = useState<LawTab>(tabFromSearch);

  const switchTab = (next: LawTab) => {
    setTab(next);
    const url = new URL(window.location.href);
    url.searchParams.set("law", next);
    url.hash = `${next}-${LAW_CONFIG[next].defaultId}`;
    window.history.replaceState(null, "", url.toString());
  };

  useEffect(() => {
    const onPop = () => setTab(tabFromSearch());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  return (
    <div className="app-shell">
      <LawWorkspace tab={tab} onTabChange={switchTab} />
    </div>
  );
}

export default App;
