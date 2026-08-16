# Run RuckCoin on your computer

The public network is not open. This is how you run the software locally.

Pick your OS. Different computers get different files.

| You have | Wallet | Node |
| --- | --- | --- |
| Windows | `ruckcoin-wallet.zip` | No `.exe` yet. Linux zip inside WSL, or build. |
| Linux (Ubuntu 24.04 x86_64) | same wallet zip | `ruckcoin-linux-x86_64.zip` |
| macOS | same wallet zip | Build from source |

Site version of this page: `website/run.html`.

## ruck.conf

```
server=1
listen=1
port=8867
rpcport=8866
rpcuser=ruck
rpcpassword=YOUR_OWN_PASSWORD
rpcallowip=127.0.0.1
rpcbind=127.0.0.1
miningrequirespeers=0
# addnode=SEED_HOST:8867
```

Windows path: `%APPDATA%\Ruck\ruck.conf`  
Linux / macOS: `~/.ruck/ruck.conf`

`addnode` stays commented until the official site prints a host.

## Build from source

```
./autogen.sh
./configure --without-gui --disable-tests --disable-bench
make
```

Berkeley DB 4.8 is required for the wallet. See `doc/build-unix.md`.
The binaries are still named `ravend` and `raven-cli`. Wrappers: `contrib/ruckd`, `contrib/ruck-cli`.
