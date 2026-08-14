#!/usr/bin/env python3
"""Generate unspendable Base58Check burn addresses for a version byte."""
import hashlib
import sys

B58 = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = bytearray()
    while n > 0:
        n, r = divmod(n, 58)
        out.append(B58[r])
    pad = 0
    for b in data:
        if b == 0:
            pad += 1
        else:
            break
    return (B58[0:1] * pad + out[::-1]).decode()


def b58check(version: int, payload20: bytes) -> str:
    raw = bytes([version]) + payload20
    chk = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    return b58encode(raw + chk)


def payload(label: str) -> bytes:
    return hashlib.sha256(f"RuckCoin burn {label}".encode()).digest()[:20]


LABELS = [
    "issueAsset",
    "reissueAsset",
    "issueSubAsset",
    "issueUniqueAsset",
    "issueMsgChannelAsset",
    "issueQualifier",
    "issueSubQualifier",
    "issueRestricted",
    "addTagBurn",
    "globalBurn",
]


def main() -> None:
    version = int(sys.argv[1]) if len(sys.argv) > 1 else 45
    for label in LABELS:
        addr = b58check(version, payload(label))
        print(f"{label:24} {addr}")


if __name__ == "__main__":
    main()
