# Public reproduction kit

This directory is a sidecar reproduction layer for **MC-F40-EXACT-HTM-V1**. It does not modify or replace the frozen V1 benchmark files.

## What can be checked quickly

Run:

```bash
python -m unittest discover -s tests -v
python -m repro.verify_public replay --json
```

The replay command:

1. reads the checked-in 40-row CSV;
2. verifies each 13-move generator against the published compact-JSON SHA-256 convention;
3. reconstructs all 40 target states with an independent cubie implementation;
4. replays the four public 12-move witnesses for ordinals 7, 9, 20 and 29.

A replay PASS proves state reconstruction and the four published upper bounds. It does **not** by itself prove that no shorter solution exists.

## Independent lower-bound reproduction

Build a solved-side radius-6 authority:

```bash
python -m repro.verify_public build-radius6 --cache .repro-cache/radius6.sqlite --json
```

The builder fails closed unless the independently generated search agrees with these controls:

- exact depth 1: 18 states;
- exact depth 2: 243 states;
- exact depth 3: 3240 states;
- unique radius <=5: 621649 states;
- unique radius <=6: 8240087 states;
- canonical sequence-tree nodes through depth 6: 8331112.

The cache is marked `COMPLETE` only after all applicable checks pass. Interrupted, mismatched or incomplete databases are rejected as authority.

Then classify one state:

```bash
python -m repro.verify_public classify --cache .repro-cache/radius6.sqlite --ordinal 7 --json
```

Or all 40:

```bash
python -m repro.verify_public classify-all --cache .repro-cache/radius6.sqlite --json
```

For an `EXACT12` row the verifier searches exhaustively for any solution of length <=11. For an `EXACT13` row it searches exhaustively for any solution of length <=12. A found shorter solution is replayed before it is reported as a contradiction.

## Test a proposed counterexample

```bash
python -m repro.verify_public check-solution --ordinal 7 --moves "..." --json
```

Exit codes:

- `0`: requested verification completed without contradiction;
- `1`: a replayable shorter counterexample contradicts the frozen classification;
- `2`: verification could not complete safely or the input/cache is invalid.

## Current claim boundary

Until a fresh full radius-6 build and `classify-all` run complete, the supported new claim is:

`PUBLIC_STATE_RECONSTRUCTION_AND_4_OF_4_WITNESS_REPLAY_ONLY__NO_INDEPENDENT_EXACT13_LOWER_BOUND_PASS`

Only after the full lower-bound run succeeds may the sidecar layer claim independent reproduction of the exact HTM distances for these 40 frozen states. Even then it does not establish the complete 3x3 diameter, global solver optimality, physical Mirror Cube perception, or robotics capability.

## Frozen V1 discipline

A genuine counterexample does not rewrite V1 in place. It opens a new benchmark-version/adjudication gate while preserving the frozen historical artifact.
