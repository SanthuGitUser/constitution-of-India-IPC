import type { LawMeta, Provision } from "../types";

type Props = {
  provision: Provision;
  meta: LawMeta;
};

export function ProvisionView({ provision, meta }: Props) {
  const unit = meta.unitLabel ?? "Article";
  const law = meta.lawName ?? "Constitution of India";
  const heading = provision.number
    ? `${unit} ${provision.number}`
    : "Preamble";

  return (
    <article className="article-view">
      <header className="article-header">
        <div className="article-header-top">
          <span className="crumb">{provision.partTitle}</span>
          {provision.status === "omitted" && (
            <span className="status-pill status-pill--muted">Not in force</span>
          )}
          {provision.status === "active" && provision.number && (
            <span className="status-pill status-pill--live">In force</span>
          )}
        </div>
        <h1>{heading}</h1>
        {provision.title && provision.number && (
          <p className="article-title">{provision.title}</p>
        )}
        {!provision.explainerReviewed && (
          <p className="draft-note">
            <span className="draft-note-icon" aria-hidden="true">
              ✦
            </span>
            Summary is an AI-assisted draft — official text is on the right.
          </p>
        )}
      </header>

      <div className="dual-read">
        <section
          className="read-pane read-pane--simple"
          aria-label="Plain-language summary"
        >
          <div className="read-pane-label">
            <span className="read-pane-dot read-pane-dot--simple" />
            In simple terms
          </div>
          <p>{provision.simpleText}</p>
        </section>
        <section
          className="read-pane read-pane--official"
          aria-label={`Official ${law} text`}
        >
          <div className="read-pane-label">
            <span className="read-pane-dot read-pane-dot--official" />
            Official text
          </div>
          <p>{provision.officialText}</p>
        </section>
      </div>
    </article>
  );
}
