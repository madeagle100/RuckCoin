#!/usr/bin/env python3
"""Validate a RuckCoin node against the checked-in integration manifest."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_MANIFEST = Path(__file__).with_name("network-manifest.json")


class CliError(RuntimeError):
    pass


def call_cli(cli, datadir, *args):
    command = [cli]
    if datadir:
        command.append("-datadir=" + datadir)
    command.extend(str(arg) for arg in args)
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise CliError("{} failed: {}".format(" ".join(args), detail))
    return result.stdout.strip()


def call_json(cli, datadir, *args):
    output = call_cli(cli, datadir, *args)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise CliError("{} did not return JSON: {}".format(" ".join(args), exc))


def check_equal(errors, label, actual, expected):
    if actual != expected:
        errors.append("{}: expected {!r}, got {!r}".format(label, expected, actual))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", default="ruck-cli", help="path/name of ruck-cli wrapper")
    parser.add_argument("--datadir", help="node data directory passed to the CLI")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--require-production",
        action="store_true",
        help="fail unless the manifest is explicitly production listing-ready",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    options = parser.parse_args()

    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    expected_genesis = manifest["network"]["genesis"]
    expected_release = manifest["release"]
    errors = []
    warnings = list(manifest.get("warnings", []))

    if options.require_production and not manifest.get("production_listing_ready", False):
        errors.append("manifest is not production listing-ready")

    try:
        chain = call_json(options.cli, options.datadir, "getblockchaininfo")
        network = call_json(options.cli, options.datadir, "getnetworkinfo")
        genesis_hash = call_cli(options.cli, options.datadir, "getblockhash", "0")
        genesis = call_json(options.cli, options.datadir, "getblock", genesis_hash)
        txoutset = call_json(options.cli, options.datadir, "gettxoutsetinfo")
    except (OSError, CliError) as exc:
        errors.append(str(exc))
        chain = network = genesis = txoutset = {}
        genesis_hash = None

    if genesis_hash is not None:
        check_equal(errors, "RPC chain name", chain.get("chain"), manifest["network"]["rpc_chain_name"])
        check_equal(errors, "genesis hash", genesis_hash, expected_genesis["hash"])
        check_equal(errors, "genesis block hash", genesis.get("hash"), expected_genesis["hash"])
        check_equal(errors, "genesis merkle root", genesis.get("merkleroot"), expected_genesis["merkle_root"])
        check_equal(errors, "genesis time", genesis.get("time"), expected_genesis["time"])
        check_equal(errors, "genesis nonce", genesis.get("nonce"), expected_genesis["nonce"])
        check_equal(errors, "genesis bits", genesis.get("bits"), expected_genesis["bits"])
        check_equal(errors, "genesis version", genesis.get("version"), expected_genesis["version"])
        check_equal(errors, "client version", network.get("version"), expected_release["client_version"])
        check_equal(errors, "protocol version", network.get("protocolversion"), expected_release["protocol_version"])
        if not str(network.get("subversion", "")).startswith(expected_release["subversion_prefix"]):
            errors.append("unexpected subversion: {!r}".format(network.get("subversion")))

        peer_count = network.get("connections", 0)
        pause_below = manifest["exchange_policy"]["pause_below_peer_count"]
        if peer_count < pause_below:
            warnings.append(
                "peer count {} is below {}; deposits and withdrawals should be paused".format(
                    peer_count, pause_below
                )
            )
        if chain.get("headers", 0) > chain.get("blocks", 0):
            warnings.append("node is still syncing headers/blocks")
        if chain.get("warnings"):
            warnings.append("node warning: {}".format(chain["warnings"]))

    report = {
        "ok": not errors,
        "network_status": manifest.get("network_status"),
        "production_listing_ready": manifest.get("production_listing_ready", False),
        "height": chain.get("blocks"),
        "best_block_hash": chain.get("bestblockhash"),
        "utxo_total_ruck": txoutset.get("total_amount"),
        "connections": network.get("connections"),
        "errors": errors,
        "warnings": warnings,
    }

    if options.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("RuckCoin node validation: {}".format("PASS" if report["ok"] else "FAIL"))
        print("Network status: {}".format(report["network_status"]))
        print("Height: {}  Connections: {}".format(report["height"], report["connections"]))
        for warning in warnings:
            print("WARNING: " + warning)
        for error in errors:
            print("ERROR: " + error)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
