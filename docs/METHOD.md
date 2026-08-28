# Method

## Metric and backend

The benchmark uses the standard 3x3 cubie state space and the Half Turn Metric (HTM): each face quarter-turn, inverse quarter-turn, or half-turn counts as one move.

## Frozen inputs

The benchmark contains exactly 40 deterministic 13-move candidate sequences. Their source JSON is included unchanged in `data/DEPTH13_CANDIDATE_POOL_V1.json`; its SHA-256 is bound by the final seal.

## Exact-distance rule

Every row is classified only after a lower bound and an upper bound meet.

- `EXACT12`: a verified 12-move target-to-solved witness exists, while predecessor lower-bound evidence excludes distance <=11.
- `EXACT13`: exhaustive predecessor evidence excludes solutions <=12, while the frozen 13-move generating sequence supplies an upper bound of 13.

The four exact-12 witnesses are preserved in `data/EXACT12_WITNESS_REGISTRY.json`.

## Proof routes

The detailed JSON ledger records the proof route per ordinal. Some earlier 16-state evidence was verified on an authorized remote Linux recovery host. Its hashes and classifications are bound in provenance, while this publication bundle explicitly does not claim current local byte custody for those historical predecessor files.

## Final counts

Exact 12: 4. Exact 13: 36. Total: 40.
