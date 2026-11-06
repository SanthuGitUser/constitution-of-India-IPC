export type LawMeta = {
  source: string;
  asOn?: string;
  editionNote: string;
  lawName?: string;
  unitLabel?: string;
  partLabel?: string;
  actNumber?: string;
};

export type Part = {
  id: string;
  number: string;
  title: string;
};

export type Provision = {
  id: string;
  number: string;
  title: string;
  partId: string;
  partTitle: string;
  officialText: string;
  simpleText: string;
  status: "active" | "omitted";
  explainerReviewed: boolean;
};

export type LawData = {
  meta: LawMeta;
  parts: Part[];
  articles: Provision[];
};

export type LawTab = "constitution" | "ipc";

export const LAW_CONFIG: Record<
  LawTab,
  { path: string; defaultId: string; shortName: string }
> = {
  constitution: {
    path: "/data/constitution.json",
    defaultId: "preamble",
    shortName: "Constitution",
  },
  ipc: {
    path: "/data/ipc.json",
    defaultId: "preamble",
    shortName: "IPC",
  },
};

/** @deprecated use LawData */
export type ConstitutionData = LawData;
/** @deprecated use Provision */
export type Article = Provision;
