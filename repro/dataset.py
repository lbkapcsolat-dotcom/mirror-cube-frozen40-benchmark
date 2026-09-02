from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv, hashlib, json
from .cube import parse_moves

@dataclass(frozen=True)
class BenchmarkRow:
    ordinal:int
    exact_distance_htm:int
    classification:str
    frozen_sequence_13:tuple[str,...]
    frozen_sequence_sha256:str
    proof_route:str

@dataclass(frozen=True)
class Witness:
    ordinal:int
    moves:tuple[str,...]
    length:int
    replay_status:str

def canonical_sequence_sha256(moves) -> str:
    tokens=parse_moves(list(moves))
    payload=json.dumps(tokens,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def load_ledger(path: str | Path) -> list[BenchmarkRow]:
    rows=[]; seen=set()
    with open(path,newline='',encoding='utf-8') as f:
        for raw in csv.DictReader(f):
            ordinal=int(raw['ordinal'])
            if ordinal in seen: raise ValueError(f'duplicate ordinal {ordinal}')
            seen.add(ordinal)
            moves=tuple(parse_moves(raw['frozen_sequence_13']))
            if len(moves)!=13: raise ValueError(f'ordinal {ordinal}: generator length != 13')
            expected=raw['frozen_sequence_sha256'].lower()
            actual=canonical_sequence_sha256(moves)
            if actual!=expected: raise ValueError(f'ordinal {ordinal}: generator sha256 mismatch')
            distance=int(raw['exact_distance_htm'])
            classification=raw['classification']
            if classification not in ('EXACT12','EXACT13') or distance not in (12,13) or classification != f'EXACT{distance}':
                raise ValueError(f'ordinal {ordinal}: inconsistent classification')
            rows.append(BenchmarkRow(ordinal,distance,classification,moves,expected,raw['proof_route']))
    rows.sort(key=lambda r:r.ordinal)
    return rows

def load_witnesses(path: str | Path) -> dict[int,Witness]:
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    out={}
    for raw in data['witnesses']:
        ordinal=int(raw['ordinal'])
        if ordinal in out: raise ValueError(f'duplicate witness ordinal {ordinal}')
        moves=tuple(parse_moves(raw['moves']))
        length=int(raw['length'])
        if length != len(moves): raise ValueError(f'ordinal {ordinal}: witness length mismatch')
        out[ordinal]=Witness(ordinal,moves,length,raw.get('replay_status',''))
    if int(data.get('count',len(out))) != len(out): raise ValueError('witness count mismatch')
    if sorted(map(int,data.get('ordinals',out))) != sorted(out): raise ValueError('witness ordinal registry mismatch')
    return out
