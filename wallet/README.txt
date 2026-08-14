RuckCoin wallet
===============

This is the official local wallet. It runs on YOUR computer and talks to
a RuckCoin node on the same computer.

You do not need to know how mining works to use it.

First time
----------
1. Install Python 3 if you do not have it (python.org).
2. Start your RuckCoin node.
3. Double-click "Open Wallet.bat" (Windows) or run:
     python ruck-wallet.py
4. Open the page it prints: http://127.0.0.1:8870
5. If it says it cannot connect, open Settings and enter the same
   user / password / port as in your node's ruck.conf.

What you will see
-----------------
Home     Your address and how much you can spend
Receive  Give this K address to get paid
Send     Pay someone (cannot be undone)
Activity A list of what moved
Assets   Named tokens, if you have any
Mine     Optional. How new coins are created. You can skip this.
Settings Where the node lives on this computer

Safety
------
- Never send your node password to a stranger.
- Never type an address from memory. Copy it.
- RuckCoin addresses start with K. Ravencoin starts with R.
- This program only listens on 127.0.0.1 (this computer).
