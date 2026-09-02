from __future__ import annotations
import argparse, json
from pathlib import Path
from .cube import CubeState
from .dataset import load_ledger, load_witnesses

EXPECTED_EXACT12={7,9,20,29}

def replay_public_inputs(ledger_path: str | Path, witness_path: str | Path, require_frozen40: bool=True) -> dict:
    rows=load_ledger(ledger_path)
    witnesses=load_witnesses(witness_path)
    if require_frozen40:
        ordinals=[r.ordinal for r in rows]
        if ordinals != list(range(1,41)):
            raise ValueError('frozen40 ledger must contain ordinals 1..40 exactly once')
        exact12={r.ordinal for r in rows if r.classification=='EXACT12'}
        if exact12 != EXPECTED_EXACT12:
            raise ValueError(f'unexpected exact12 ordinals: {sorted(exact12)}')
        if set(witnesses) != EXPECTED_EXACT12:
            raise ValueError(f'unexpected witness ordinals: {sorted(witnesses)}')
    witness_pass=0
    for row in rows:
        target=CubeState.solved().apply_sequence(row.frozen_sequence_13)
        target.validate()
        witness=witnesses.get(row.ordinal)
        if witness is not None:
            if witness.length != 12:
                raise ValueError(f'ordinal {row.ordinal}: published exact12 witness length != 12')
            if not target.apply_sequence(witness.moves).is_solved():
                raise ValueError(f'ordinal {row.ordinal}: witness replay did not solve')
            witness_pass += 1
    return {
        'states':len(rows),
        'exact12':sum(r.classification=='EXACT12' for r in rows),
        'exact13':sum(r.classification=='EXACT13' for r in rows),
        'witness_replay_pass':witness_pass,
        'claim_ceiling':'PUBLIC_STATE_RECONSTRUCTION_AND_4_OF_4_WITNESS_REPLAY_ONLY__NO_INDEPENDENT_EXACT13_LOWER_BOUND_PASS',
    }

def main(argv=None) -> int:
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser()
    p.add_argument('--ledger',default=str(root/'data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv'))
    p.add_argument('--witnesses',default=str(root/'data/EXACT12_WITNESS_REGISTRY.json'))
    p.add_argument('--json',action='store_true')
    args=p.parse_args(argv)
    try:
        result=replay_public_inputs(args.ledger,args.witnesses,True)
    except Exception as exc:
        if args.json:
            print(json.dumps({'status':'HOLD','error':str(exc)},sort_keys=True))
        else:
            print(f'HOLD: {exc}')
        return 2
    if args.json:
        print(json.dumps({'status':'PASS',**result},sort_keys=True))
    else:
        print(f"PASS states={result['states']} exact12={result['exact12']} exact13={result['exact13']} witness_replay={result['witness_replay_pass']}/4")
        print(result['claim_ceiling'])
    return 0

if __name__=='__main__':
    raise SystemExit(main())
