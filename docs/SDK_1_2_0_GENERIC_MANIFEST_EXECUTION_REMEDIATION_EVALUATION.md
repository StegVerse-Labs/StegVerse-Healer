# StegVerse-Healer Remediation Evaluation — SDK 1.2.0 Generic Manifest Execution

Date: 2026-09-20

## Request identity

- Request ID: `SDK-1.2.0-GENERIC-MANIFEST-EXECUTION-REMEDIATION-001`
- Originating Goal: `SDK-TT-PURPOSE-BOUND-WORKER-RUNTIME-PROOF-001`
- Originating COSV: `71000000111111`
- Owning domain: `StegVerse SDK 1.2.0`
- Current-version day-one baseline: `b8d763619290b2c9d6ea49aa1b46f3eea4e250eb` (`1.2.0.dev0`)
- Clean pre-repair current-version state: `8a28d063bce97e3d247b337c89400da406fcfed1` (`1.2.0`)
- Task Registry generation observed: `132`
- Authority transfer: `NONE`

## Exact observed evidence

The exact clean SDK 1.2.0 source at `8a28d063...` was transported without merging any repair code and executed through the public SDK interface.

Using the intended shared evaluator source:
`inspection/examples/sdk-tt-shared-source.json`

all three public commands completed and returned their local semantic expectations as satisfied:

| Test | Manifest SHA-256 | Result SHA-256 | Returned authority effect |
|---|---|---|---|
| 1 | `1887e9460501d4c2d0de0fe9f3d3cff2bc077b62952ada791e93d74ba6719e03` | `c66014bea93279a5cc8081a7838d8f71b1f7bf7fcf4880da6a732de3dc2df9f6` | `NONE_MANIFEST_DRIVEN_SDK_TEST` |
| 2 | `869cdc70d3ab1255ffdaac429f7dbc0c93c56d244d410f79d3d43eb9983d8816` | `c3d5772abe18157c80e07c43f1910f921b92923004432f37b7bc906f0d7c351b` | `NONE_EVALUATOR_MANIFEST_DRIVEN_SDK_TEST` |
| 3 | `c9890b212cba9c1b65566dcc900ccc882d7f1dc7346d368b12bfcff06d8d488c` | `3762d5483850dc3cb75040aed78ed480735bad7b2fb2f73aee21d9e1f5772bb3` | `NONE_EVALUATOR_MANIFEST_DRIVEN_SDK_TEST` |

The current public `run-manifest` route resolves Test 1 to
`stegverse.purpose_bound_worker_processor.execute_manifest`, which directly calls the SDK-local purpose-bound worker implementation.

Tests 2 and 3 resolve to
`stegverse.atomic_task_worker_processor.execute_manifest`, which directly calls the SDK-local atomic task/worker implementation.

Those returned packets do not establish WorkerCoordinator claim/fence, Interlock/InTr state-transition admission, per-transition Master Records closure, deterministic replay, reconstruction PASS, or exact receipt/reconstruction digest equality. Therefore the local semantic PASS markers are not authentic governed completion evidence.

A second exact defect is also reproducible from the clean version: the README's published Test 1 command uses `inspection/examples/sdk-test1-source.json`, but that file has no `payload.text`; `run-manifest` rejects it with `manifest payload.text must be a string for purpose_bound_worker`. The shared-source fixture succeeds.

## Healer trigger evaluation

Disposition: `AUTHORIZED_TRIGGER_MATCHED_APPLY_BOUNDED_REMEDY`

Basis:
1. the defect is deterministic on the exact clean current-version source;
2. it blocks the originating Goal's next required authentic transition;
3. the owner is the SDK 1.2.0 execution integration itself;
4. the bounded remedy can preserve the current version and its prior 565-commit capability history;
5. no new scheduler, runtime, WorkerCoordinator, transition authority, credential authority, custody plane, carrier, or second-device dependency is required.

## Derived bounded remediation task

Healer derives:

`SDK-1.2.0-GENERIC-MANIFEST-EXECUTION-REMEDIATION-001`

Required result:

`manifest is the variable execution input -> versioned SDK resolves processing capability -> existing WorkerCoordinator/Interlock-InTr/TV-TVC/Master Records path -> replay/reconstruction -> SDK return`

The remediation MUST:
- start from exact SDK `8a28d063...`;
- preserve unrelated 1.2.0 capabilities;
- remove test-specific execution authority from purpose/atomic processors rather than adding another test runtime;
- make the generic `run-manifest` completion fail closed unless its event chain has the required governed custody/replay/reconstruction closure;
- keep Test 1, Test 2, Test 3, and any Test 4 variation as manifested input differences, not execution-path differences;
- repair the published Test 1 source example or command so the documented public invocation is executable;
- return remediation evidence to the originating Goal before further promotion.

## Explicit non-authorizations

This evaluation does not make Healer an execution authority or prerequisite. WorkerCoordinator remains assignment authority, Interlock/InTr transition authority, TV/TVC credential authority, and Master Records custody/reconstruction authority. GitHub Actions remain validation/evidence transport only.
