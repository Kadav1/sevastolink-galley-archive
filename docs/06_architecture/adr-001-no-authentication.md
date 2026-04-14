# ADR-001: No Authentication in v1

**Status:** Accepted  
**Date:** 2026-04-05

## Context

Sevastolink Galley Archive is a local-first, self-hosted application designed for a single user on a trusted home LAN. The intended deployment model is:

- API and UI run on one machine, accessed by one user over the home network.
- No external internet exposure in normal operation.
- No multiple users, roles, or shared access requirements.

## Decision

**v1 ships with no authentication layer.** Every device on the home LAN can read and write all data without credentials.

This is an intentional product decision, not an oversight.

## Rationale

- Adding authentication (session tokens, API keys, JWT, etc.) introduces meaningful complexity — key management, expiry, CSRF protection, secure storage — that has no payoff for a single-user private archive.
- The threat model is a trusted LAN: an attacker would already need physical access to the network.
- Every AI workflow already has a manual approval step. There is no path where unauthenticated access leads to silent data loss.
- CORS is configured to `allow_origins = settings.cors_origins` (default: the LAN subnet). This is the only network boundary — it is not a security boundary.

## Known Risks

| Risk                                                    | Likelihood | Severity | Mitigation                                                                 |
| ------------------------------------------------------- | ---------- | -------- | -------------------------------------------------------------------------- |
| IoT or guest device on flat LAN reads/deletes recipes   | Low        | Medium   | Segment IoT devices onto a separate VLAN                                   |
| Port accidentally forwarded to the internet             | Low        | High     | Bind API to `127.0.0.1` or LAN IP, never `0.0.0.0` on a public-facing host |
| Malicious script on another LAN device modifies archive | Very low   | Medium   | Backup regularly (`scripts/backup/backup.sh`)                              |

The security audit (2026-04-01) documents these risks in detail and recommends re-evaluation if the deployment context changes.

## Consequences

- Any future multi-user or remote-access feature requires adding authentication before any other work.
- Optional API key authentication can be layered on without changing the data model — the `app_settings` table can store a hashed key.
- If network isolation is weak, an optional `GALLEY_API_KEY` environment variable can be added in a future patch release.

## Review Trigger

Revisit this decision if:

- A second user needs access to the archive, or
- The deployment host is reachable from the internet.
