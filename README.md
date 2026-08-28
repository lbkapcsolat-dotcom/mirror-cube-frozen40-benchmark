# Frozen 40-State Exact HTM Benchmark — MC-F40-EXACT-HTM-V1

This bundle publishes a **read-only benchmark view** of a frozen 40-state candidate pool on the standard 3x3 cubie backend under the Half Turn Metric (HTM).

## Result

- 40/40 states have exact distances.
- Exact distance 12: **4 states** — ordinals **7, 9, 20, 29**.
- Exact distance 13: **36 states** — all remaining ordinals.
- Frozen pool SHA-256: `9d0faf5229f56bfc203a68a54d56eff23b56c804588511c04d84774f98e198bd`
- Canonical final seal root: `2cd24c9d2fb473bbab9bc79e79a2ce59373fad324fe0ad9bddf65ab917732fd8`

## Files

- `data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv` — portable tabular benchmark.
- `data/FROZEN_40_EXACT_DISTANCE_LEDGER.json` — canonical detailed ledger.
- `data/EXACT12_WITNESS_REGISTRY.json` — four verified 12-move witnesses.
- `data/DEPTH13_CANDIDATE_POOL_V1.json` — frozen source pool.
- `BENCHMARK_READ_ONLY_LOCK.json` — immutable V1 lock contract.
- `BENCHMARK_METADATA.json` — publication metadata and release boundaries.
- `docs/METHOD.md` — classification method.
- `docs/REPRODUCIBILITY.md` — integrity and proof-reproduction notes.
- `provenance/` — final seal, receipt, verification report, and predecessor lineage.
- `verify_benchmark_bundle.py` — standalone bundle-integrity verifier.
- `SHA256SUMS` — file hashes for the publication payload.

## Read-only rule

This V1 benchmark is immutable. Any changed state, sequence, witness, proof basis, classification, or metadata that affects benchmark meaning requires a **new version and new seal**, not an in-place edit.

## Scope boundary

BOUNDED_FROZEN_40_STATE_DEPTH13_CANDIDATE_POOL; STANDARD_3X3_HTM_CUBIE_BACKEND; EXACT_DISTANCE_FOR_THESE_40_FROZEN_STATES_ONLY; NO_COMPLETE_3X3_STATE_SPACE_DIAMETER_PROOF; NO_PHYSICAL_MIRROR_CUBE_VISION_OR_ROBOTICS_SOLVER; NO_GLOBAL_SOLVER_OPTIMALITY_CLAIM; REMOTE_16_STATE_PREDECESSOR_BYTES_NOT_CURRENTLY_LOCAL_ONLY_PREVIOUSLY_VERIFIED_HASH_AUTHORITY.

## Release boundary

This package does **not** assert an author identity, copyright license grant, DOI, or repository publication. Those are owner/repository actions outside this gate.
