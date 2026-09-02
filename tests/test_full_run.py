import tempfile
import unittest
from pathlib import Path

from repro.full_run import logical_cache_digest, make_semantic_receipt
from repro.mitm import build_radius_cache


class FullRunReceiptTests(unittest.TestCase):
    def test_logical_cache_digest_is_stable_across_independent_builds(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / 'a.sqlite'
            p2 = Path(td) / 'b.sqlite'
            build_radius_cache(p1, 3)
            build_radius_cache(p2, 3)
            self.assertEqual(logical_cache_digest(p1, 3), logical_cache_digest(p2, 3))

    def test_semantic_receipt_is_order_independent_for_results(self):
        a = make_semantic_receipt(
            cache_digest='abc',
            radius=3,
            state_count=3502,
            classification_results=[
                {'ordinal': 2, 'status': 'CONFIRMED', 'exact_distance_htm': 13},
                {'ordinal': 1, 'status': 'CONFIRMED', 'exact_distance_htm': 12},
            ],
        )
        b = make_semantic_receipt(
            cache_digest='abc',
            radius=3,
            state_count=3502,
            classification_results=list(reversed(a['classification_results'])),
        )
        self.assertEqual(a, b)
        self.assertEqual(a['classification_results'][0]['ordinal'], 1)


if __name__ == '__main__':
    unittest.main()
