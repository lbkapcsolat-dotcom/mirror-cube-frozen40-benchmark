from __future__ import annotations
from dataclasses import dataclass
from math import factorial

MOVE_TOKENS = tuple(f+s for f in 'URFDLB' for s in ('', "'", '2'))
_BASE = {
'U': ((3,0,1,2,4,5,6,7),(0,0,0,0,0,0,0,0),(3,0,1,2,4,5,6,7,8,9,10,11),(0,)*12),
'R': ((4,1,2,0,7,5,6,3),(2,0,0,1,1,0,0,2),(8,1,2,3,11,5,6,7,4,9,10,0),(0,)*12),
'F': ((1,5,2,3,0,4,6,7),(1,2,0,0,2,1,0,0),(0,9,2,3,4,8,6,7,1,5,10,11),(0,1,0,0,0,1,0,0,1,1,0,0)),
'D': ((0,1,2,3,5,6,7,4),(0,0,0,0,0,0,0,0),(0,1,2,3,5,6,7,4,8,9,10,11),(0,)*12),
'L': ((0,2,6,3,4,1,5,7),(0,1,2,0,0,2,1,0),(0,1,10,3,4,5,9,7,8,2,6,11),(0,)*12),
'B': ((0,1,3,7,4,5,2,6),(0,0,1,2,0,0,2,1),(0,1,2,11,4,5,6,10,8,9,3,7),(0,0,0,1,0,0,0,1,0,0,1,1)),
}

def parse_moves(text: str | list[str] | tuple[str, ...]) -> list[str]:
    toks = text.split() if isinstance(text, str) else list(text)
    for token in toks:
        if token not in MOVE_TOKENS:
            raise ValueError(f'unknown move: {token}')
    return toks

def _parity(p: tuple[int, ...]) -> int:
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p))) & 1

def _rank_perm(p: tuple[int, ...]) -> int:
    n=len(p); rank=0
    for i in range(n-1):
        smaller=sum(p[j] < p[i] for j in range(i+1,n))
        rank += smaller * factorial(n-1-i)
    return rank

def _unrank_perm(rank: int, n: int) -> tuple[int, ...]:
    if rank < 0 or rank >= factorial(n):
        raise ValueError('permutation rank out of range')
    items=list(range(n)); out=[]
    for i in range(n):
        f=factorial(n-1-i)
        idx=rank // f
        rank=rank % f
        out.append(items.pop(idx))
    return tuple(out)

def _encode_base(values: tuple[int, ...], base: int) -> int:
    out=0
    for value in values:
        out=out*base+value
    return out

def _decode_base(value: int, length: int, base: int) -> tuple[int, ...]:
    out=[0]*length
    for i in range(length-1,-1,-1):
        out[i]=value%base; value//=base
    if value:
        raise ValueError('coordinate out of range')
    return tuple(out)

@dataclass(frozen=True, slots=True)
class CubeState:
    cp: tuple[int, ...] = tuple(range(8))
    co: tuple[int, ...] = (0,)*8
    ep: tuple[int, ...] = tuple(range(12))
    eo: tuple[int, ...] = (0,)*12

    @classmethod
    def solved(cls) -> 'CubeState':
        return cls()

    def validate(self) -> None:
        if sorted(self.cp) != list(range(8)) or sorted(self.ep) != list(range(12)):
            raise ValueError('invalid permutation')
        if len(self.co)!=8 or any(x not in (0,1,2) for x in self.co) or sum(self.co)%3:
            raise ValueError('invalid corner orientation')
        if len(self.eo)!=12 or any(x not in (0,1) for x in self.eo) or sum(self.eo)%2:
            raise ValueError('invalid edge orientation')
        if _parity(self.cp) != _parity(self.ep):
            raise ValueError('parity mismatch')

    def _quarter(self, face: str) -> 'CubeState':
        mcp,mco,mep,meo=_BASE[face]
        return CubeState(
            tuple(self.cp[mcp[i]] for i in range(8)),
            tuple((self.co[mcp[i]]+mco[i])%3 for i in range(8)),
            tuple(self.ep[mep[i]] for i in range(12)),
            tuple((self.eo[mep[i]]+meo[i])%2 for i in range(12)),
        )

    def apply(self, move: str) -> 'CubeState':
        parse_moves([move])
        turns=2 if move.endswith('2') else 3 if move.endswith("'") else 1
        state=self
        for _ in range(turns):
            state=state._quarter(move[0])
        return state

    def apply_sequence(self, sequence: str | list[str] | tuple[str, ...]) -> 'CubeState':
        state=self
        for move in parse_moves(sequence):
            state=state.apply(move)
        return state

    def is_solved(self) -> bool:
        return self == CubeState.solved()

    def key(self) -> bytes:
        self.validate()
        corner_ori=_encode_base(self.co[:7],3)
        edge_ori=_encode_base(self.eo[:11],2)
        corner_coord=_rank_perm(self.cp)*2187+corner_ori
        edge_coord=_rank_perm(self.ep)*2048+edge_ori
        return corner_coord.to_bytes(4,'big') + edge_coord.to_bytes(5,'big')

    @classmethod
    def from_key(cls, key: bytes) -> 'CubeState':
        if len(key)!=9:
            raise ValueError('cube key must be exactly 9 bytes')
        corner_coord=int.from_bytes(key[:4],'big')
        edge_coord=int.from_bytes(key[4:],'big')
        corner_perm_rank, corner_ori=divmod(corner_coord,2187)
        edge_perm_rank, edge_ori=divmod(edge_coord,2048)
        co7=_decode_base(corner_ori,7,3)
        eo11=_decode_base(edge_ori,11,2)
        state=cls(
            _unrank_perm(corner_perm_rank,8),
            co7+((-sum(co7))%3,),
            _unrank_perm(edge_perm_rank,12),
            eo11+((-sum(eo11))%2,),
        )
        state.validate()
        return state
