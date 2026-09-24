# StegVerse-Healer

StegVerse-Healer is the ecosystem's central scheduling, observation, repair-dispatch, and continuity service.

## Authority boundary

This repository is the only managed StegVerse repository permitted to own scheduled GitHub Actions workflows. Downstream repositories expose manual or bounded event-driven entrypoints and retain their own repository-specific logic and evidence.

Healer dispatch does not itself grant provider execution, deployment, custody, publication, release, Site activation, admissibility, or receipt-minting authority.

## Ecosystem Continuity Evaluator intake

StegVerse-Healer consumes non-PASS findings from the canonical Ecosystem Continuity Evaluator as read-only repair-dispatch input. `app/ece_finding_intake.py` preserves the exact finding/evaluation identity, hashes the accepted snapshot, starts Healer state at `DETECTED`, and carries `authority_effect=NONE_INTAKE_ONLY`.

ECE remains continuity-evaluation truth. Healer must not rewrite the underlying observation or claim recovery because work was acknowledged, queued, dispatched, retried, or completed. Recovery requires a later independent ECE evaluation that observes the predicate `PASS` with acceptable evidence and freshness.

The bounded periodic cycle implementation is `app/ece_periodic_evaluation.py`, with CLI entrypoint `app/run_ece_periodic_evaluation.py`. It consumes only already-local canonical source roots plus the resident runtime root. When a resident observation bundle is absent, it supplies an empty observation set to the canonical evaluator so continuity degrades to explicit `NOT_OBSERVED` findings rather than inventing green state. Generated evaluation, exact-byte Master Records custody/reconstruction, Healer intake, Site-safe projection, and cycle receipts are written under the resident runtime root; source repositories remain read-only. Scheduling for this cycle must use the existing reusable-task scheduler extension and must not create another scheduler.

## Current capabilities

- Central resident scheduler driven by `data/orchestrator_targets.json`; legacy fixed-UTC targets remain compatibility rows, while ST-018 is eligible only on validated resident HB(Δ) progression (2,160,000 references at the canonical 100 Hz oscillator). HB observation is scheduling evidence, not execution authority.
- Data-driven reusable-task scheduling through `data/reusable_task_schedule.json` inside that same sovereign scheduler path. A UTC-hour slot is idempotent after a retained reusable-task receipt reaches a recognized successful terminal state: legacy bounded tasks use `AUTOMATABLE_STEPS_EXHAUSTED`, while fully closed reusable lifecycles use `ENTROPY_RECOVERY_RECORDED`. Failed or boundary-only receipts remain retryable instead of poisoning the slot, but retry cadence and attempts are bounded by the task's schedule record.
- Scheduled reusable tasks keep source and resident runtime distinct: task source comes from the already-materialized local repository map, execution state and reusable-task receipts live under the resident runtime identified by `STEGVERSE_HEARTBEAT_ROOT` or canonical local resident-root discovery. When no valid root is observed but `RT-SOVEREIGN-SOURCE-REFRESH-001` is enabled, the existing Healer carrier may pass the canonical resident-root path as a non-authorizing materialization target to the existing neutral scheduler so that the existing local-only source-refresh task can populate it; the carrier then re-runs root discovery and remains blocked unless authentic resident markers are observed. Schedules without that source-refresh task still fail closed at `RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED`. Source checkouts are never treated as resident runtime proof.
- The Healer reusable-task carrier retains its StegBrowser resident-root observation packet at `receipts/sovereign-host/stegbrowser-resident-custody-root-observation.latest.json` under the observed resident runtime root, or under the non-authorizing canonical materialization target when source refresh is enabled and no valid root is yet observed. This retained packet is an observation surface only: it records task/COSV binding, packet state, root source, matched marker relpaths, and authority fields, but it never proves runtime completion or request consumption by itself.
- `RT-NATIVE-EMAIL-ACTION-MONITOR-001` is scheduled hourly through the existing reusable-task trigger and canonical `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` path. A failed slot may retry no sooner than every 15 minutes and at most four times in that UTC-hour slot; a new hour receives a new deterministic slot ID. No second mailbox monitor or scheduler is created.
- `RT-STEGBROWSER-RUNTIME-CONSUMPTION-001` is carried through the same neutral reusable-task scheduler and standing sovereign Healer carrier for Goal `STEG-BROWSER-RUNTIME-CONSUMPTION-001` / COSV `40000100100000`. It selects the existing `ADMITTED-EPHEMERAL-STEGOS-NODE` path and does not require Remote Desktop, a particular device, a second scheduler, or a second user-operated device. The schedule binding is source/configuration only; authentic runtime-consumption receipts remain the completion authority.
- `RT-STEGOS-AI-PREEXECUTION-RUNTIME-PROOF-001` is carried through the same neutral reusable-task scheduler and standing sovereign Healer carrier for Goal `STEGOS-AI-PREEXECUTION-RUNTIME-PROOF-001` / COSV `40000100100000`. It selects the existing `ADMITTED-EPHEMERAL-STEGOS-NODE` path with automatic advancement and does not require Remote Desktop, a second scheduler, a second runtime plane, or a second user-operated device. This carrier binding repairs invocation reachability only; authentic resident materialization, WorkerCoordinator, Interlock/InTr, target-state, and Master Records receipts remain the completion authority.
- `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` is carried through the same neutral reusable-task scheduler and standing sovereign Healer carrier for Goal `HYGIENE-CAUSAL-ROOTS-001` / COSV `10100000100000`. Its schedule parameters bind only `only_consumer=canonical_work_coordination` and `goal_task_id=HYGIENE-CAUSAL-ROOTS-001`; the neutral scheduler injects local source/runtime roots. No Remote Desktop, second scheduler, second runtime plane, Site route, or second user-operated device is required. Source reachability is not an authentic Task Registry `CONTINUE` receipt.
- `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` is also bound to Goal `CONVERSATION-EVIDENCE-INGESTION-CUSTODY-001` / COSV `20011000100000` through the same neutral scheduler and standing sovereign Healer carrier. Its task-scoped invocation key and parameters carry only `only_consumer=canonical_work_coordination` plus the exact Goal Task ID; no device inventory, second scheduler, second runtime, or second user-operated device is introduced. Authentic WorkerCoordinator claim/fence and Master Records custody remain the completion authority.
- `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` is bound to Goal `ERL-HOUSEHOLD-ECONOMIC-CONDITIONS-SITE-001` / COSV `10100000100000` through the existing neutral scheduler and standing sovereign Healer carrier. It carries only the exact `canonical_work_coordination` selector and Goal ID; WorkerCoordinator retains claim/fence authority, TV/TVC retains BEA credential authority, and Site public activation remains false until governed ERL output plus served-body proof. No device inventory, second scheduler, second runtime, or second user-operated device is required.
- The native-email reusable slot may receive the already-materialized KnowledgeVault path through `STEGVERSE_KV_ROOT` or `STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT`. These are non-secret local path bindings only; Healer does not mount a provider or acquire credentials. Missing KV materialization blocks failure-email archival rather than bypassing KV persistence; retry state suppresses tight provider loops while preserving bounded recovery.
- For governed native-email provider mutation, the scheduler may augment its already-local repository map from the existing `SV-DN1-PRODUCTION-SOURCE-PREP-001` v2 receipt. It accepts the SDK, StegCore, Core-Lite, and Master Records roots only when that receipt is `COMPLETE`, all four SHA-256 source identities are present, migration anchors were verified, no network/GitHub/credential source acquisition occurred, and required runtime marker files still exist. An absent or invalid source-prep receipt adds no roots and creates no fallback fetch.
- Unauthorized downstream schedule auditing.
- Configured cross-repository workflow dispatch.
- YAML correction and reusable repair workflows.
- Evidence-derived StegDeploy publication relay.
- Durable machine-readable migration, dispatch, blocker, and continuity records.

