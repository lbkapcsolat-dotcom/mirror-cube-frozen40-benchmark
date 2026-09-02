import hashlib, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ManifestTests(unittest.TestCase):
    def test_manifest_hashes_match_checked_in_bytes(self):
        manifest=json.loads((ROOT/'repro/PUBLIC_REPRO_MANIFEST.json').read_text(encoding='utf-8'))
        mismatches=[]
        for section in ('public_inputs','source_files','test_files','support_files'):
            for path,expected in manifest[section].items():
                actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
                if actual != expected:
                    mismatches.append({'path':path,'expected':expected,'actual':actual})
        self.assertEqual(mismatches,[],json.dumps(mismatches,indent=2,sort_keys=True))

    def test_manifest_keeps_frozen_inputs_as_inputs(self):
        manifest=json.loads((ROOT/'repro/PUBLIC_REPRO_MANIFEST.json').read_text(encoding='utf-8'))
        self.assertEqual(set(manifest['public_inputs']),{
            'data/FROZEN_40_EXACT_DISTANCE_LEDGER.csv',
            'data/EXACT12_WITNESS_REGISTRY.json',
        })
        self.assertEqual(manifest['benchmark_id'],'MC-F40-EXACT-HTM-V1')
        self.assertEqual(manifest['full_lower_bound_status'],'HOLD_NOT_YET_FRESHLY_EXECUTED')

if __name__=='__main__': unittest.main()
