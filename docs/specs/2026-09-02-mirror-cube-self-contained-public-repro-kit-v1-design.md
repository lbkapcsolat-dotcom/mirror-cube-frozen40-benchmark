# MIRROR_CUBE_SELF_CONTAINED_PUBLIC_REPRO_KIT_V1 Design

## Objective

Build a new public, independently runnable reproduction layer beside the frozen MC-F40-EXACT-HTM-V1 benchmark without mutating any frozen V1 benchmark file, classification, witness, seal, or proof-basis artifact.

The new layer must independently reconstruct every frozen state from the published 13-move generator, replay the four published 12-move witnesses, and independently test the lower-bound side needed to distinguish exact distance 12 from exact distance 13.

## Non-negotiable boundaries

1. Frozen V1 remains byte-for-byte untouched.
2. The repro layer lives under `repro/` plus `tests/` and its own documentation/manifest.
3. No historical predecessor artifact is treated as independently reproduced merely because its hash appears in provenance.
4. The new implementation must use the published ledger and witness registry as inputs, not private remembered state.
5. A PASS for exact distance requires both an upper bound and an independently recomputed lower bound.
6. Any disagreement with V1 is reported as a counterexample/conflict; V1 is not silently edited.
7. Standard 3x3 cubie backend and Half Turn Metric only.
8. Standard-library Python only for the reference implementation. No paid service, API key, network dependency, hidden binary, or finite-credit dependency.
9. Fail closed: malformed moves, invalid cube states, incomplete search, resource exhaustion, missing inputs, or inconsistent hashes cannot produce PASS.

## Architecture

### 1. Cubie engine

`repro/cube.py` owns the standard 3x3 cubie state representation and the 18 HTM face moves. It exposes a small immutable state interface and deterministic sequence application. The implementation must validate cube invariants and support a compact canonical state key suitable for meet-in-the-middle search.

Required public interface:

- `CubeState.solved()`
- `CubeState.apply(move: str) -> CubeState`
- `CubeState.apply_sequence(sequence: str | list[str]) -> CubeState`
- `CubeState.is_solved() -> bool`
- `CubeState.validate() -> None`
- `CubeState.key() -> bytes`
- `parse_moves(text: str) -> list[str]`

### 2. Dataset loader and public replay

`repro/dataset.py` reads only the checked-in public CSV and witness JSON. It reconstructs each target state from solved by applying the published 13-move generator. It checks ordinals, classifications, lengths, and the generator SHA-256 field against the exact published sequence text convention used by the dataset.

`repro/replay.py` performs:

- all 40 generator replays;
- four exact-12 witness replays;
- explicit upper-bound checks;
- deterministic machine-readable output.

A witness replay PASS proves only `distance <= 12`; it does not prove exactness by itself.

### 3. Independent lower-bound engine

`repro/mitm.py` independently tests whether a target has a solution of length at most a requested HTM bound using a 6+6 meet-in-the-middle search.

For the V1 boundary:

- exact-12 candidates require proving no solution of length <=11;
- exact-13 candidates require proving no solution of length <=12.

The engine constructs the solved-side radius-6 state set from the new cubie implementation. Target-side bounded search then checks for intersections whose path lengths satisfy the requested bound. Immediate same-face repetitions are canonicalized so the search does not enumerate trivially reducible HTM sequences; correctness tests must show this pruning does not remove shortest solutions.

The solved-side authority must be recomputed, not copied from historical files. A successful build must reproduce the known shallow/radius census checkpoints recorded in the prior close-seal evidence:

- depth 1 exact count: 18;
- depth 2 exact count: 243;
- depth 3 exact count: 3240;
- unique states within radius <=5: 621649;
- unique states within radius <=6: 8240087.

If any checkpoint differs, the lower-bound engine stops with HOLD.

Because radius-6 contains millions of states, the implementation may use a disk-backed standard-library store if required. The default design is a deterministic SQLite cache under a user-selected cache path, keyed by the compact canonical cube key and storing minimum solved distance 0..6. Cache metadata binds engine version, move convention, schema version, and row count. A cache with mismatched metadata is rejected rather than reused.

### 4. Reproduction CLI

