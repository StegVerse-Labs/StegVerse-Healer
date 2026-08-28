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


## Merge / validation evidence

```text
PR: StegVerse-Labs/StegVerse-Healer#41
merge: 1a6dacf80b84e62b2c8709f9dcc75765cea1f5f7
source state: MERGED_MAIN
scheduler target installed: true
second scheduler created: false
second heartbeat created: false
```

Hosted Test Readiness run `33118079568`, job `98677773520`, passed the repository smoke suite, deterministic Healer tests, credential refusal, anonymous exact-source retrieval and validation-only authority checks on the prior semantic PR head. The final branch-only change before merge minimized JSON formatting churn and did not alter target semantics; no separate exact-final-head hosted run is claimed.

Runtime distinctions remain:

```text
source merged: true
real sovereign scheduler execution receipt: NOT OBSERVED
local Coinbase Gateway READY: NOT OBSERVED
production public HTTPS route: NOT OBSERVED
TVC READY_FOR_OWNER_INGRESS: NOT OBSERVED
```

The next runtime attempt may proceed only when the already-local TVC tree contains the canonical non-secret no-value decision receipt. Missing decision/runtime/Docker prerequisites must remain BLOCKED.


## TVC decision availability + consumer hardening

The downstream TVC decision prerequisite is now source-materialized and hosted-validated:

```text
StegVerse-Labs/TVC PR #173
merge: e8813e81494deb8e8563763675b5123e360397e6
receipt: receipts/service-gateway/coinbase-skap-intake-decision.json
Stage Drain Validation 33118626226: SUCCESS
Capability Broker Validation 33118626234: SUCCESS
credential material: NONE
```

The Healer consumer now verifies that decision before any deploy attempt:

```text
Healer PR #42
merge: a60e9d6717b4784591dffca8147b0b4afda2d468
Test Readiness 33118760520: SUCCESS
schema/digest/SHA-256 bindings: REQUIRED
```

Source prerequisites for an admitted local StegDeploy attempt are now installed. Actual scheduler execution and local/public route observations remain unobserved.


## Downstream sovereign route discovery source complete

The local runtime target's downstream route-discovery contract is now source-complete:

```text
LLM-adapter node advertisement PR #208:
  merge 479b8caad6504317603e60661f2f79d7fd04afcc
TVC advertised-route observer PR #179:
  merge f883fa2a9ed01a3bba78510a9216b17eb7dffac0
  Stage Drain Validation 33119463670 SUCCESS
  Capability Broker Validation 33119463674 SUCCESS
```

After a real local StegDeploy execution, the node itself can advertise Coinbase routes and TVC can consume them without an out-of-band hostname. Actual public TLS ingress/reachability remains separate and unobserved.


## Native TLS runtime locator integration — 2026-08-27

Upstream native TLS source is now merged and hosted-validated:

```text
StegVerse-org/LLM-adapter PR #209
merge: 10a6f6247771b2a85b07f5f19810403c3acde513
Coinbase SKAP Service Gateway Validation: 33121152939 SUCCESS
global validate: 33121152794 SUCCESS
TLS termination: UVICORN_NATIVE
reverse proxy required: false
Render/Cloudflare required: false
```

The existing Healer target now accepts optional path-only runtime locators:

```text
STEGVERSE_SERVICE_GATEWAY_TLS_CERT_FILE
STEGVERSE_SERVICE_GATEWAY_TLS_KEY_FILE
STEGVERSE_SERVICE_GATEWAY_TLS_BIND_ADDRESS
STEGVERSE_SERVICE_GATEWAY_TLS_PORT
```

These variables are locators/configuration only; certificate/private-key bytes are not read into the Healer receipt and are not copied into the child environment as secret values. Certificate/key locators must be paired and materialized locally before the TLS attempt.

Behavior:

```text
no TLS locators
-> existing local HTTP StegDeploy readiness only
-> production_public_route_observed=false

paired TV/TVC TLS locators
-> existing LLM-adapter deploy-tls bootstrap
-> native Uvicorn TLS
-> local HTTPS readiness
-> production_public_route_observed=false
-> public_certificate_hostname_verified=false
```

A local TLS-ready receipt remains insufficient for production route activation. TVC must still independently observe the advertised HTTPS node/readiness route with normal hostname/certificate verification.

No user-operated second machine and no manual shell step are introduced.


## Resident worker propagation merged

The TLS-capable Healer target is now reachable from the existing machine-owned sovereign worker without widening credential authority.

```text
Healer PR #43:
  merge 7aa88c39d5e46402e3368b5ebd81d27a773ce93d
  Test Readiness 33121314608 SUCCESS

StegVerse-Labs/.github PR #328:
  merge 583f3277c7eee9f0d12ab63280d31fbbc278aa85
  Heartbeat Worker Project 33121525095 SUCCESS
  Organization control-plane validation 33121525130 SUCCESS
```

Only the four TLS path/non-secret config locators can cross the worker boundary. Provider/Master-Records/GitHub tokens and certificate/private-key bytes do not.

Current runtime state remains:

```text
SHWP-DURABLE-RUNTIME-ACTIVATION: BLOCKED_ON_ELIGIBLE_SOVEREIGN_NODE_DECLARATION
G18 claim/fence: MACHINE_OWNED / fence18
local TLS Gateway receipt: NOT OBSERVED
public HTTPS route: NOT OBSERVED
user action required: false
heartbeat dependency: false
```


## TVC TLS adoption receipt auto-discovery

The upstream TVC lane now has a bounded, credential-model-approved adoption/validation step for already-materialized Service Gateway TLS files:

```text
StegVerse-Labs/TVC PR #202
merge: 0ca30b7806d2a96d9a256a7cd9fa0702f718a5e2
TVC Credential Model Consistency Validation: 33139239831 SUCCESS
Coinbase Gateway Stage Drain Validation: 33139239828 SUCCESS
receipt schema: stegverse.tvc.service_gateway_tls_material_adoption/v1
default resident receipt: /var/lib/stegverse/tvc/service-gateway-tls/latest.json
classification: CONSISTENT_TARGET_UNPROVEN_RUNTIME
```

Healer may now discover that same-host receipt automatically when explicit TLS path locators are absent. It requires the exact TVC schema/state/digest, TV/TVC credential authority, Gateway/provider authority NONE, verified certificate pair/hostname/time validity, all acquisition/issuance/renewal/revocation flags false, and both locators confined beneath the TV/TVC resident credential root.

Resolution precedence:

```text
paired explicit TV/TVC path locators
  -> bounded compatibility override

else valid TVC resident TLS adoption receipt
  -> automatic native-TLS locator discovery

else
  -> existing local HTTP readiness mode only
```

Healer reads no certificate/private-key bytes. The LLM-adapter native TLS bootstrap remains responsible for final pair/permissions verification immediately before local TLS execution.

This source integration does not claim that an authentic TVC adoption receipt currently exists, that native TLS executed, or that a production public HTTPS route is observed.
