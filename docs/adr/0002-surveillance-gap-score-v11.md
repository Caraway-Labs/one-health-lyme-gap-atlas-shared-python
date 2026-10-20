# 0002: Surveillance Gap Score v1.1

Status: Accepted
Date: 2026-10-19
Decision owner: Product owner, Shared Python #32

## Context
The v1.0 hard cutoff forced the whole score to zero for published floors >=10.
Research #31 compared equations on one pinned governed snapshot.

## Decision
Implement the owner's final Smooth k=50 equation. Preserve weights, missing H75,
classification thresholds, underlying data and all ML outputs. k50 is a product
decision, not a claim of demonstrated scientific optimality. See
[the method contract](../surveillance-gap-score-v1.1.md).

## Consequences
ScoreSettings becomes the v1.1 contract and rejects breakpoint arguments.
Package 2.0.0 reflects changed scoring semantics; scoring version is v1.1.
Historical behavior is isolated in LegacyScoreSettings. API/Web must upgrade
with generated types, incidence inputs, version checks and numerical parity.

## Alternatives considered
Formula selection is concluded by #32; no further model selection is in scope.

## Acceptance criteria
Full snapshot k50 reconciliation; edge/missingness validation; consumer parity;
unchanged band thresholds and ML outputs; coordinated production evidence.

## Rollout, observability, and rollback
Dependency-order protected PRs and CI. Monitor exact deployed commits, method
metadata and representative county scores. Revert coordinated API/Web versions
if parity fails; retain previous immutable package pin and data release.
