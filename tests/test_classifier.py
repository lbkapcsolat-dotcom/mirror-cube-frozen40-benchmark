import tempfile, unittest
from pathlib import Path
from repro.cube import CubeState
from repro.mitm import build_radius_cache, open_radius_cache, iter_canonical_states_at_depth

class ClassifierTests(unittest.TestCase):
    def test_search_finds_depth4_target_and_excludes_it_at_bound3(self):
        from repro.verify_public import search_within_bound
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'r3.sqlite'; build_radius_cache(path,radius=3)
            cache=open_radius_cache(path,required_radius=3)
            try:
                target=None
                for s in iter_canonical_states_at_depth(CubeState.solved(),4):
                    if cache.distance(s) is None:
                        target=s; break
                self.assertIsNotNone(target)
                r3=search_within_bound(target,3,cache)
                self.assertFalse(r3.found); self.assertTrue(r3.exhaustive)
                r4=search_within_bound(target,4,cache)
                self.assertTrue(r4.found); self.assertTrue(r4.exhaustive)
                self.assertLessEqual(len(r4.solution),4)
                self.assertTrue(target.apply_sequence(r4.solution).is_solved())
            finally:
                cache.close()

    def test_solved_target_returns_empty_solution(self):
        from repro.verify_public import search_within_bound
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'r1.sqlite'; build_radius_cache(path,radius=1)
            cache=open_radius_cache(path,required_radius=1)
            try:
                result=search_within_bound(CubeState.solved(),0,cache)
                self.assertTrue(result.found); self.assertEqual(result.solution,())
            finally: cache.close()

if __name__=='__main__': unittest.main()
