# Tensor — Frozen 40-State Exact HTM Benchmark

**CANONICAL_RESEARCH_IDENTITY:** Tensor  
**BENCHMARK_ID:** `TENSOR-F40-EXACT-HTM-V1`  
**STATUS:** current public research surface

Tensor is the current public research identity for this bounded 40-state exact-distance benchmark on the standard 3x3 cubie backend under the Half Turn Metric (HTM).

## Published result

- 40 frozen benchmark states.
- Exact HTM distance 12: 4 states, ordinals 7, 9, 20 and 29.
- Exact HTM distance 13: 36 states.
- The checked-in ledger and four public witnesses remain the reproducible data surface.

## Public files

- `data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv` — 40-row benchmark ledger.
- `data/EXACT12_WITNESS_REGISTRY.json` — four replayable 12-move witnesses.
- `repro/` — bounded public reproduction tooling.
- `tests/` — bounded regression tests.
- `docs/METHOD.md` — method summary.
- `docs/CLAIM_CEILING.md` — explicit scope boundary.
- `docs/CURRENT_VS_HISTORICAL_PUBLIC_SURFACE_POLICY.md` — current-vs-historical provenance policy.

## Claim boundary

This repository supports only the bounded claims stated for these 40 frozen standard-3x3 states. It does not establish a complete 3x3 state-space diameter theorem, global solver optimality, physical puzzle perception, robotics capability, or universal results outside this benchmark.

## Identity boundary

**Tensor** is the research identity of this public benchmark surface.

**Equilibrium Stability System (ESS)** is a separate system identity. This repository is not the ESS system root and does not publish ESS internal formulas, scoring weights, control-plane state, authority records, or runtime admission.

Older branch names, tags, releases, commits, URLs, or labels may remain visible solely as historical provenance. They are **inactive**, **non-authoritative**, and **not current Tensor identity**. The current `main` branch and `TENSOR_PUBLIC_IDENTITY_MANIFEST_V1.md` control current public identity.

**Current-surface rule:** `main` is the only current branch authority for Tensor public identity in this repository. Historical tags/releases may remain visible for lineage, but they are provenance-only and do not define current identity.
