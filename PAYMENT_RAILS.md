# PAYMENT RAILS — no-KYC receive, wired to what already exists

You own a finished payment stack: `~/payment_system/` (BTC on-chain +
Lightning + Monero, order tracking, license delivery, web UI). Zero
identification required to RECEIVE on the crypto rails. This doc maps it to
ConstraintOps and lists the only human steps left.

## The endpoint map

| Step | What happens | Human needed? |
|---|---|---|
| 1. Client picks a tier | `web_app.py` `/order/<product>` — prices now match ConstraintOps tiers | no |
| 2. Order created | system shows BTC/XMR address + amount (auto USD→crypto rate) | no |
| 3. Client pays from their wallet | on-chain or Lightning | no |
| 4. BTC: auto-verified via blockchain API; XMR: flagged "awaiting manual confirmation" | payment_checker.py | XMR: you eyeball your wallet |
| 5. Delivery | license key generated / you send the report | report = your human pass anyway |

## ConstraintOps prices now in config.py

`mess_to_map $100 · damage_triage $250 · sprawl_triage $250 ·
sprawl_triage_multi $500 · platform_survival $250/$500 · resilience_plan $500 ·
automation_risk $750` (legacy boardroom products kept for old orders)

## THE ONLY MISSING PIECES (human, ~30–60 min total)

1. **A BTC receive address** — from any wallet you control (self-custody:
   BlueWallet, Sparrow, Electrum; or custody-free Lightning: Strike/Wallet of
   Satoshi gives a Lightning address). Put it in the vault under
   `infra.payment_system` → `BITCOIN_ADDRESS` (and optionally
   `BITCOIN_LIGHTNING_ADDRESS` + `BITCOIN_LIGHTNING_ENABLED=true`).
2. **An XMR address** (optional but the most private rail) — from Feather or
   Monero.com wallet → vault `MONERO_ADDRESS`.
3. **Test the loop once** — `source ~/bin/vault-env && python main.py` (or
   web_app), place a fake order, confirm the address/amount displays.

## Critical honesty notes (creed: reveal, don't conceal)

- **Receiving crypto is no-KYC. Converting to spendable fiat is where ID
  usually enters** (exchanges require it). Know your local options: P2P
  platforms, crypto debit cards, direct crypto-for-goods, holding as savings.
  Plan the exit path BEFORE the first client pays.
- **Taxes are yours to figure.** Crypto income is still income almost
  everywhere. The ledger is honest; keep yours that way.
- **XMR = private by design; BTC = pseudonymous, NOT private.** Chain
  analysis is real. Don't promise clients privacy the rail doesn't give.
- Stripe stays OUT per operator constraint. If a corporate client ever
  insists on card payment, that's a future decision with future tradeoffs —
  not today's problem.

## Current state of this repo (dated 2026-09-11)

- `.env` retired → secrets sourced from `~/.concierge/vault.json` at runtime
  via `~/bin/vault-env` (working as designed)
- `PRICES` in config.py updated to ConstraintOps tiers ✅
- Wallet addresses: **NOT configured** ← the only blocker, human task
- `charges.log` shows selftests only — no real money has moved yet