`repro/verify_public.py` is the user-facing entry point.

Commands:

- `python -m repro.verify_public replay` — reconstruct all 40 states and replay all four witnesses.
- `python -m repro.verify_public build-radius6 --cache <path>` — build/rebuild solved-side radius-6 authority and verify census checkpoints.
- `python -m repro.verify_public classify --cache <path> --ordinal N` — independently classify one ordinal.
- `python -m repro.verify_public classify-all --cache <path>` — independently test all 40 V1 classifications.
- `python -m repro.verify_public check-solution --ordinal N --moves "..."` — replay a proposed counterexample and report whether it solves and whether its HTM length would falsify the V1 classification.

Exit status contract:

- `0`: requested verification completed and all checked claims passed.
- `1`: a reproducible contradiction/counterexample was found.
- `2`: verification could not complete safely (bad input, invalid state, missing file, cache mismatch, resource/database failure, or interrupted/incomplete search).

The CLI prints human-readable output to stderr/stdout as appropriate and emits JSON with `--json`.

## Public evidence outputs

`repro/REPRODUCIBILITY.md` states exactly what is and is not reproduced.

`repro/PUBLIC_REPRO_MANIFEST.json` binds:

- benchmark ID;
- frozen ledger path and SHA-256;
- witness registry path and SHA-256;
- repro source file hashes;
- expected radius census checkpoints;
- claim ceiling;
- implementation/version identifier.

The manifest is generated only after tests pass. It must not copy the historical V1 final-seal verdict as a new independent result.

## Error handling and fail-closed behavior

The kit must stop without PASS for:

- unknown move token;
- sequence whose token count does not match the declared generator/witness length;
- invalid permutation/orientation/parity state;
- duplicated/missing ordinal;
- generator SHA mismatch;
- witness that does not solve;
- solved-radius census mismatch;
- cache metadata mismatch;
- interrupted or incomplete lower-bound search;
- a target-side search that exceeds the declared bound without exhaustive completion;
- any proposed counterexample that cannot be replayed exactly.

## Testing strategy

### Cubie model controls

- solved state validates;
- each of the 18 HTM moves is invertible;
- each quarter turn applied four times returns solved;
- each half turn applied twice returns solved;
- move + inverse returns solved;
- generated states preserve all cube invariants.

### Enumeration controls

- exact depth counts 18 / 243 / 3240;
- radius <=5 count 621649;
- radius <=6 count 8240087;
- repeated builds produce identical cache metadata and state-count result.

### Benchmark controls

- 40/40 generator records load and reconstruct;
- published exact-12 ordinals are exactly 7, 9, 20, 29;
- four published witnesses replay to solved;
- each 13-move generator is a valid upper bound;
- a deliberately shortened known-valid sequence is accepted when valid;
- malformed/non-solving counterexamples are rejected.

### Classification acceptance

Full `classify-all` PASS requires independently reproducing:

- 4 states with exact distance 12;
- 36 states with exact distance 13;
- no contradiction;
- all lower-bound searches complete exhaustively under the declared bound.

Anything less remains HOLD_PARTIAL_REPRODUCTION.

## Claim ceiling

Before full lower-bound reproduction:

`PUBLIC_STATE_RECONSTRUCTION_AND_4_OF_4_WITNESS_REPLAY_ONLY__NO_INDEPENDENT_EXACT13_LOWER_BOUND_PASS`

After successful full classify-all and fresh manifest/readback:

`INDEPENDENT_SELF_CONTAINED_REPRODUCTION_OF_EXACT_HTM_DISTANCES_FOR_THE_FROZEN_40_STANDARD_3X3_STATES_ONLY__NO_COMPLETE_3X3_DIAMETER_THEOREM__NO_GLOBAL_SOLVER_OPTIMALITY__NO_PHYSICAL_MIRROR_CUBE_VISION_OR_ROBOTICS_CLAIM`

## Release discipline

Development occurs on branch `repro-kit-v1`. No frozen V1 file is modified. The branch may open a review PR only after focused tests and the complete public verification command have produced evidence-backed results. Merge/release is a separate gate; no automatic merge, tag, release, Reddit post, or Hacker News submission occurs in this build gate.
