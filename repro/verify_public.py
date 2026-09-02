from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import argparse, json
from .cube import CubeState, MOVE_TOKENS, parse_moves
from .dataset import load_ledger, load_witnesses
from .mitm import build_radius_cache, open_radius_cache, iter_canonical_states_at_depth
from .replay import replay_public_inputs

@dataclass(frozen=True)
class SearchResult:
    found: bool
    exhaustive: bool
    bound: int
    solution: tuple[str,...] = ()
    target_depth: int | None = None
    solved_depth: int | None = None

def _path_to_solved(state: CubeState, cache) -> tuple[str,...]:
    distance=cache.distance(state)
    if distance is None:
        raise ValueError('intersection state absent from solved cache')
    path=[]; cur=state; d=distance
    while d:
        for move in MOVE_TOKENS:
            nxt=cur.apply(move)
            nd=cache.distance(nxt)
            if nd == d-1:
                path.append(move); cur=nxt; d=nd; break
        else:
            raise ValueError('cache has no descending path to solved')
    if not cur.is_solved():
        raise ValueError('descending cache path did not reach solved')
    return tuple(path)

def search_within_bound(target: CubeState, bound: int, cache, batch_size: int=400) -> SearchResult:
    if bound < 0:
        raise ValueError('bound must be non-negative')
    target.validate()
    max_target=max(0,bound-cache.radius)
    for depth in range(max_target+1):
        iterator=[(target,())] if depth==0 else iter_canonical_states_at_depth(target,depth,with_path=True)
        batch=[]
        for state,path in iterator:
            batch.append((state,path,state.key()))
            if len(batch)>=batch_size:
                hit=_find_hit(batch,depth,bound,cache,target)
                if hit is not None: return hit
                batch.clear()
        if batch:
            hit=_find_hit(batch,depth,bound,cache,target)
            if hit is not None: return hit
    return SearchResult(False,True,bound)

def _find_hit(batch, target_depth, bound, cache, original_target):
    hits=cache.distances([key for _state,_path,key in batch])
    for state,path,key in batch:
        solved_depth=hits.get(key)
        if solved_depth is None or target_depth+solved_depth>bound:
            continue
        solution=tuple(path)+_path_to_solved(state,cache)
        if len(solution)>bound or not original_target.apply_sequence(solution).is_solved():
            raise ValueError('MITM intersection failed replay')
        return SearchResult(True,True,bound,solution,target_depth,solved_depth)
    return None

def _inverse_move(move: str) -> str:
    if move.endswith('2'): return move
    if move.endswith("'"): return move[0]
    return move+"'"

def inverse_sequence(moves) -> tuple[str,...]:
    tokens=parse_moves(list(moves))
    return tuple(_inverse_move(m) for m in reversed(tokens))

def classify_ordinal(ordinal: int, ledger_path, witness_path, cache) -> dict:
    rows=load_ledger(ledger_path); witnesses=load_witnesses(witness_path)
    by_ord={r.ordinal:r for r in rows}
    if ordinal not in by_ord: raise ValueError(f'ordinal {ordinal} not found')
    row=by_ord[ordinal]
    target=CubeState.solved().apply_sequence(row.frozen_sequence_13)
    if row.exact_distance_htm==12:
        witness=witnesses.get(ordinal)
        if witness is None or witness.length!=12 or not target.apply_sequence(witness.moves).is_solved():
            raise ValueError(f'ordinal {ordinal}: upper-bound witness unavailable or invalid')
        upper=tuple(witness.moves)
    else:
        upper=inverse_sequence(row.frozen_sequence_13)
        if len(upper)!=13 or not target.apply_sequence(upper).is_solved():
            raise ValueError(f'ordinal {ordinal}: generator inverse failed upper-bound replay')
    lower_search=search_within_bound(target,row.exact_distance_htm-1,cache)
    if lower_search.found:
        return {'ordinal':ordinal,'status':'CONTRADICTION','claimed_exact':row.exact_distance_htm,'counterexample':list(lower_search.solution),'counterexample_length':len(lower_search.solution)}
    return {'ordinal':ordinal,'status':'CONFIRMED','exact_distance_htm':row.exact_distance_htm,'upper_bound_length':len(upper),'lower_bound_exhaustive_through':row.exact_distance_htm-1}

def check_solution(ordinal: int, moves, ledger_path) -> dict:
    rows=load_ledger(ledger_path); by_ord={r.ordinal:r for r in rows}
    if ordinal not in by_ord: raise ValueError(f'ordinal {ordinal} not found')
    row=by_ord[ordinal]; solution=tuple(parse_moves(moves))
    target=CubeState.solved().apply_sequence(row.frozen_sequence_13)
    if not target.apply_sequence(solution).is_solved():
        raise ValueError('proposed solution does not solve the target')
    status='CONTRADICTION' if len(solution)<row.exact_distance_htm else 'VALID_UPPER_BOUND'
    return {'ordinal':ordinal,'status':status,'claimed_exact':row.exact_distance_htm,'solution_length':len(solution),'solution':list(solution)}

def _paths():
    root=Path(__file__).resolve().parents[1]
    return root/'data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv', root/'data/EXACT12_WITNESS_REGISTRY.json'

def main(argv=None) -> int:
    ledger,witnesses=_paths()
    p=argparse.ArgumentParser(prog='python -m repro.verify_public')
    sub=p.add_subparsers(dest='command',required=True)
    rp=sub.add_parser('replay'); rp.add_argument('--json',action='store_true')
    bp=sub.add_parser('build-radius6'); bp.add_argument('--cache',required=True); bp.add_argument('--json',action='store_true')
    cp=sub.add_parser('classify'); cp.add_argument('--cache',required=True); cp.add_argument('--ordinal',type=int,required=True); cp.add_argument('--json',action='store_true')
    ap=sub.add_parser('classify-all'); ap.add_argument('--cache',required=True); ap.add_argument('--json',action='store_true')
    sp=sub.add_parser('check-solution'); sp.add_argument('--ordinal',type=int,required=True); sp.add_argument('--moves',required=True); sp.add_argument('--json',action='store_true')
    args=p.parse_args(argv)
    try:
        if args.command=='replay':
            result={'status':'PASS',**replay_public_inputs(ledger,witnesses,True)}
        elif args.command=='build-radius6':
            result={'status':'PASS',**build_radius_cache(args.cache,6)}
        elif args.command=='classify':
            cache=open_radius_cache(args.cache,6)
            try: result=classify_ordinal(args.ordinal,ledger,witnesses,cache)
            finally: cache.close()
        elif args.command=='classify-all':
            cache=open_radius_cache(args.cache,6)
            try:
                results=[classify_ordinal(i,ledger,witnesses,cache) for i in range(1,41)]
            finally: cache.close()
            contradictions=[r for r in results if r['status']=='CONTRADICTION']
            result={'status':'CONTRADICTION' if contradictions else 'PASS','total':40,'confirmed':40-len(contradictions),'contradictions':contradictions,'results':results}
        else:
            result=check_solution(args.ordinal,args.moves,ledger)
    except Exception as exc:
        print(json.dumps({'status':'HOLD','error':str(exc)},sort_keys=True) if getattr(args,'json',False) else f'HOLD: {exc}')
        return 2
    if getattr(args,'json',False): print(json.dumps(result,sort_keys=True))
    else: print(json.dumps(result,indent=2,sort_keys=True))
    return 1 if result.get('status')=='CONTRADICTION' else 0

if __name__=='__main__':
    raise SystemExit(main())
