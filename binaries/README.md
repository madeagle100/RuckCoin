# RuckCoin binaries

Official downloads for people who are not building from source.

Until a GitHub Release is cut, the files live with the site:

- `website/downloads/ruckcoin-wallet.zip` — wallet (Windows / Linux / macOS)
- `website/downloads/ruckcoin-linux-x86_64.zip` — node for Ubuntu 24.04 x86_64
- `website/downloads/SHA256SUMS.txt` — SHA-256 of those files

There is **no Windows `ravend.exe` and no macOS binary** in this tree yet.
Windows can run the Linux node inside WSL. Mac builds from source.

Do not use Ravencoin’s GitHub releases. Those are a different coin.

Rebuild the zips from the repo root (PowerShell):

```
contrib/pack-stranger.ps1
```

Public announcement still waits on a height-0 reset. These packs are so a stranger can run the software on their own computer.
