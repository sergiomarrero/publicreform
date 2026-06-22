import React, { useMemo, useState } from "react";
import dataset from "./data/states.json";
import StateTable from "./components/StateTable.jsx";
import SourcesPanel from "./components/SourcesPanel.jsx";
import Methodology from "./components/Methodology.jsx";
import CompositePlaceholder from "./components/CompositePlaceholder.jsx";
import { compareValues } from "./format.js";

export default function App() {
  const [query, setQuery] = useState("");
  const [showTerritories, setShowTerritories] = useState(false);
  const [sortKey, setSortKey] = useState("name");
  const [sortDir, setSortDir] = useState("asc");

  const build = dataset.meta.build || { status: "interim" };
  const interim = build.status !== "full";

  const onSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "name" ? "asc" : "desc");
    }
  };

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matches = (s) => !q || s.name.toLowerCase().includes(q);

    const ranking = dataset.states.filter(
      (s) => !s.excluded_from_ranking && matches(s)
    );
    const territories = dataset.states.filter(
      (s) => s.excluded_from_ranking && matches(s)
    );

    const sortGroup = (group) => {
      const sorted = [...group];
      if (sortKey === "name") {
        sorted.sort((a, b) =>
          sortDir === "asc"
            ? a.name.localeCompare(b.name)
            : b.name.localeCompare(a.name)
        );
      } else {
        sorted.sort((a, b) =>
          compareValues(
            a.metrics[sortKey] ? a.metrics[sortKey].value : null,
            b.metrics[sortKey] ? b.metrics[sortKey].value : null,
            sortDir
          )
        );
      }
      return sorted;
    };

    // Ranked jurisdictions first. Territories, when shown, always sit after the
    // ranked set so they never enter the ranking.
    const out = sortGroup(ranking);
    if (showTerritories) out.push(...sortGroup(territories));
    return out;
  }, [query, showTerritories, sortKey, sortDir]);

  const rankingCount = dataset.meta.ranking_jurisdiction_count;

  return (
    <div className="page">
      <header className="site-header">
        <div className="wrap">
          <h1>Public Reform State Dashboard</h1>
          <p className="tagline">
            State-level administrative performance across Unemployment Insurance,
            SNAP, and WIOA. Descriptive and correlational. Every figure carries a
            source and vintage.
          </p>
        </div>
      </header>

      {interim ? (
        <div className="build-banner">
          <div className="wrap">
            <strong>Interim build.</strong> {build.note} Live now:{" "}
            {(build.live_metrics || []).length} of{" "}
            {(build.live_metrics || []).length +
              (build.pending_metrics || []).length}{" "}
            dimensions. Pending dimensions show pending, not numbers.
          </div>
        </div>
      ) : null}

      <main className="wrap">
        <section className="controls">
          <label className="search">
            <span className="sr-only">Filter by state name</span>
            <input
              type="text"
              placeholder="Filter by state name"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
          <label className="toggle">
            <input
              type="checkbox"
              checked={showTerritories}
              onChange={(e) => setShowTerritories(e.target.checked)}
            />
            Show territories (not ranked)
          </label>
          <div className="scope-note">
            Ranked view: {rankingCount} jurisdictions (50 states and DC). Click a
            column to sort.
          </div>
        </section>

        <StateTable
          dataset={dataset}
          rows={rows}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={onSort}
        />

        <CompositePlaceholder dataset={dataset} />
        <SourcesPanel dataset={dataset} />
        <Methodology dataset={dataset} />
      </main>

      <footer className="site-footer">
        <div className="wrap">
          <p>
            Built {build.built_at ? build.built_at.slice(0, 10) : ""} from{" "}
            {build.source_file || "validated pipeline output"}. Generated{" "}
            {dataset.meta.generated_at
              ? dataset.meta.generated_at.slice(0, 10)
              : ""}
            . Data is descriptive and correlational; no causal claims.
          </p>
        </div>
      </footer>
    </div>
  );
}
