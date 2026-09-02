# MIRROR_CUBE_SELF_CONTAINED_PUBLIC_REPRO_KIT_V1 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standard-library Python reproduction kit that independently reconstructs the frozen 40 states, replays the four 12-move witnesses, recomputes radius-6 search authority, and independently verifies the 12/13 exact HTM classifications without mutating frozen V1 artifacts.

**Architecture:** A small immutable cubie engine provides deterministic HTM state transitions and canonical keys. A dataset/replay layer consumes only public benchmark files. A disk-backed SQLite 6+6 meet-in-the-middle engine recomputes the lower-bound search from scratch, while a CLI exposes replay, radius build, single/all classification, and counterexample checking with fail-closed exit codes.

**Tech Stack:** Python 3 standard library (`dataclasses`, `csv`, `json`, `hashlib`, `sqlite3`, `argparse`, `unittest`); GitHub branch `repro-kit-v1`.

## Global Constraints

- Frozen V1 benchmark files, witnesses, classifications, seals, and lock stay untouched.
- No network dependency, API key, paid service, finite credit, or hidden binary.
- PASS requires fresh computation; historical hashes are provenance only.
- Unknown/malformed/incomplete/resource-failed work returns HOLD semantics, never PASS.
- Exact-12 requires upper bound 12 plus exhaustive no-solution <=11.
- Exact-13 requires upper bound 13 plus exhaustive no-solution <=12.
- Scope remains only the frozen 40 standard-3x3 HTM states.

---

### Task 1: Cubie engine and public dataset replay

**Files:**
- Create: `repro/__init__.py`
- Create: `repro/cube.py`
- Create: `repro/dataset.py`
- Create: `repro/replay.py`
- Create: `tests/test_cube.py`
- Create: `tests/test_replay.py`

**Interfaces:**
- Consumes: `data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv`, `data/EXACT12_WITNESS_REGISTRY.json`
- Produces: `CubeState`, `parse_moves`, `load_benchmark`, `replay_public_inputs`

- [ ] **Step 1: Add the focused failing tests**

Tests must assert: solved validates; U/R/F/D/L/B quarter-turn^4 identity; move+inverse identity; X2 twice identity; unknown move rejected; 40 ledger rows load uniquely; exact-12 ordinals equal `{7,9,20,29}`; all generators are 13 HTM tokens; all four witnesses are 12 tokens and solve their corresponding generated states.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.test_cube tests.test_replay -v`
Expected: non-zero exit because `repro.cube` / replay interfaces do not exist.

- [ ] **Step 3: Implement the minimum behavior**

Implement a deterministic standard cubie representation with 8-corner permutation/orientation and 12-edge permutation/orientation, the 18 HTM moves, state validation, canonical compact key, sequence parser/application, CSV/JSON loading, generator reconstruction, and witness replay. Reject invalid token, duplicate ordinal, declared-length mismatch, invalid state, and generator hash mismatch.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.test_cube tests.test_replay -v`
Expected: all Task-1 tests pass; 40/40 generators valid and 4/4 witnesses solve.

- [ ] **Step 5: Run the affected integration check**

Run: `python -m repro.replay`
Expected: deterministic summary with `states=40`, `exact12=4`, `exact13=36`, `witness_replay=4/4 PASS`, and no exact lower-bound PASS claim.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add repro/__init__.py repro/cube.py repro/dataset.py repro/replay.py tests/test_cube.py tests/test_replay.py
git commit -m "feat: add public cube replay engine"
```

### Task 2: Radius-6 authority builder and census controls

**Files:**
- Create: `repro/mitm.py`
- Create: `tests/test_mitm.py`

**Interfaces:**
- Consumes: `CubeState.key()`, 18 HTM moves
- Produces: `build_radius_cache(path)`, `open_radius_cache(path)`, `enumerate_exact_depth(depth)`

- [ ] **Step 1: Add the focused failing tests**

Tests assert exact depth counts 18, 243, 3240 for depths 1..3; cache metadata rejects wrong engine/schema/move convention; interrupted/incomplete cache cannot be opened as authority; a complete small-radius cache records minimum distances exactly.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.test_mitm -v`
Expected: non-zero exit because the MITM/cache module is absent.

- [ ] **Step 3: Implement the minimum behavior**

