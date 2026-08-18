#!/usr/bin/env python3
"""Calculate RuckCoin emission and a live circulating-supply upper bound."""

import argparse
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path


DEFAULT_MANIFEST = Path(__file__).with_name("network-manifest.json")


def subsidy_emitted_satoshis(height, initial_subsidy, halving_interval):
    """Maximum subsidy issued at heights 1..height; genesis is excluded."""
    if height <= 0:
        return 0
    total = 0
    start = 1
    while start <= height:
        era = start // halving_interval
        reward = initial_subsidy >> era if era < 64 else 0
        if reward == 0:
            break
        end = min(height, ((era + 1) * halving_interval) - 1)
        total += (end - start + 1) * reward
        start = end + 1
    return total


def cli_json(cli, datadir, *args):
    command = [cli]
    if datadir:
        command.append("-datadir=" + datadir)
    command.extend(str(arg) for arg in args)
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout)


def coins_to_satoshis(value, coin):
    return int(Decimal(str(value)) * coin)


def format_coins(satoshis, coin):
    return format(Decimal(satoshis) / Decimal(coin), ".8f")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--height", type=int, help="offline height; live node height if omitted")
    parser.add_argument("--cli", default="ruck-cli", help="path/name of ruck-cli wrapper")
    parser.add_argument("--datadir", help="node data directory passed to the CLI")
    parser.add_argument("--offline", action="store_true", help="calculate emission only")
    parser.add_argument("--human", action="store_true", help="emit a short text report")
    options = parser.parse_args()

    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    money = manifest["money"]
    coin = money["coin_satoshis"]
    warnings = list(manifest.get("warnings", []))
    live = not options.offline

    if live:
        try:
            chain = cli_json(options.cli, options.datadir, "getblockchaininfo")
            txoutset = cli_json(options.cli, options.datadir, "gettxoutsetinfo")
        except (OSError, RuntimeError, json.JSONDecodeError) as exc:
            print("Unable to query node: {}".format(exc), file=sys.stderr)
            return 2
        height = chain["blocks"] if options.height is None else options.height
        if options.height is not None and options.height != chain["blocks"]:
            warnings.append("requested height differs from the live node height")
        utxo_satoshis = coins_to_satoshis(txoutset["total_amount"], coin)
    else:
        if options.height is None:
            parser.error("--offline requires --height")
        height = options.height
        utxo_satoshis = None

    if height < 0:
        parser.error("height cannot be negative")

    emitted = subsidy_emitted_satoshis(
        height,
        money["initial_subsidy_satoshis"],
        money["halving_interval_blocks"],
    )
    burned = None
    burn_details = []

    if live:
        burned = 0
        for item in manifest["burns"]:
            try:
                balance = cli_json(
                    options.cli,
                    options.datadir,
                    "getaddressbalance",
                    json.dumps({"addresses": [item["address"]]}, separators=(",", ":")),
                )["balance"]
            except (OSError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
                warnings.append(
                    "could not read burn address {} (is addressindex=1?): {}".format(
                        item["address"], exc
                    )
                )
                burned = None
                burn_details = []
                break
            burned += balance
            burn_details.append(
                {"purpose": item["purpose"], "address": item["address"], "balance_satoshis": balance}
            )

    circulating = utxo_satoshis - burned if utxo_satoshis is not None and burned is not None else None
    report = {
        "network_status": manifest["network_status"],
        "production_listing_ready": manifest["production_listing_ready"],
        "height": height,
        "maximum_subsidy_emitted_satoshis": emitted,
        "maximum_subsidy_emitted_ruck": format_coins(emitted, coin),
        "utxo_total_satoshis": utxo_satoshis,
        "utxo_total_ruck": format_coins(utxo_satoshis, coin) if utxo_satoshis is not None else None,
        "known_burn_satoshis": burned,
        "known_burn_ruck": format_coins(burned, coin) if burned is not None else None,
        "circulating_upper_bound_satoshis": circulating,
        "circulating_upper_bound_ruck": format_coins(circulating, coin) if circulating is not None else None,
        "burn_addresses": burn_details,
        "warnings": warnings,
        "methodology": (
            "UTXO total minus balances at consensus burn addresses. This is an upper bound: "
            "it still includes immature, locked, and possibly lost coins."
        ),
    }

    if options.human:
        print("Network: {} (production ready: {})".format(report["network_status"], report["production_listing_ready"]))
        print("Height: {}".format(height))
        print("Maximum subsidy emitted: {} RUCK".format(report["maximum_subsidy_emitted_ruck"]))
        if report["utxo_total_ruck"] is not None:
            print("UTXO total: {} RUCK".format(report["utxo_total_ruck"]))
        if report["circulating_upper_bound_ruck"] is not None:
            print("Circulating upper bound: {} RUCK".format(report["circulating_upper_bound_ruck"]))
        for warning in warnings:
            print("WARNING: " + warning)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
