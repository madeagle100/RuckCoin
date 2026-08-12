#!/usr/bin/env python3
# Copyright (c) 2026 The Raven Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

"""
P2AH stress/regression harness.

Runs asset-auth scenarios repeatedly in one session to catch intermittent wallet,
RPC, and consensus bugs. Intended for cron/CI — not a minimal feature test.
"""

import math
import optparse

from test_framework.test_framework import RavenTestFramework
from test_framework.util import assert_equal, assert_raises_rpc_error


def truncate(number, digits=8):
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper


class AssetAuthStressTest(RavenTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.extra_args = [['-assetindex', '-fallbackfee=0.0001'], ['-assetindex', '-fallbackfee=0.0001']]
        self.stress_rounds = 5

    def add_options(self, parser):
        parser.add_option("--stress-rounds", dest="stress_rounds", default=5, type="int",
                          help="How many times to repeat each stress scenario (default: %default)")

    def activate(self):
        n0 = self.nodes[0]
        n0.generate(432)
        self.sync_all()
        assert_equal("active", n0.getblockchaininfo()['bip9_softforks']['assets']['status'])
        assert_equal("active", n0.getblockchaininfo()['bip9_softforks']['assetauth']['status'])

    def stress_simple_spend(self, round_idx):
        n0, n1 = self.nodes[0], self.nodes[1]
        asset = "STR%d" % round_idx
        n0.issue(asset, 1000)
        n0.generate(1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, [asset + "!"])
        n0.sendtoaddress(p2ah['address'], 20)
        n0.generate(1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: 19.5})
        assert_equal(spend['owner_assets_moved'], [asset + "!"])

        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        n0.generate(1)
        self.sync_all()
        assert_equal(float(n1.getreceivedbyaddress(dest)), 19.5)

    def stress_chained_spend(self, round_idx):
        n0, n1 = self.nodes[0], self.nodes[1]
        root = "RT%d!" % round_idx
        leaf = "LF%d!" % round_idx
        n0.issue(root.replace("!", ""), 100)
        n0.issue(leaf.replace("!", ""), 100)
        n0.generate(1)
        self.sync_all()

        p2ah_root = n0.addassetauthaddress(1, [root])
        p2ah_leaf = n0.addassetauthaddress(1, [leaf])

        n0.transfer(leaf, 1, p2ah_root['address'])
        n0.sendtoaddress(p2ah_leaf['address'], 5)
        n0.generate(1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah_leaf['address'], {dest: 4.9})
        assert_equal(spend['owner_assets_moved'], [root, leaf])

        moved = dict(zip(spend['owner_assets_moved'], spend['owner_asset_destinations']))
        assert moved[root] != p2ah_root['address']
        assert_equal(moved[leaf], p2ah_root['address'])

        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        n0.generate(1)
        self.sync_all()

        # Second chained spend from the restored LEAF! position
        dest2 = n1.getnewaddress()
        spend2 = n0.spendassetauth(p2ah_leaf['address'], {dest2: 0.1})
        assert root in spend2['owner_assets_moved']
        assert leaf in spend2['owner_assets_moved']

        n0.generate(1)
        self.sync_all()

    def stress_multisig_and_multi_utxo(self, round_idx):
        n0 = self.nodes[0]
        a = "BA%d!" % round_idx
        b = "BB%d!" % round_idx
        c = "BC%d!" % round_idx
        n0.issue(a.replace("!", ""), 100)
        n0.issue(b.replace("!", ""), 100)
        n0.issue(c.replace("!", ""), 100)
        n0.generate(1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(2, [a, b, c])

        n0.sendtoaddress(p2ah['address'], 3)
        n0.sendtoaddress(p2ah['address'], 4)
        n0.generate(1)
        self.sync_all()

        assert_equal(len(n0.listassetauthutxos(p2ah['address'])), 2)

        dest = n0.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: 6.5})
        assert_equal(len(spend['owner_assets_moved']), 2)

        rawtx = n0.getrawtransaction(spend['txid'], 1)
        p2ah_inputs = [vin for vin in rawtx['vin'] if 'assetAuthPreimage' in vin]
        assert_equal(len(p2ah_inputs), 2)

        n0.generate(1)
        self.sync_all()

    def stress_asset_on_p2ah(self, round_idx):
        n0, n1 = self.nodes[0], self.nodes[1]
        owner = "OWN%d!" % round_idx
        token = "TOK%d" % round_idx
        n0.issue(owner.replace("!", ""), 100)
        n0.issue(token, 1000)
        n0.generate(1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, [owner])
        n0.transfer(token, 500, p2ah['address'])
        n0.generate(1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: {'transfer': {token: 100}}})
        assert_equal(spend['owner_assets_moved'], [owner])

        n0.generate(1)
        self.sync_all()
        assert_equal(float(n1.listmyassets(token)[token]), 100.0)

    def stress_rejection_paths(self):
        n0 = self.nodes[0]
        n0.issue("REJ", 100)
        n0.generate(1)
        self.sync_all()

        p2ah = n0.createassetauthaddress(1, ["REJ!"])
        utxos = n0.listassetauthutxos(p2ah['address'])
        if not utxos:
            n0.sendtoaddress(p2ah['address'], 2)
            n0.generate(1)
            self.sync_all()
            utxos = n0.listassetauthutxos(p2ah['address'])

        utxo = utxos[0]
        dest = n0.getnewaddress()
        inputs = [{'txid': utxo['txid'], 'vout': utxo['vout']}]
        outputs = {dest: float(utxo['amount']) - 0.01}
        rawtx = n0.createrawtransaction(inputs, outputs)
        spk = n0.getrawtransaction(utxo['txid'], 1)['vout'][utxo['vout']]['scriptPubKey']['hex']
        prevtxs = [{'txid': utxo['txid'], 'vout': utxo['vout'], 'scriptPubKey': spk,
                    'assetAuthPreimage': p2ah['preimage'], 'amount': float(utxo['amount'])}]
        signed = n0.signrawtransaction(rawtx, prevtxs)
        assert_raises_rpc_error(-26, "bad-txns-assetauth-insufficient-owner-movement",
                                n0.sendrawtransaction, signed['hex'])

    def run_test(self):
        self.stress_rounds = max(1, int(getattr(self.options, 'stress_rounds', 5)))

        self.log.info("Activating assets + assetauth for stress run (%d rounds each)" % self.stress_rounds)
        self.activate()

        for i in range(self.stress_rounds):
            self.log.info("=== stress round %d/%d: simple spend ===" % (i + 1, self.stress_rounds))
            self.stress_simple_spend(i)

        for i in range(self.stress_rounds):
            self.log.info("=== stress round %d/%d: chained spend (double) ===" % (i + 1, self.stress_rounds))
            self.stress_chained_spend(i)

        for i in range(self.stress_rounds):
            self.log.info("=== stress round %d/%d: multisig + multi-utxo ===" % (i + 1, self.stress_rounds))
            self.stress_multisig_and_multi_utxo(i)

        for i in range(self.stress_rounds):
            self.log.info("=== stress round %d/%d: asset held at P2AH ===" % (i + 1, self.stress_rounds))
            self.stress_asset_on_p2ah(i)

        for i in range(self.stress_rounds):
            self.log.info("=== stress round %d/%d: rejection paths ===" % (i + 1, self.stress_rounds))
            self.stress_rejection_paths()

        self.log.info("P2AH stress harness finished %d rounds x 5 scenarios" % self.stress_rounds)


if __name__ == '__main__':
    AssetAuthStressTest().main()
