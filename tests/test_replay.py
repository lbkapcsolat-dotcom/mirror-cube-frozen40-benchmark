import json, unittest
from repro.cube import CubeState
from repro.dataset import canonical_sequence_sha256

PAIRS={
7:("R2 U F' L D L2 R U2 L R2 U2 R2 B2", "B2 L2 D2 R2 L' D2 R D' L' F U' R2", '31b1d37318a64360e3051ada912ca89c407586576273ad85019cb8759e3d89bc'),
9:("F D2 B' U D L2 F B' D' F2 B2 L2 F2", "R2 U2 F B' U' D F' L2 B' D2 R2 F'", '897dbf296c2d776408cc304ff96dfe4b4afc3d56a75ae5485859256a0046f01d'),
20:("B D' F2 U' R2 U2 B2 U2 L2 R' D2 F' B2", "F B2 D2 R' D2 F2 D2 L2 U F2 D B'", '8832af9a86a8e3a85ca1a00a4849c19f88c1f78e153d90dc25eb925c12f92331'),
29:("U' D2 F' L' D' L B D B' L2 B R' F'", "F R B' L2 F L' D F L F' U D", '07f181d4f3dacaa53ceee19d6d4d790d34c7c2efaf5f23d358cad969bbcfaa00'),
}

class ReplayTests(unittest.TestCase):
    def test_canonical_generator_hash_convention(self):
        for ordinal,(generator,_witness,expected) in PAIRS.items():
            with self.subTest(ordinal=ordinal):
                self.assertEqual(canonical_sequence_sha256(generator.split()), expected)

    def test_four_public_witnesses_solve(self):
        for ordinal,(generator,witness,_hash) in PAIRS.items():
            with self.subTest(ordinal=ordinal):
                target=CubeState.solved().apply_sequence(generator)
                self.assertTrue(target.apply_sequence(witness).is_solved())

class PublicReplayContractTests(unittest.TestCase):
    def test_replay_rejects_non_frozen40_scope(self):
        import csv, tempfile
        from pathlib import Path
        from repro.replay import replay_public_inputs
        with tempfile.TemporaryDirectory() as td:
            ledger=Path(td)/'ledger.csv'; witnesses=Path(td)/'w.json'
            seq="U R F D L B U R F D L B U".split()
            with ledger.open('w',newline='',encoding='utf-8') as f:
                w=csv.writer(f); w.writerow(['ordinal','exact_distance_htm','classification','frozen_sequence_13','frozen_sequence_sha256','proof_route'])
                w.writerow([1,13,'EXACT13',' '.join(seq),canonical_sequence_sha256(seq),'TEST'])
            witnesses.write_text(json.dumps({'count':0,'ordinals':[],'witnesses':[]}),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'ordinals 1..40'):
                replay_public_inputs(ledger,witnesses,True)

if __name__ == '__main__': unittest.main()