## Continuation records

Read these before modifying scheduling or dispatch behavior:

- `docs/HEALER_MIRROR_HANDOFF.md`
- `docs/NATIVE_EMAIL_REUSABLE_SCHEDULE_MIRROR_HANDOFF.md`
- `docs/STEGBROWSER_RUNTIME_CONSUMPTION_CARRIER_BINDING_MIRROR_HANDOFF.md`
- `docs/STEGOS_AI_PREEXECUTION_RUNTIME_PROOF_CARRIER_BINDING_MIRROR_HANDOFF.md`
- `docs/HEALER_ACTIVATION_PLAN.md`
- `docs/ECOSYSTEM_CONTINUITY_HEALER_INTAKE_MIRROR_HANDOFF.md`
- `docs/ECOSYSTEM_CONTINUITY_PERIODIC_CYCLE_MIRROR_HANDOFF.md`
- `data/orchestrator_targets.json`
- `data/reusable_task_schedule.json`
- `data/summary/single_scheduler_migration.json`

## Validation

Repository validation is performed by the `Test Readiness` workflow. Runtime activation claims require observed resident/runtime evidence and retained receipts; configuration or source merge alone is not activation proof.


### Separate HIL receiver projection

Service Gateway activation keeps Universal InTr and the machine-owned HIL receiver on distinct loopback bindings. The receiver projection is enabled only from a validated pathless loopback origin and must pass exact HIL readiness through the Gateway before being reported ready.

### Native-email source-prep reachability

When the native-email governance source-preparation v2 receipt is absent, the existing Healer carrier now invokes the already-canonical `.github/scripts/refresh_and_execute_resident_task.py` bridge for `SV-DN1-PRODUCTION-SOURCE-PREP-001`. The call uses the existing resident runtime, WorkerCoordinator independent-task-control admission, COSV `50000000102000`, and only the four already-local non-secret SDK/StegCore/Core-Lite/Master Records root locators. Healer then re-reads the canonical source-prep receipt before delegating to the neutral reusable-task scheduler. This is reachability repair only; it creates no scheduler, dispatcher, WorkerCoordinator, source transport, credential route, custody store, or device prerequisite.

- Native-email governance-root reuse now accepts an SV-DN1 production-source-prep v2 receipt only when it is bound to the canonical source-prep task/worker, carries a WorkerCoordinator claim ID exactly matching its fencing generation above the source-prep minimum fence, and proves the current sha256-content-manifest identity policy. Receipt shape alone no longer authorizes governance-root reuse.

## ST-018 resident HB(Δ) schedule (candidate; governed activation pending)

ST-018 is selected by the existing sovereign Healer scheduler after a validated independent resident heartbeat carrier observation, not by 00/06/12/18 UTC. One six-hour-equivalent period is 2,160,000 canonical 10 ms references. First authentic observation permits a bootstrap execution. A successful ST-018 PASS yields an atomic resident-local content-hashed checkpoint; subsequent schedule cycles require another full Δ. Failed executions may retry only after 90,000 HB references and at most four attempts per 2,160,000-reference window. Missing, malformed, regressing or unauthenticated carrier state and invalid checkpoints block the target with an explicit scheduling outcome. A restart recovers the exact checkpoint from the existing resident runtime root; no UTC fallback is permitted for ST-018. No new heartbeat, scheduler, worker, runtime, credential provider or repository-writeback authority is introduced. WorkerCoordinator still independently owns admission/claim/fence; Interlock/InTr and Master Records remain authoritative for applicable governed transitions. The local scheduling checkpoint is not a Master Records closure receipt.