Implement deterministic breadth-first enumeration from solved with same-face canonical pruning and visited-state deduplication. Persist canonical state keys plus minimum depth in SQLite. Use transactional checkpoint metadata: `status=BUILDING` during enumeration and change to `COMPLETE` only after expected counts and integrity checks pass. A reused cache must match schema, engine version, move convention, maximum radius, row count, and completion marker.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.test_mitm -v`
Expected: all focused shallow/cache tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python -m repro.verify_public build-radius6 --cache .repro-cache/radius6.sqlite`
Expected: successful exhaustive build with checkpoints `depth1=18`, `depth2=243`, `depth3=3240`, `radius5=621649`, `radius6=8240087`, then cache status `COMPLETE`. Any mismatch returns exit 2 and leaves no authoritative COMPLETE cache.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add repro/mitm.py tests/test_mitm.py
git commit -m "feat: add deterministic radius6 authority"
```

### Task 3: Exact classifier and counterexample verifier

**Files:**
- Create: `repro/verify_public.py`
- Create: `tests/test_classifier.py`

**Interfaces:**
- Consumes: public benchmark records, complete radius-6 cache, cubie engine
- Produces: `classify_ordinal`, `classify_all`, `check_solution`; CLI exit codes 0/1/2

- [ ] **Step 1: Add the focused failing tests**

Tests assert: a known published 12-move witness is accepted as a solving upper bound; non-solving sequence is rejected; malformed move gives exit 2; a synthetic shallow target is correctly found within bound; a synthetic target outside a tested shallow bound returns exhaustive `NO_SOLUTION_WITHIN_BOUND`; incomplete cache yields HOLD/exit 2; contradiction result yields exit 1; ordinary confirmed classification yields exit 0.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.test_classifier -v`
Expected: non-zero exit because classifier/CLI interfaces are absent.

- [ ] **Step 3: Implement the minimum behavior**

For a requested bound, enumerate target-side states through the necessary complementary depth and query solved-side minimum distances from the COMPLETE cache. Treat an intersection as a solution only when `target_depth + solved_depth <= bound`. Exhaustive completion with no qualifying intersection proves no solution within that bound. Apply bound 11 to V1 exact-12 ordinals and bound 12 to V1 exact-13 ordinals. Replay any found path before returning contradiction. Implement CLI commands and exact exit-status contract.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest tests.test_classifier -v`
Expected: all classifier/counterexample/exit-code tests pass.

- [ ] **Step 5: Run the affected integration check**

Run: `python -m repro.verify_public classify-all --cache .repro-cache/radius6.sqlite --json`
Expected for full gate PASS: `total=40`, `exact12=4`, `exact13=36`, `contradictions=0`, `incomplete=0`. Any counterexample returns exit 1; any incomplete search/cache/resource failure returns exit 2.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add repro/verify_public.py tests/test_classifier.py
git commit -m "feat: independently classify frozen40 states"
```

### Task 4: Public reproducibility contract, manifest, and review gate

**Files:**
- Create: `repro/REPRODUCIBILITY.md`
- Create: `repro/PUBLIC_REPRO_MANIFEST.json`
- Create: `tests/test_manifest.py`
- Create: `.github/workflows/repro-kit.yml`

**Interfaces:**
- Consumes: passing source/tests and public benchmark files
- Produces: hash-bound public repro manifest, documented commands, CI replay/shallow tests; full radius-6/classify-all remains a deliberate heavier local reproduction command unless runtime budget proves suitable for CI.

- [ ] **Step 1: Add the focused failing test**

Manifest test asserts every declared source/input path exists, SHA-256 matches checked-in bytes, benchmark ID is correct, claim ceiling is explicit, radius census expectations are present, and frozen V1 files are not listed as modified outputs.

- [ ] **Step 2: Verify the relevant failure**

Run: `python -m unittest tests.test_manifest -v`
Expected: non-zero exit because manifest/docs do not yet exist.

- [ ] **Step 3: Implement the minimum behavior**

Document quick witness replay, radius-cache build, single classification, all-40 classification, and counterexample submission. Generate the manifest from actual branch bytes only after source/test state is stable. CI runs unit tests plus public replay and shallow enumeration; it must never label skipped heavy lower-bound work as PASS.

- [ ] **Step 4: Verify the focused pass**

Run: `python -m unittest discover -s tests -v`
Expected: all tests pass.

- [ ] **Step 5: Run the affected integration check**

Run sequentially:

`python -m repro.verify_public replay`

`python -m repro.verify_public build-radius6 --cache .repro-cache/radius6.sqlite`

`python -m repro.verify_public classify-all --cache .repro-cache/radius6.sqlite --json`

Expected final gate PASS only if the radius census matches and all 40 classifications independently reproduce with zero contradiction/incomplete result. Then perform GitHub branch readback of all new files and compare hashes to `PUBLIC_REPRO_MANIFEST.json`.

- [ ] **Step 6: Commit the passing deliverable**

```bash
git add repro/REPRODUCIBILITY.md repro/PUBLIC_REPRO_MANIFEST.json tests/test_manifest.py .github/workflows/repro-kit.yml
git commit -m "docs: seal public repro contract"
```

## Externally observable decisions

All externally observable behavior is fixed by the design: standard-library-only implementation; SQLite disk-backed radius cache; exit codes 0/1/2; no mutation of frozen V1; no automatic merge/release/community post; full PASS requires independent lower-bound completion for all 40. No unresolved product decision remains for implementation.
