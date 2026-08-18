#!/usr/bin/env python3
# Copyright (c) 2026 The Raven Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

"""
P2AH stress/regression harness.

Runs asset-auth scenarios repeatedly, appending blocks to one regtest chain so
wallet/chain history accumulates across cron invocations.

Persistent chain (default for cron)
-----------------------------------
Pass --persistent-dir=/path/to/chain (or set P2AH_DATADIR). The same node
datadirs are reused; each run adds blocks/transactions on top of prior history.
A monotonic run counter drives unique asset names so scenarios do not collide.

Ephemeral chain (one-off debugging)
-----------------------------------
Omit --persistent-dir to use a temporary datadir (removed after the run unless
--nocleanup is set).
"""

import math
import os
import shutil
import time

from test_framework.test_framework import RavenTestFramework
from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
    connect_nodes_bi,
    initialize_data_dir,
    set_node_times,
    sync_blocks,
    sync_mempools,
)


def truncate(number, digits=8):
    stepper = pow(10.0, digits)
    return math.trunc(stepper * number) / stepper


class AssetAuthStressTest(RavenTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.extra_args = [['-assetindex', '-fallbackfee=0.0001'], ['-assetindex', '-fallbackfee=0.0001']]
        self.stress_rounds = 5
        self.persistent_dir = None
        self.run_id = 0
        self.tag_epoch = 0
        self.scenario_counter = 0
        self._persistent_fund_address = None

    def add_options(self, parser):
        parser.add_option("--stress-rounds", dest="stress_rounds", default=5, type="int",
                          help="How many times to repeat each stress scenario (default: %default)")
        parser.add_option("--persistent-dir", dest="persistent_dir", default=os.environ.get("P2AH_DATADIR", ""),
                          help="Reuse this datadir across runs to accumulate chain history")
        parser.add_option("--reset-chain", dest="reset_chain", default=False, action="store_true",
                          help="Delete persistent-dir before starting (fresh chain)")

    def setup_chain(self):
        self.persistent_dir = getattr(self.options, "persistent_dir", "") or None
        if self.persistent_dir:
            self.persistent_dir = os.path.abspath(self.persistent_dir)
            if getattr(self.options, "reset_chain", False) and os.path.isdir(self.persistent_dir):
                self.log.info("Resetting persistent chain at %s" % self.persistent_dir)
                shutil.rmtree(self.persistent_dir)
            os.makedirs(self.persistent_dir, exist_ok=True)
            self.options.tmpdir = self.persistent_dir
            self.options.nocleanup = True
            self.log.info("Using persistent chain datadir %s" % self.persistent_dir)
            for i in range(self.num_nodes):
                initialize_data_dir(self.options.tmpdir, i)
            self._prepare_persistent_mempools()
            self.run_id = self._load_run_counter()
            self.log.info("Persistent run id %d (block height will accumulate)" % self.run_id)
        else:
            super().setup_chain()

    def _counter_path(self):
        return os.path.join(self.options.tmpdir, "p2ah_stress_run_counter")

    def _load_run_counter(self):
        path = self._counter_path()
        if os.path.isfile(path):
            with open(path, "r", encoding="utf8") as f:
                return int(f.read().strip())
        return 0

    def _save_run_counter(self, value):
        with open(self._counter_path(), "w", encoding="utf8") as f:
            f.write(str(value))

    def _height_path(self):
        return os.path.join(self.options.tmpdir, "p2ah_chain_height")

    def _save_chain_height(self, height):
        if self.persistent_dir:
            with open(self._height_path(), "w", encoding="utf8") as f:
                f.write(str(height))

    def unique_tag(self, prefix):
        """Short unique name (<=31 chars, A-Z0-9 only) for persistent chain history."""
        self.scenario_counter += 1
        base = "".join(c for c in prefix.upper() if c.isalnum())[:4]
        return "%s%04X%04X" % (base.ljust(4, "X"), self.tag_epoch & 0xFFFF, self.scenario_counter & 0xFFFF)

    def _mempool_dat_paths(self, node_index):
        base = os.path.join(self.persistent_dir, "node%d" % node_index)
        for rel in ("regtest/mempool.dat", "mempool.dat"):
            yield os.path.join(base, rel)

    def _prepare_persistent_mempools(self):
        """Do not reload divergent mempools from an aborted prior run."""
        no_persist = "-persistmempool=0"
        self.extra_args = [
            (args + [no_persist]) if no_persist not in args else args
            for args in self.extra_args
        ]
        for i in range(self.num_nodes):
            for path in self._mempool_dat_paths(i):
                if os.path.isfile(path):
                    self.log.info("Removing stale mempool state %s" % path)
                    os.remove(path)

    def reconcile_mempools(self):
        """Mine until all nodes share the same mempool."""
        max_attempts = 5
        for attempt in range(max_attempts):
            pools = [set(n.getrawmempool()) for n in self.nodes]
            if pools[0] == pools[1]:
                if attempt:
                    self.log.info("Mempools reconciled after %d block(s)" % attempt)
                return
            sizes = [len(p) for p in pools]
            self.log.info("Mempool mismatch (sizes %s); mining reconciliation block" % sizes)
            self.mine(self.nodes[0], 1)
            sync_blocks(self.nodes)

        pools = [set(n.getrawmempool()) for n in self.nodes]
        if pools[0] == pools[1]:
            return

        only0 = pools[0] - pools[1]
        only1 = pools[1] - pools[0]
        self.log.warning("Mempools still differ after %d blocks (only node0=%d only node1=%d)" % (
            max_attempts, len(only0), len(only1)))
        if only1 and not only0:
            self.mine(self.nodes[1], 1)
        elif only0:
            self.mine(self.nodes[0], 1)
        sync_blocks(self.nodes)

        pools = [set(n.getrawmempool()) for n in self.nodes]
        if pools[0] != pools[1]:
            raise AssertionError(
                "Mempool reconciliation failed: %s vs %s txs" % (len(pools[0]), len(pools[1])))

    def setup_network(self):
        self.log.info("Running setup_network")
        self.setup_nodes()
        for i in range(self.num_nodes - 1):
            connect_nodes_bi(self.nodes, i, i + 1)
        sync_blocks(self.nodes)
        if self.persistent_dir:
            self.reconcile_mempools()
        sync_mempools(self.nodes)

    def _fund_address(self):
        if self._persistent_fund_address is None:
            self._persistent_fund_address = self.nodes[0].getnewaddress()
        return self._persistent_fund_address

    def _regtest_block_subsidy(self, height):
        """Regtest subsidy (5000 RVN initial, halving every 150 blocks)."""
        halvings = height // 150
        if halvings >= 64:
            return 0.0
        return 5000.0 / (2 ** halvings)

    def _clear_stale_mempool_files(self):
        for i in range(self.num_nodes):
            for path in self._mempool_dat_paths(i):
                if os.path.isfile(path):
                    os.remove(path)

    def _reset_persistent_chain(self):
        """Wipe node datadirs when regtest subsidy can no longer fund issue burns."""
        height = self.nodes[0].getblockcount()
        subsidy = self._regtest_block_subsidy(height + 1)
        self.log.warning(
            "Resetting persistent chain (height %d, next block subsidy %.4f RVN)" % (height, subsidy))
        self.stop_nodes()
        for i in range(self.num_nodes):
            node_dir = os.path.join(self.persistent_dir, "node%d" % i)
            if os.path.isdir(node_dir):
                shutil.rmtree(node_dir)
        self._persistent_fund_address = None
        for i in range(self.num_nodes):
            initialize_data_dir(self.persistent_dir, i)
        self._clear_stale_mempool_files()
        self.start_nodes()
        for i in range(self.num_nodes - 1):
            connect_nodes_bi(self.nodes, i, i + 1)
        sync_blocks(self.nodes)
        sync_mempools(self.nodes)
        self.mine(self.nodes[0], 101)

    def ensure_persistent_funds(self):
        """Keep node0 funded for 500 RVN asset-issue burns on a long-lived chain."""
        if not self.persistent_dir:
            return
        n0 = self.nodes[0]
        min_balance = 550
        balance = n0.getbalance()
        if balance >= min_balance:
            return
        if self._regtest_block_subsidy(n0.getblockcount() + 1) < min_balance:
            self._reset_persistent_chain()
            if n0.getbalance() >= min_balance:
                return
        self.log.info("Node0 balance low (%.8f); mining coinbase (every 10th to %s)" % (
            balance, self._fund_address()))
        for attempt in range(3):
            if n0.getbalance() >= min_balance:
                return
            if self._regtest_block_subsidy(n0.getblockcount() + 1) < min_balance:
                self._reset_persistent_chain()
                continue
            self.log.info("Funding batch %d (height %d)" % (attempt + 1, n0.getblockcount()))
            self._mine_blocks(n0, 101)
        if n0.getbalance() < min_balance:
            self._reset_persistent_chain()
        if n0.getbalance() < min_balance:
            raise AssertionError("Node0 balance still %.8f after persistent chain reset" % n0.getbalance())

    def mine(self, node, count=1):
        self._mine_blocks(node, count)

    def _mine_blocks(self, node, count):
        fund_addr = self._fund_address() if self.persistent_dir and node is self.nodes[0] else None
        for i in range(count):
            tip_time = max(node.getblockchaininfo()['mediantime'], int(time.time()))
            set_node_times(self.nodes, tip_time + 1)
            if fund_addr and (i + 1) % 10 == 0:
                node.generatetoaddress(1, fund_addr)
            else:
                node.generate(1)
        sync_blocks(self.nodes)

    def activate(self):
        n0 = self.nodes[0]
        info = n0.getblockchaininfo()
        assets_status = info['bip9_softforks']['assets']['status']
        auth_status = info['bip9_softforks']['assetauth']['status']
        assert_equal("active", assets_status)
        assert_equal("active", auth_status)
        if info['blocks'] < 101:
            self.log.info("Mining mature coinbase (assets/assetauth active from genesis, height %d)" % info['blocks'])
            self.mine(n0, 101 - info['blocks'])
            self.sync_all()
        else:
            self.log.info("Assets/assetauth active from genesis at height %d" % info['blocks'])

    def stress_simple_spend(self):
        n0, n1 = self.nodes[0], self.nodes[1]
        tag = self.unique_tag("STR")
        n0.issue(tag, 1000)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, [tag + "!"])
        n0.sendtoaddress(p2ah['address'], 20)
        self.mine(n0, 1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: 19.5})
        assert_equal(spend['owner_assets_moved'], [tag + "!"])

        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        self.mine(n0, 1)
        self.sync_all()
        assert_equal(float(n1.getreceivedbyaddress(dest)), 19.5)

    def stress_chained_spend(self):
        n0, n1 = self.nodes[0], self.nodes[1]
        root = self.unique_tag("RT") + "!"
        leaf = self.unique_tag("LF") + "!"
        n0.issue(root.replace("!", ""), 100)
        n0.issue(leaf.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah_root = n0.addassetauthaddress(1, [root])
        p2ah_leaf = n0.addassetauthaddress(1, [leaf])

        n0.transfer(leaf, 1, p2ah_root['address'])
        n0.sendtoaddress(p2ah_leaf['address'], 5)
        self.mine(n0, 1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah_leaf['address'], {dest: 4.9})
        assert_equal(spend['owner_assets_moved'], [root, leaf])

        moved = dict(zip(spend['owner_assets_moved'], spend['owner_asset_destinations']))
        assert moved[root] != p2ah_root['address']
        assert_equal(moved[leaf], p2ah_root['address'])

        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        self.mine(n0, 1)
        self.sync_all()

        dest2 = n1.getnewaddress()
        spend2 = n0.spendassetauth(p2ah_leaf['address'], {dest2: 0.1})
        assert root in spend2['owner_assets_moved']
        assert leaf in spend2['owner_assets_moved']

        self.mine(n0, 1)
        self.sync_all()

    def stress_multisig_and_multi_utxo(self):
        n0 = self.nodes[0]
        a = self.unique_tag("BA") + "!"
        b = self.unique_tag("BB") + "!"
        c = self.unique_tag("BC") + "!"
        n0.issue(a.replace("!", ""), 100)
        n0.issue(b.replace("!", ""), 100)
        n0.issue(c.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(2, [a, b, c])

        n0.sendtoaddress(p2ah['address'], 3)
        n0.sendtoaddress(p2ah['address'], 4)
        self.mine(n0, 1)
        self.sync_all()

        assert_equal(len(n0.listassetauthutxos(p2ah['address'])), 2)

        dest = n0.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: 6.5})
        assert_equal(len(spend['owner_assets_moved']), 2)

        rawtx = n0.getrawtransaction(spend['txid'], 1)
        p2ah_inputs = [vin for vin in rawtx['vin'] if 'assetAuthPreimage' in vin]
        assert_equal(len(p2ah_inputs), 2)

        self.mine(n0, 1)
        self.sync_all()

    def stress_asset_on_p2ah(self):
        n0, n1 = self.nodes[0], self.nodes[1]
        owner = self.unique_tag("OWN") + "!"
        token = self.unique_tag("TOK")
        n0.issue(owner.replace("!", ""), 100)
        n0.issue(token, 1000)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, [owner])
        n0.transfer(token, 500, p2ah['address'])
        self.mine(n0, 1)
        self.sync_all()

        dest = n1.getnewaddress()
        spend = n0.spendassetauth(p2ah['address'], {dest: {'transfer': {token: 100}}})
        assert_equal(spend['owner_assets_moved'], [owner])

        self.mine(n0, 1)
        self.sync_all()
        assert_equal(float(n1.listmyassets(token)[token]), 100.0)

    def stress_nested_multisig_chain_heavy(self):
        """2-of-3 outer P2AH authorizes 1-of-3 inner P2AH holding many UTXOs."""
        n0, n1 = self.nodes[0], self.nodes[1]
        gate_a = self.unique_tag("GA") + "!"
        gate_b = self.unique_tag("GB") + "!"
        gate_c = self.unique_tag("GC") + "!"
        vault_a = self.unique_tag("VA") + "!"
        vault_b = self.unique_tag("VB") + "!"
        vault_c = self.unique_tag("VC") + "!"
        heavy_asset = self.unique_tag("HVY")

        for name in (gate_a, gate_b, gate_c, vault_a, vault_b, vault_c):
            n0.issue(name.replace("!", ""), 100)
        n0.issue(heavy_asset, 10000)
        self.mine(n0, 1)
        self.sync_all()

        p2ah_outer = n0.addassetauthaddress(2, [gate_a, gate_b, gate_c])
        p2ah_inner = n0.addassetauthaddress(1, [vault_a, vault_b, vault_c])

        n0.transfer(vault_a, 1, p2ah_outer['address'])
        self.mine(n0, 1)
        self.sync_all()

        for _ in range(8):
            n0.sendtoaddress(p2ah_inner['address'], 0.5)
        for amount in (100, 150, 200, 250):
            n0.transfer(heavy_asset, amount, p2ah_inner['address'])
        self.mine(n0, 1)
        self.sync_all()

        utxos = n0.listassetauthutxos(p2ah_inner['address'])
        assert len(utxos) >= 8
        asset_utxos = [u for u in utxos if 'asset' in u and u['asset']['name'] == heavy_asset]
        assert len(asset_utxos) >= 4

        dest_rvn = n1.getnewaddress()
        dest_asset = n1.getnewaddress()
        spend = n0.spendassetauth(
            p2ah_inner['address'],
            {dest_rvn: 3.5, dest_asset: {'transfer': {heavy_asset: 400}}},
        )
        assert_equal(len(spend['owner_assets_moved']), 3)
        assert vault_a in spend['owner_assets_moved']
        assert len([g for g in (gate_a, gate_b, gate_c) if g in spend['owner_assets_moved']]) == 2

        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        self.mine(n0, 1)
        self.sync_all()
        assert float(n1.listmyassets(heavy_asset)[heavy_asset]) >= 400.0

        dest2 = n1.getnewaddress()
        spend2 = n0.spendassetauth(p2ah_inner['address'], {dest2: 0.4})
        assert len(spend2['owner_assets_moved']) >= 3
        self.mine(n0, 1)
        self.sync_all()

    def stress_concurrent_same_dest_same_block(self):
        """Two independent 1-of-3 P2AH addresses spend to the same dest in one block."""
        n0, n1 = self.nodes[0], self.nodes[1]
        shared_dest = n1.getnewaddress()

        setups = [
            (self.unique_tag("LA"), [self.unique_tag("LAA") + "!", self.unique_tag("LAB") + "!", self.unique_tag("LAC") + "!"]),
            (self.unique_tag("LB"), [self.unique_tag("LBA") + "!", self.unique_tag("LBB") + "!", self.unique_tag("LBC") + "!"]),
        ]

        p2ah_addrs = []
        for _, owners in setups:
            for owner in owners:
                n0.issue(owner.replace("!", ""), 100)
            self.mine(n0, 1)
            self.sync_all()
            p2ah = n0.addassetauthaddress(1, owners)
            n0.sendtoaddress(p2ah['address'], 2.0)
            self.mine(n0, 1)
            self.sync_all()
            p2ah_addrs.append(p2ah['address'])

        spend_a = n0.spendassetauth(p2ah_addrs[0], {shared_dest: 1.5})
        spend_b = n0.spendassetauth(p2ah_addrs[1], {shared_dest: 1.5})
        assert spend_a['txid'] != spend_b['txid']

        for txid in (spend_a['txid'], spend_b['txid']):
            verify = n0.verifyassetauth(n0.getrawtransaction(txid))
            assert_equal(verify['valid'], True)

        self.mine(n0, 1)
        self.sync_all()
        assert float(n1.getreceivedbyaddress(shared_dest)) >= 3.0

    def stress_same_p2ah_same_block_dual_spend(self):
        """Same 1-of-3 P2AH: two spends to same dest queued before one block."""
        n0, n1 = self.nodes[0], self.nodes[1]
        owners = [self.unique_tag("SA") + "!", self.unique_tag("SB") + "!", self.unique_tag("SC") + "!"]
        for owner in owners:
            n0.issue(owner.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()
        for owner in owners:
            assert owner in n0.listmyassets()

        p2ah = n0.addassetauthaddress(1, owners)
        shared_dest = n1.getnewaddress()
        for _ in range(4):
            n0.sendtoaddress(p2ah['address'], 1.0)
        self.mine(n0, 1)
        self.sync_all()

        spend1 = n0.spendassetauth(p2ah['address'], {shared_dest: 0.9})
        dual_mempool = True
        try:
            spend2 = n0.spendassetauth(p2ah['address'], {shared_dest: 0.9})
        except Exception as e:
            dual_mempool = False
            self.log.info("Second mempool spend from same 1-of-3 P2AH rejected: %s" % e)
            spend2 = None

        self.mine(n0, 1)
        self.sync_all()
        received = float(n1.getreceivedbyaddress(shared_dest))
        assert received >= 0.9

        if dual_mempool:
            assert spend1['txid'] != spend2['txid']
            moved1 = set(spend1['owner_assets_moved'])
            moved2 = set(spend2['owner_assets_moved'])
            assert len(moved1) == 1
            assert len(moved2) == 1
            assert moved1 != moved2
            assert received >= 1.8
        else:
            self.log.info("Observed wallet single-mempool-spend limit; confirmed %.8f RVN" % received)

    def stress_same_p2ah_sequential_owner_rotation(self):
        """Same 1-of-3 P2AH: confirmed spends in short succession (mine between each)."""
        n0, n1 = self.nodes[0], self.nodes[1]
        owners = [self.unique_tag("SQ") + "!", self.unique_tag("SR") + "!", self.unique_tag("SS") + "!"]
        for owner in owners:
            n0.issue(owner.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, owners)
        shared_dest = n1.getnewaddress()
        for _ in range(4):
            n0.sendtoaddress(p2ah['address'], 1.0)
        self.mine(n0, 1)
        self.sync_all()

        total = 0.0
        spend_count = 0
        for amount in (0.9, 0.9, 0.8, 0.8):
            spend = n0.spendassetauth(p2ah['address'], {shared_dest: amount})
            spend_count += 1
            self.mine(n0, 1)
            self.sync_all()
            total = float(n1.getreceivedbyaddress(shared_dest))

        assert spend_count == 4
        assert total >= 3.4

    def stress_one_of_three_shared_asset_same_dest(self):
        """One 1-of-3 P2AH holding two assets; two spends targeting same dest, same block."""
        n0, n1 = self.nodes[0], self.nodes[1]
        owners = [self.unique_tag("OA") + "!", self.unique_tag("OB") + "!", self.unique_tag("OC") + "!"]
        asset_x = self.unique_tag("AX")
        asset_y = self.unique_tag("AY")
        for owner in owners:
            n0.issue(owner.replace("!", ""), 100)
        n0.issue(asset_x, 5000)
        n0.issue(asset_y, 5000)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.addassetauthaddress(1, owners)
        shared_dest = n1.getnewaddress()
        n0.transfer(asset_x, 300, p2ah['address'])
        n0.transfer(asset_y, 400, p2ah['address'])
        n0.sendtoaddress(p2ah['address'], 1.0)
        self.mine(n0, 1)
        self.sync_all()

        spend_x = None
        spend_y = None
        dual_asset_block = True
        try:
            spend_x = n0.spendassetauth(
                p2ah['address'], {shared_dest: {'transfer': {asset_x: 100}}},
            )
            try:
                spend_y = n0.spendassetauth(
                    p2ah['address'], {shared_dest: {'transfer': {asset_y: 150}}},
                )
            except Exception as e:
                dual_asset_block = False
                self.log.info("Second same-block asset spend rejected: %s" % e)
        except Exception as e:
            dual_asset_block = False
            self.log.info("Same-block asset spend unavailable (%s); trying sequential" % e)
            spend_x = n0.spendassetauth(
                p2ah['address'], {shared_dest: {'transfer': {asset_x: 100}}},
            )
            self.mine(n0, 1)
            self.sync_all()
            spend_y = n0.spendassetauth(
                p2ah['address'], {shared_dest: {'transfer': {asset_y: 150}}},
            )

        if spend_y is None:
            self.mine(n0, 1)
            self.sync_all()
            spend_y = n0.spendassetauth(
                p2ah['address'], {shared_dest: {'transfer': {asset_y: 150}}},
            )

        self.mine(n0, 1)
        self.sync_all()
        bal = n1.listmyassets()
        assert spend_x is not None
        assert spend_y is not None
        assert float(bal.get(asset_x, 0)) >= 100.0
        assert float(bal.get(asset_y, 0)) >= 150.0
        if dual_asset_block:
            assert spend_x['txid'] != spend_y['txid']
            assert len(set(spend_x['owner_assets_moved']).intersection(spend_y['owner_assets_moved'])) == 0
        else:
            self.log.info("Confirmed both asset transfers (sequential fallback for second spend)")

    def stress_one_asset_multisig_multi_dest(self):
        """One owner asset authorizes a single spend to two different 2-of-3 P2AH addresses."""
        n0, n1 = self.nodes[0], self.nodes[1]
        hub = self.unique_tag("HUB") + "!"
        va, vb, vc = self.unique_tag("VA") + "!", self.unique_tag("VB") + "!", self.unique_tag("VC") + "!"
        wa, wb, wc = self.unique_tag("WA") + "!", self.unique_tag("WB") + "!", self.unique_tag("WC") + "!"

        for name in (hub, va, vb, vc, wa, wb, wc):
            n0.issue(name.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah_source = n0.addassetauthaddress(1, [hub])
        vault_a = n0.addassetauthaddress(2, [va, vb, vc])
        vault_b = n0.addassetauthaddress(2, [wa, wb, wc])

        n0.sendtoaddress(p2ah_source['address'], 5.0)
        self.mine(n0, 1)
        self.sync_all()

        spend = n0.spendassetauth(
            p2ah_source['address'],
            {vault_a['address']: 2.0, vault_b['address']: 2.5},
        )
        assert_equal(spend['owner_assets_moved'], [hub])
        verify = n0.verifyassetauth(n0.getrawtransaction(spend['txid']))
        assert_equal(verify['valid'], True)

        self.mine(n0, 1)
        self.sync_all()

        utxos_a = n0.listassetauthutxos(vault_a['address'])
        utxos_b = n0.listassetauthutxos(vault_b['address'])
        assert len(utxos_a) >= 1
        assert len(utxos_b) >= 1
        rvn_a = sum(float(u['amount']) for u in utxos_a if 'asset' not in u)
        rvn_b = sum(float(u['amount']) for u in utxos_b if 'asset' not in u)
        assert rvn_a >= 2.0
        assert rvn_b >= 2.5

        # Each vault can spend independently with its own 2-of-3 policy.
        dest_a = n1.getnewaddress()
        dest_b = n1.getnewaddress()
        spend_a = n0.spendassetauth(vault_a['address'], {dest_a: 1.5})
        spend_b = n0.spendassetauth(vault_b['address'], {dest_b: 2.0})
        assert spend_a['txid'] != spend_b['txid']
        assert len(spend_a['owner_assets_moved']) == 2
        assert len(spend_b['owner_assets_moved']) == 2

        self.mine(n0, 1)
        self.sync_all()
        assert float(n1.getreceivedbyaddress(dest_a)) >= 1.5
        assert float(n1.getreceivedbyaddress(dest_b)) >= 2.0

    def stress_one_asset_two_multisig_same_block(self):
        """One hub owner asset chains to two 2-of-3 vaults; spend both in the same block."""
        n0, n1 = self.nodes[0], self.nodes[1]
        hub = self.unique_tag("SG") + "!"
        va, vb, vc = self.unique_tag("GA") + "!", self.unique_tag("GB") + "!", self.unique_tag("GC") + "!"
        wa, wb, wc = self.unique_tag("GD") + "!", self.unique_tag("GE") + "!", self.unique_tag("GF") + "!"

        for name in (hub, va, vb, vc, wa, wb, wc):
            n0.issue(name.replace("!", ""), 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah_hub = n0.addassetauthaddress(1, [hub])
        vault_a = n0.addassetauthaddress(2, [va, vb, vc])
        vault_b = n0.addassetauthaddress(2, [wa, wb, wc])

        # Leave only one co-signer in the wallet so the gate key at the hub must be used.
        n1_addr = n1.getnewaddress()
        n0.transfer(vc, 1, n1_addr)
        n0.transfer(wc, 1, n1_addr)
        n0.transfer(va, 1, p2ah_hub['address'])
        n0.transfer(wa, 1, p2ah_hub['address'])
        n0.sendtoaddress(vault_a['address'], 3.0)
        n0.sendtoaddress(vault_b['address'], 3.0)
        self.mine(n0, 1)
        self.sync_all()

        dest_a = n1.getnewaddress()
        dest_b = n1.getnewaddress()
        same_block = True
        spend_a = n0.spendassetauth(vault_a['address'], {dest_a: 2.5})
        assert hub in spend_a['owner_assets_moved']
        try:
            spend_b = n0.spendassetauth(vault_b['address'], {dest_b: 2.5})
        except Exception as e:
            same_block = False
            self.log.info("Second chained multisig spend same-block rejected: %s" % e)
            spend_b = None

        if spend_b is None:
            self.mine(n0, 1)
            self.sync_all()
            spend_b = n0.spendassetauth(vault_b['address'], {dest_b: 2.5})

        assert len(spend_a['owner_assets_moved']) >= 2
        assert len(spend_b['owner_assets_moved']) >= 2
        assert hub in spend_a['owner_assets_moved']

        self.mine(n0, 1)
        self.sync_all()
        assert float(n1.getreceivedbyaddress(dest_a)) >= 2.5
        assert float(n1.getreceivedbyaddress(dest_b)) >= 2.5

        if same_block:
            assert spend_a['txid'] != spend_b['txid']
            self.log.info("One hub asset authorized two 2-of-3 vault spends in the same block")
        else:
            self.log.info("Hub asset authorized both vaults (sequential fallback for second spend)")

    def stress_subpoena_recovery_seizure_chain(self):
        """Nested 2-of-3 chains: subpoenaed recovery keys seize treasury + admin owner token.

        Topology (each layer is 2-of-3 P2AH):

          recovery_p2ah  --holds gate-->  CUST_A!  (subpoenaed REC_A + REC_B authorize)
                |
          custody_p2ah  --holds gate-->  VAULT_A!
                |
          vault_p2ah    --holds-->       TREASURY asset + TREASURY! (admin owner token)

        Authority wallet retains only the subpoenaed/compelled keys; user-held keys are
        transferred away so spends must walk the full chain.
        """
        n0, n1 = self.nodes[0], self.nodes[1]
        # Recovery layer — simulates court/compelled 2-of-3 (authority has 2 of 3)
        rec_a = self.unique_tag("RC") + "!"
        rec_b = self.unique_tag("RD") + "!"
        rec_c = self.unique_tag("RE") + "!"
        # Custody layer — original custodian multisig
        cust_a = self.unique_tag("CS") + "!"
        cust_b = self.unique_tag("CT") + "!"
        cust_c = self.unique_tag("CU") + "!"
        # Vault layer — holds the asset under admin control
        vault_a = self.unique_tag("VL") + "!"
        vault_b = self.unique_tag("VM") + "!"
        vault_c = self.unique_tag("VN") + "!"
        treasury = self.unique_tag("TRS")
        admin = treasury + "!"

        for name in (rec_a, rec_b, rec_c, cust_a, cust_b, cust_c, vault_a, vault_b, vault_c):
            n0.issue(name.replace("!", ""), 100)
        n0.issue(treasury, 50000)
        self.mine(n0, 1)
        self.sync_all()

        recovery_p2ah = n0.addassetauthaddress(2, [rec_a, rec_b, rec_c])
        custody_p2ah = n0.addassetauthaddress(2, [cust_a, cust_b, cust_c])
        vault_p2ah = n0.addassetauthaddress(2, [vault_a, vault_b, vault_c])

        # Gate keys sit at the parent layer (recovery holds custody gate, custody holds vault gate).
        n0.transfer(cust_a, 1, recovery_p2ah['address'])
        n0.transfer(vault_a, 1, custody_p2ah['address'])
        n0.transfer(treasury, 40000, vault_p2ah['address'])
        n0.transfer(admin, 1, vault_p2ah['address'])
        n0.sendtoaddress(vault_p2ah['address'], 2.0)
        self.mine(n0, 1)
        self.sync_all()

        # User-held keys the authority did NOT obtain — only subpoenaed recovery pair remains usable.
        user_sink = n1.getnewaddress()
        n0.transfer(rec_c, 1, user_sink)
        n0.transfer(cust_c, 1, user_sink)
        n0.transfer(vault_c, 1, user_sink)
        self.mine(n0, 1)
        self.sync_all()

        seizure_asset_dest = n1.getnewaddress()
        seizure_admin_dest = recovery_p2ah['address']

        # Phase 1: seize treasury tokens + move admin owner token to recovery custody.
        seize1 = n0.spendassetauth(
            vault_p2ah['address'],
            {
                seizure_asset_dest: {'transfer': {treasury: 25000}},
                seizure_admin_dest: {'transfer': {admin: 1}},
            },
        )
        moved = set(seize1['owner_assets_moved'])
        assert len(moved) >= 5
        assert len([k for k in (rec_a, rec_b) if k in moved]) == 2
        assert len([k for k in (cust_a, cust_b) if k in moved]) >= 1
        assert len([k for k in (vault_a, vault_b) if k in moved]) >= 1

        self.mine(n0, 1)
        self.sync_all()
        assert float(n1.listmyassets(treasury)[treasury]) >= 25000.0

        admin_on_recovery = [
            u for u in n0.listassetauthutxos(recovery_p2ah['address'])
            if 'asset' in u and u['asset']['name'] == admin
        ]
        assert len(admin_on_recovery) >= 1
        self.log.info("Seized %s admin token to recovery P2AH" % admin)

        # Phase 2: using the same subpoenaed chain, drain remaining treasury from vault.
        seizure_asset_dest2 = n1.getnewaddress()
        seize2 = n0.spendassetauth(
            vault_p2ah['address'],
            {seizure_asset_dest2: {'transfer': {treasury: 10000}}},
        )
        assert len(seize2['owner_assets_moved']) >= 4
        self.mine(n0, 1)
        self.sync_all()
        total_seized = float(n1.listmyassets(treasury)[treasury])
        assert total_seized >= 35000.0

        # Phase 3: recovery P2AH re-spends the seized admin token to a final escrow (full control transfer).
        final_escrow = n1.getnewaddress()
        admin_spend = n0.spendassetauth(
            recovery_p2ah['address'],
            {final_escrow: {'transfer': {admin: 1}}},
        )
        assert len([k for k in (rec_a, rec_b) if k in admin_spend['owner_assets_moved']]) == 2
        self.mine(n0, 1)
        self.sync_all()

        assert float(n1.listmyassets().get(admin, 0)) >= 1.0
        self.log.info(
            "Subpoena recovery chain complete: seized %.0f %s, admin %s in final escrow"
            % (total_seized, treasury, admin)
        )

    def stress_rejection_paths(self):
        n0 = self.nodes[0]
        tag = self.unique_tag("REJ")
        n0.issue(tag, 100)
        self.mine(n0, 1)
        self.sync_all()

        p2ah = n0.createassetauthaddress(1, [tag + "!"])
        n0.sendtoaddress(p2ah['address'], 2)
        self.mine(n0, 1)
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

        if self.persistent_dir:
            self._save_run_counter(self.run_id + 1)
        self.activate()
        self.ensure_persistent_funds()

        start_height = self.nodes[0].getblockcount()
        self.tag_epoch = (start_height << 4) | (self.run_id & 0xF)
        self.scenario_counter = 0
        self.log.info("Stress run %d: %d scenario-rounds each, starting height %d (tag epoch 0x%X)" % (
            self.run_id, self.stress_rounds, start_height, self.tag_epoch))

        scenarios = (
            ("simple spend", self.stress_simple_spend),
            ("chained spend (double)", self.stress_chained_spend),
            ("multisig + multi-utxo", self.stress_multisig_and_multi_utxo),
            ("asset held at P2AH", self.stress_asset_on_p2ah),
            ("nested 2-of-3 -> 1-of-3 heavy", self.stress_nested_multisig_chain_heavy),
            ("concurrent same dest same block", self.stress_concurrent_same_dest_same_block),
            ("same P2AH same-block dual spend", self.stress_same_p2ah_same_block_dual_spend),
            ("same P2AH sequential owner rotation", self.stress_same_p2ah_sequential_owner_rotation),
            ("dual asset same P2AH same block", self.stress_one_of_three_shared_asset_same_dest),
            ("one asset -> two multisig dests", self.stress_one_asset_multisig_multi_dest),
            ("one asset two multisig same block", self.stress_one_asset_two_multisig_same_block),
            ("subpoena recovery seizure chain", self.stress_subpoena_recovery_seizure_chain),
            ("rejection paths", self.stress_rejection_paths),
        )

        for i in range(self.stress_rounds):
            for name, fn in scenarios:
                self.ensure_persistent_funds()
                self.log.info("=== round %d/%d: %s ===" % (i + 1, self.stress_rounds, name))
                fn()

        end_height = self.nodes[0].getblockcount()
        self.log.info("Stress harness done: height %d -> %d (+%d blocks), run id %d" % (
            start_height, end_height, end_height - start_height, self.run_id))

        if self.persistent_dir:
            self._mine_blocks(self.nodes[0], 1)
            end_height = self.nodes[0].getblockcount()
            self._save_chain_height(end_height)


if __name__ == '__main__':
    AssetAuthStressTest().main()
