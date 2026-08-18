#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("supply.py")
SPEC = importlib.util.spec_from_file_location("ruck_supply", MODULE_PATH)
SUPPLY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUPPLY)


COIN = 100_000_000
REWARD = 5_000 * COIN
HALVING = 2_100_000


class SupplyTests(unittest.TestCase):
    def test_genesis_is_not_issued_supply(self):
        self.assertEqual(SUPPLY.subsidy_emitted_satoshis(0, REWARD, HALVING), 0)

    def test_early_chain(self):
        self.assertEqual(SUPPLY.subsidy_emitted_satoshis(1, REWARD, HALVING), REWARD)
        self.assertEqual(SUPPLY.subsidy_emitted_satoshis(337, REWARD, HALVING), 337 * REWARD)

    def test_first_halving_boundary(self):
        before = (HALVING - 1) * REWARD
        self.assertEqual(SUPPLY.subsidy_emitted_satoshis(HALVING - 1, REWARD, HALVING), before)
        self.assertEqual(
            SUPPLY.subsidy_emitted_satoshis(HALVING, REWARD, HALVING),
            before + (REWARD // 2),
        )


if __name__ == "__main__":
    unittest.main()
