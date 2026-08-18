# RuckCoin security policy

RuckCoin is currently operating a disposable public-test network. It is not approved for production custody, exchange deposits, withdrawals, or trading.

## Reporting a vulnerability

Use <https://ruckcoin.org/report.html> and select or write **Security**. Include affected version/commit, impact, reproduction steps, and a safe way to contact you. Do not include private keys, wallet files, RPC credentials, personal information, or live exploit payloads that are unnecessary to reproduce the issue.

Please do not open a public GitHub issue for an unpatched vulnerability. Ordinary bugs and documentation errors may use the public issue tracker.

The project will try to acknowledge a credible security report within seven calendar days. This is a best-effort target, not a service-level agreement. Coordinated disclosure timing will depend on severity, patch availability, and node-upgrade safety.

## Supported versions

Only the latest tagged RuckCoin release is considered for security fixes. The current test tag is `test-2026-08-15`; it remains test software. A production-support window will be published with any production release.

## Exchange emergencies

Exchange operators should use the same private report route, mark the report **Exchange emergency**, and immediately pause deposits/withdrawals if they observe an unexpected reorganization, peer isolation, conflicting chain tips, or a consensus/wallet defect.
