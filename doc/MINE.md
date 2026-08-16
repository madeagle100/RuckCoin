# Mine RUCK (practice)

Use **your** K address from the wallet Receive tab. There is no project
mining address and no project RPC password.

Public mining is not open. Coins on the private test chain do not carry over.

## 1. Node

Start a node. See `doc/RUN.md` / `website/run.html`.

`ruck.conf` needs `server=1` and an RPC password you chose.

Solo with no peers: add `bypassdownload=1` if `getblocktemplate` says the
node is not connected.

## 2. Stratum proxy + GPU miner

Most miners speak stratum, not raw RPC. Example (kralverde proxy):

```
python stratum-converter.py 54325 127.0.0.1 YOUR_RPC_USER YOUR_RPC_PASSWORD 8866 false
```

Then:

```
kawpowminer -P stratum+tcp://YOUR_K_ADDRESS.worker@127.0.0.1:54325
```

T-Rex: `t-rex -a kawpow -o stratum+tcp://127.0.0.1:54325 -u YOUR_K_ADDRESS -p x`

## Notes

- Algorithm after genesis is KAWPOW.
- Fast GPUs can hit `time-too-old` if blocks come faster than one per minute.
- Site page: `website/mine.html`.
