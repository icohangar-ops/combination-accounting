# combination-accounting

> **Cubiczan stack** — [CHP](https://github.com/Cubiczan/consensus-hardening-protocol) · [control-spine](https://github.com/Cubiczan/control-spine) · **You are here:** `combination-accounting`

**ASC 805 purchase accounting and de-SPAC reverse recapitalization.** Consideration, identifiable net assets at FV, NCI, previously held interest, goodwill or bargain gain, measurement-period adjustments, reverse-recap equity. Pre-combination control gaps do not disappear at close. `convergence` is M&A decision intelligence. This is the purchase-accounting engine.

Fair values are inputs. The engine does not appraise a customer relationship or decide who the accounting acquirer is. The control owner does. The engine produces the allocation they reperform.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What it produces

| Artefact | What a tester samples |
|---|---|
| Consideration transferred | Cash + equity FV + contingent FV + pre-combination replacement awards |
| Identifiable net | Assets FV − liabilities FV ± measurement-period adjustments |
| Goodwill / bargain | Aggregate minus identifiable net (acquisition mode) |
| Reverse recap | No goodwill; SPAC net assets recorded; issuance costs against APIC when flagged |
| Evidence pack | Mode, numbers, adjustment register, owner sign-off |

Cash 50m + equity 30m + contingent 5m + NCI 2m against identifiable net 70m → goodwill **17m**. That vector is in the tests.

## Quick start

```bash
pip install -e ".[dev]"
pytest -q
combination-accounting examples/deal.json --period "H1 2026" --owner "Controller"
```

## Compliance spine

Vendored `control-spine`. Fair values and the accounting-acquirer determination are foundation inputs. Reverse recap still produces no goodwill. Unsigned packs are `EXPLORING`. A named owner reaches `LOCKED`.

## MCP server

`src/combination_accounting/mcp_server.py` publishes the engine over Model Context Protocol: a thin wrapper in the `io.github.Cubiczan` namespace (stdio transport) whose tools — `allocate_deal` and `deal_evidence_pack` — call `combination_accounting.engine` and `combination_accounting.evidence` verbatim. All allocation logic lives in the engine module; the wrapper adds no logic, touches no network, and never appraises anything — fair values and the accounting-acquirer determination stay inputs.

```bash
uvx --from combination-accounting combination-accounting-mcp
# or from a checkout:
python -m combination_accounting.mcp_server
```
