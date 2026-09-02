from __future__ import annotations
from pathlib import Path
import sqlite3
from .cube import CubeState

CACHE_SCHEMA='MC_F40_RADIUS_CACHE_V1'
MOVE_CONVENTION='STANDARD_3X3_HTM_URFDLB'
FACES='URFDLB'
SUFFIXES=('',"'",'2')
OPPOSITE={'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}
FACE_ORDER={f:i for i,f in enumerate(FACES)}
KNOWN_EXACT={1:18,2:243,3:3240}
KNOWN_RADIUS={3:3502,5:621649,6:8240087}
KNOWN_CANONICAL_RADIUS6=8331112

def _allowed(prev_face: str | None, face: str) -> bool:
    if prev_face == face:
        return False
    if prev_face and OPPOSITE[prev_face] == face and FACE_ORDER[prev_face] > FACE_ORDER[face]:
        return False
    return True

def canonical_state_count(depth: int) -> int:
    if depth < 0:
        raise ValueError('depth must be non-negative')
    if depth == 0:
        return 1
    counts={None:1}
    for _ in range(depth):
        nxt={f:0 for f in FACES}
        for prev,n in counts.items():
            for face in FACES:
                if _allowed(prev,face):
                    nxt[face]+=n*3
        counts=nxt
    return sum(counts.values())

def iter_canonical_states_at_depth(start: CubeState, depth: int, with_path: bool=False):
    if depth < 0:
        raise ValueError('depth must be non-negative')
    stack=[(start,None,0,())]
    while stack:
        state,prev,level,path=stack.pop()
        if level == depth:
            yield (state,path) if with_path else state
            continue
        for face in reversed(FACES):
            if not _allowed(prev,face):
                continue
            for suffix in reversed(SUFFIXES):
                move=face+suffix
                ns=state.apply(move)
                stack.append((ns,face,level+1,path+(move,)))

def _set_meta(con, key, value):
    con.execute('insert or replace into metadata(k,v) values (?,?)',(key,str(value)))

def _metadata(con):
    try:
        return dict(con.execute('select k,v from metadata'))
    except sqlite3.Error as exc:
        raise ValueError(f'invalid cache metadata: {exc}') from exc

def build_radius_cache(path: str | Path, radius: int=6, batch_size: int=5000) -> dict:
    if radius < 0 or radius > 6:
        raise ValueError('radius must be between 0 and 6')
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        cache=open_radius_cache(path,required_radius=radius)
        try:
            return {'radius':cache.radius,'state_count':cache.state_count,'status':'COMPLETE','reused':True}
        finally:
            cache.close()
    con=sqlite3.connect(path)
    try:
        con.execute('pragma journal_mode=WAL')
        con.execute('pragma synchronous=NORMAL')
        con.execute('create table metadata (k text primary key, v text not null)')
        con.execute('create table states (k blob primary key, depth integer not null) without rowid')
        _set_meta(con,'schema',CACHE_SCHEMA)
        _set_meta(con,'status','BUILDING')
        _set_meta(con,'radius',radius)
        _set_meta(con,'move_convention',MOVE_CONVENTION)
        _set_meta(con,'canonical_pruning','NO_SAME_FACE__OPPOSITE_FACE_ASCENDING')
        con.execute('insert into states(k,depth) values (?,0)',(sqlite3.Binary(CubeState.solved().key()),))
        con.commit()
        for depth in range(1,radius+1):
            batch=[]
            con.execute('begin')
            for state in iter_canonical_states_at_depth(CubeState.solved(),depth):
                batch.append((sqlite3.Binary(state.key()),depth))
                if len(batch)>=batch_size:
                    con.executemany('insert or ignore into states(k,depth) values (?,?)',batch); batch.clear()
            if batch:
                con.executemany('insert or ignore into states(k,depth) values (?,?)',batch)
            con.commit()
            exact=con.execute('select count(*) from states where depth=?',(depth,)).fetchone()[0]
            total=con.execute('select count(*) from states').fetchone()[0]
            _set_meta(con,f'exact_depth_{depth}',exact)
            _set_meta(con,f'radius_{depth}',total)
            con.commit()
            if depth in KNOWN_EXACT and exact != KNOWN_EXACT[depth]:
                raise ValueError(f'exact depth {depth} census mismatch: {exact} != {KNOWN_EXACT[depth]}')
            if depth in KNOWN_RADIUS and total != KNOWN_RADIUS[depth]:
                raise ValueError(f'radius {depth} census mismatch: {total} != {KNOWN_RADIUS[depth]}')
        total=con.execute('select count(*) from states').fetchone()[0]
        if radius == 6:
            canonical_total=sum(canonical_state_count(d) for d in range(7))
            if canonical_total != KNOWN_CANONICAL_RADIUS6:
                raise ValueError(f'canonical radius6 tree mismatch: {canonical_total} != {KNOWN_CANONICAL_RADIUS6}')
            _set_meta(con,'canonical_tree_nodes_radius6',canonical_total)
        _set_meta(con,'state_count',total)
        _set_meta(con,'status','COMPLETE')
        con.commit()
        return {'radius':radius,'state_count':total,'status':'COMPLETE','reused':False}
    finally:
        con.close()

class RadiusCache:
    def __init__(self, path: Path, con: sqlite3.Connection, meta: dict[str,str]):
        self.path=path; self.con=con; self.meta=meta
        self.radius=int(meta['radius']); self.state_count=int(meta['state_count'])
    def distance(self, state_or_key):
        key=state_or_key.key() if isinstance(state_or_key,CubeState) else state_or_key
        row=self.con.execute('select depth from states where k=?',(sqlite3.Binary(key),)).fetchone()
        return None if row is None else int(row[0])
    def distances(self, keys):
        keys=list(keys)
        if not keys: return {}
        out={}; chunk=400
        for i in range(0,len(keys),chunk):
            part=keys[i:i+chunk]
            sql='select k,depth from states where k in (%s)' % ','.join('?'*len(part))
            for k,d in self.con.execute(sql,[sqlite3.Binary(k) for k in part]):
                out[bytes(k)]=int(d)
        return out
    def close(self):
        self.con.close()

def open_radius_cache(path: str | Path, required_radius: int=6) -> RadiusCache:
    path=Path(path)
    if not path.exists():
        raise ValueError('radius cache does not exist')
    con=sqlite3.connect(f'file:{path}?mode=ro',uri=True)
    try:
        meta=_metadata(con)
        if meta.get('schema') != CACHE_SCHEMA:
            raise ValueError('cache schema mismatch')
        if meta.get('status') != 'COMPLETE':
            raise ValueError('cache is not COMPLETE')
        if meta.get('move_convention') != MOVE_CONVENTION:
            raise ValueError('cache move convention mismatch')
        radius=int(meta.get('radius','-1'))
        if radius < required_radius:
            raise ValueError(f'cache radius {radius} < required {required_radius}')
        count=con.execute('select count(*) from states').fetchone()[0]
        if int(meta.get('state_count','-1')) != count:
            raise ValueError('cache state_count mismatch')
        if radius in KNOWN_RADIUS and count != KNOWN_RADIUS[radius]:
            raise ValueError(f'cache radius census mismatch for radius {radius}')
        return RadiusCache(path,con,meta)
    except Exception:
        con.close(); raise
