# Method

## Metric and backend

Tensor uses the standard 3x3 cubie state space and the Half Turn Metric (HTM): each face quarter-turn, inverse quarter-turn, or half-turn counts as one move.

## Frozen inputs

The benchmark contains exactly 40 deterministic 13-move candidate sequences. The frozen sequences are preserved in `data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv`, with row-level SHA-256 values for integrity checking.

## Exact-distance rule

Every row is classified only after a lower bound and an upper bound meet.

- `EXACT12`: a verified 12-move target-to-solved witness exists, while predecessor lower-bound evidence excludes distance <=11.
- `EXACT13`: exhaustive predecessor evidence excludes solutions <=12, while the frozen 13-move generating sequence supplies an upper bound of 13.

The four exact-12 witnesses are preserved in `data/EXACT12_WITNESS_REGISTRY.json`.

## Proof routes

The ledger records the proof route per ordinal. Some predecessor evidence was verified on an authorized remote recovery host. Historical evidence remains preserved by repository history; the current public surface does not claim local byte custody for those predecessor files.

## Final counts

Exact 12: 4. Exact 13: 36. Total: 40.
