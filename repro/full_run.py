from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from .dataset import load_ledger
from .mitm import build_radius_cache, open_radius_cache
from .verify_public import classify_ordinal, _paths

SCHEMA = 'MC_F40_FULL_REPRO_SEMANTIC_RECEIPT_V1'
BENCHMARK_ID = 'MC-F40-EXACT-HTM-V1'


def logical_cache_digest(path: str | Path, required_radius: int = 6) -> str:
    path = Path(path)
    cache = open_radius_cache(path, required_radius=required_radius)
    cache.close()
    h = hashlib.sha256()
    con = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        for key, depth in con.execute('select k,depth from states order by k'):
            raw = bytes(key)
            h.update(len(raw).to_bytes(2, 'big'))
            h.update(raw)
            h.update(int(depth).to_bytes(1, 'big'))
    finally:
        con.close()
    return h.hexdigest()


def make_semantic_receipt(*, cache_digest: str, radius: int, state_count: int, classification_results: list[dict]) -> dict:
    results = sorted((dict(r) for r in classification_results), key=lambda r: int(r['ordinal']))
    contradictions = [r for r in results if r.get('status') == 'CONTRADICTION']
    incomplete = [r for r in results if r.get('status') not in {'CONFIRMED', 'CONTRADICTION'}]
    confirmed = [r for r in results if r.get('status') == 'CONFIRMED']
    exact12 = sum(1 for r in confirmed if r.get('exact_distance_htm') == 12)
    exact13 = sum(1 for r in confirmed if r.get('exact_distance_htm') == 13)
    status = 'PASS' if len(results) == 40 and len(confirmed) == 40 and not contradictions and not incomplete else ('CONTRADICTION' if contradictions else 'HOLD')
    return {
        'schema': SCHEMA,
        'benchmark_id': BENCHMARK_ID,
        'status': status,
        'radius': int(radius),
        'state_count': int(state_count),
        'logical_cache_sha256': cache_digest,
        'total': len(results),
        'confirmed': len(confirmed),
        'exact12': exact12,
        'exact13': exact13,
        'contradictions': contradictions,
        'incomplete': incomplete,
        'classification_results': results,
    }


def run(cache_path: str | Path, receipt_path: str | Path) -> dict:
    ledger_path, witness_path = _paths()
    build = build_radius_cache(cache_path, 6)
    cache = open_radius_cache(cache_path, 6)
    try:
        results = [classify_ordinal(i, ledger_path, witness_path, cache) for i in range(1, 41)]
    finally:
        cache.close()
    digest = logical_cache_digest(cache_path, 6)
    receipt = make_semantic_receipt(
        cache_digest=digest,
        radius=build['radius'],
        state_count=build['state_count'],
        classification_results=results,
    )
    # Fail closed if the public ledger no longer contains exactly the frozen 40.
    if len(load_ledger(ledger_path)) != 40:
        raise ValueError('public ledger no longer contains exactly 40 rows')
    out = Path(receipt_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
    return receipt


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog='python -m repro.full_run')
    p.add_argument('--cache', required=True)
    p.add_argument('--receipt', required=True)
    args = p.parse_args(argv)
    try:
        receipt = run(args.cache, args.receipt)
    except Exception as exc:
        print(json.dumps({'status': 'HOLD', 'error': str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    if receipt['status'] == 'CONTRADICTION':
        return 1
    return 0 if receipt['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
