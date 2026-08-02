# StegVerse Federal-Plus Security Baseline

## Policy

Applicable United States federal cybersecurity requirements are the minimum acceptable floor for StegVerse systems. StegVerse controls must meet or exceed the applicable baseline, remain fail-closed when evidence is missing, and avoid claiming compliance or certification without directly inspectable validation evidence.

## Required control posture

1. Determine the applicable federal baseline for each system, data type, deployment, customer, and operating jurisdiction before activation.
2. Record the selected baseline, version, applicability decision, evidence sources, exceptions, and compensating controls in repository-owned records.
3. Implement stronger controls where technically and operationally feasible, including least privilege, phishing-resistant authentication, cryptographic provenance, immutable evidence, separation of reasoning from execution, bounded dispatch, deterministic receipts, duplicate-execution prevention, tamper detection, recovery, and independent verification.
4. Treat federal requirements as minimums, not maximums. A control may not be weakened merely because a lower baseline would satisfy a procurement or compliance threshold.
5. Missing, stale, contradictory, or unverifiable evidence must produce `BLOCKED`, `REVIEW_REQUIRED`, or `FAILED`; it must never silently become `COMPLETE`.
6. Compliance statements require an identified framework, version, scope, assessor or validation path, evidence location, and expiration or reassessment condition.
7. Security controls do not themselves grant provider execution, deployment, custody, publication, release, admissibility, or activation authority.

## Enforcement ownership

- Canonical policy owner: `StegVerse-Labs/StegVerse-Healer` for scheduler, automation, evidence, and continuation controls.
- Repository owners: implement and validate repository-specific controls in their own handoffs and workflows.
- Release gates: prohibit activation when applicable baseline selection, evidence, or stronger-control justification is absent.
- Machine observers: retain exact control and validation receipts and expose machine-observable release conditions.

## Current application

The StegDeploy publication relay exceeds a simple scheduled check by requiring a verified v2 publication receipt, SHA-256 digest, consumer pull verification, source identity, duplicate suppression, bounded remediation, and fail-closed state retention before downstream dispatch.

## Authority boundary

This document is an engineering policy and control requirement. It does not assert FedRAMP, FISMA, NIST, CMMC, DoD, agency ATO, or other certification. Certification or compliance may be claimed only when the exact applicable framework and evidence have been independently validated and retained.
