# Coinbase StegDeploy Sovereign Gateway Activation Mirror Handoff

Updated: 2026-08-27
Repository: `StegVerse-Labs/StegVerse-Healer`
Canonical upstream source: `StegVerse-org/LLM-adapter`
Canonical downstream owner: `StegVerse-Labs/TVC#119`

## Goal

Materialize and verify the already-merged Coinbase SKAP readiness/ingress routes on the existing sovereign StegDeploy runtime carrier without creating a second scheduler, second heartbeat, second gateway, provider credential path, or third-party production dependency.

## Authority

```text
credential_authority: TV/TVC
github_token_runtime_authority: NONE
render_role: FALLBACK_ONLY
healer_role: bounded sovereign execution carrier
heartbeat_authority_effect: NONE
gateway_credential_value_access: false
gateway_decryption_authority: false
gateway_execution_authority: NONE
provider_operation_authority: NONE
```

The handler may consume only an already-local LLM-adapter source tree and a non-secret TVC no-value decision receipt for role `service_gateway_coinbase_skap_ciphertext_intake`. It must never fabricate that receipt.

## Canonical source already complete

LLM-adapter source has already merged:

- deployed-entrypoint Coinbase readiness/ingress repair: PR #204 / merge `244902d475c12ee6bff7dd67e4dfacb4e2357ca7`
- StegDeploy sovereign primary-runtime binding: PR #205 / merge `0ec44419ada49147feb1866abfa6fe4fb4d0bbb2`
- Render compatibility deployment: optional fallback only; prior build failure from exhausted build minutes is not a production prerequisite.

## This implementation lane

Reuse `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` and `app/sovereign_scheduler.py`.

Install one fixed local target:

```text
repo: StegVerse-org/LLM-adapter
workflow: coinbase-stegdeploy-sovereign-gateway
handler: app/coinbase_stegdeploy_gateway.py
scheduler: existing StegVerse-Healer sovereign scheduler
```

Expected local sequence:

```text
already-local LLM-adapter source
+ already-local non-secret TVC no-value decision receipt
-> scripts/stegdeploy_bootstrap.py deploy
-> local Docker Compose build with pull_policy=never
-> GET http://127.0.0.1:8000/api/coinbase/skap/readiness
-> require READY + TV/TVC + DEVICE_TO_KV + gateway_execution_authority=NONE
-> secret-free local activation receipt
```

## Hard fail-closed boundaries

- no GitHub token/PAT;
- no provider credential/private key;
- no network source clone/fetch/pull;
- no Render/Vercel/Cloudflare authority;
- no fabricated TVC decision;
- no production-route claim from loopback readiness;
- no SKAP Vault admission claim from Gateway staging readiness;
- no Coinbase provider operation;
- no order/trade/settlement authority.

## Completion distinction

Local sovereign Gateway readiness is not the production public HTTPS route.

This lane becomes source-complete when the fixed handler, scheduler binding, target registration, tests, and this handoff are merged and validated.

Actual runtime remains open until a real sovereign scheduler execution produces a local Gateway readiness receipt. Public route observation remains a separate downstream predicate owned by the Coinbase/Site/TVC activation chain.

## Downstream chain

```text
real sovereign Gateway local readiness
-> production HTTPS route observation
-> TVC current P-256 recipient liveness / READY_FOR_OWNER_INGRESS
-> current-iPhone WebAuthn/StegID + browser-local sealing
-> DEVICE->KV
-> KV->SKAP_VAULT
-> Coinbase endpoint/session/grant/capability/fees
-> StegFin #84 explicit approval
-> max-$10 bounded maker proof
-> settlement/reconciliation/repeat loop
```

User action required: NONE until READY_FOR_OWNER_INGRESS plus production public route are genuinely observed.
