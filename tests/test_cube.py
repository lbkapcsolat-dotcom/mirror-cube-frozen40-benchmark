import unittest
from repro.cube import CubeState, MOVE_TOKENS, parse_moves

class CubeTests(unittest.TestCase):
    def test_solved_validates(self):
        self.assertIsNone(CubeState.solved().validate())

    def test_quarter_turn_fourth_power_identity(self):
        for face in 'URFDLB':
            with self.subTest(face=face):
                self.assertTrue(CubeState.solved().apply_sequence([face]*4).is_solved())

    def test_move_inverse_identity(self):
        for face in 'URFDLB':
            with self.subTest(face=face):
                self.assertTrue(CubeState.solved().apply_sequence([face, face+"'"]).is_solved())

    def test_half_turn_square_identity(self):
        for face in 'URFDLB':
            with self.subTest(face=face):
                self.assertTrue(CubeState.solved().apply_sequence([face+'2', face+'2']).is_solved())

    def test_unknown_move_rejected(self):
        with self.assertRaises(ValueError):
            parse_moves('X')

    def test_key_round_trip(self):
        state = CubeState.solved().apply_sequence("R U2 F' L D2 B")
        self.assertEqual(state, CubeState.from_key(state.key()))

    def test_shallow_exact_counts(self):
        seen={CubeState.solved().key()}
        frontier={CubeState.solved()}
        counts=[]
        for _depth in range(1,4):
            nxt=set()
            for s in frontier:
                for move in MOVE_TOKENS:
                    ns=s.apply(move)
                    if ns.key() not in seen:
                        seen.add(ns.key()); nxt.add(ns)
            counts.append(len(nxt)); frontier=nxt
        self.assertEqual(counts,[18,243,3240])

if __name__ == '__main__': unittest.main()
