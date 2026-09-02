import sqlite3, tempfile, unittest
from pathlib import Path
from repro.cube import CubeState

class MitmTests(unittest.TestCase):
    def test_canonical_tree_counts_match_known_controls(self):
        from repro.mitm import canonical_state_count
        self.assertEqual([canonical_state_count(d) for d in (1,2,3)],[18,243,3240])

    def test_small_cache_has_exact_radius3_unique_count(self):
        from repro.mitm import build_radius_cache, open_radius_cache
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'r3.sqlite'
            result=build_radius_cache(path, radius=3)
            self.assertEqual(result['state_count'],3502)
            cache=open_radius_cache(path, required_radius=3)
            try:
                self.assertEqual(cache.distance(CubeState.solved()),0)
                self.assertEqual(cache.distance(CubeState.solved().apply('R')),1)
            finally:
                cache.close()

    def test_incomplete_cache_is_rejected(self):
        from repro.mitm import open_radius_cache, CACHE_SCHEMA
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'bad.sqlite'
            con=sqlite3.connect(path)
            con.execute('create table metadata (k text primary key, v text not null)')
            for k,v in {'schema':CACHE_SCHEMA,'status':'BUILDING','radius':'3','move_convention':'STANDARD_3X3_HTM_URFDLB'}.items():
                con.execute('insert into metadata values (?,?)',(k,v))
            con.execute('create table states (k blob primary key, depth integer not null)')
            con.commit(); con.close()
            with self.assertRaisesRegex(ValueError,'not COMPLETE'):
                open_radius_cache(path, required_radius=3)

if __name__=='__main__': unittest.main()
