# Surveillance Gap Score v1.1 (approved Smooth k=50)

Owner decision: [Shared Python #32](https://github.com/Caraway-Labs/one-health-lyme-gap-atlas-shared-python/issues/32), October 19, 2026.

For valid published 2023 minimum incidence I per 100,000, H=100/(1+I/50).
E=0.6*tick+0.4*pathogen; C=0.5*SVI+0.3*uninsured+0.2*rurality.
Score=round(H*(0.65*E+0.35*C)/100,1). Intermediates are not rounded.
Only the returned display components are rounded to one decimal.

The scoring methodology `surveillance-gap-score-v1.1` is independent of the
semantic data-release methodology and release ID. Package 2.0.0 marks the
incompatible scoring-settings change; it is not the scoring method number.
The governed default is fixed k=50; explicit alternative k settings are
exploratory scenarios, not a replacement published methodology.

Missing county human observations retain legacy H=75 as an unsupported assumption,
not an incidence estimate. A published null floor uses that same legacy fallback;
true published numeric zero uses H=100. Unknown ecological status contributes no
positive signal. Existing missing community-input defaults and geography scope
remain unchanged. Invalid negative/nonfinite incidence is rejected. A computed
zero remains possible with zero/tiny context. Out-of-scope results must remain
visually distinct. The six color bands and review labels retain their thresholds.

This is a context-weighted potential human/ecological surveillance-discordance
index, not disease risk, verified underreporting, predicted incidence, or ML
review priority. A minimum floor may overstate H relative to the unknown true
reported incidence. Ranking/band changes are methodological, not new evidence.

## Compatibility and rollback

`ScoreSettings` rejects old `low_incidence_breakpoint` arguments. Do not map
breakpoint=10 to k=10. Historical replay uses the explicitly named
`models.LegacyScoreSettings` and the previous equation. Existing pinned package
commits remain immutable. No data or ML model changes are required.

Coordinate Shared Python -> API -> Web pins and generated contracts before
production activation. Old Web clients issuing breakpoint parameters must receive
an explicit incompatibility error; new Web clients require v1.1 method metadata.
Never render v1.0 published scores beside unlabeled v1.1 scenarios. In-flight
clients may require reload. Before rollback disable scenario use by version
validation, revert Web/API together through protected PR/CI promotion, then
verify prior exact commits and representative live values. Do not change data.

## Research reconciliation

`tests/fixtures/gap-score-v11-k50.csv` is the selected k50 slice of the #31
immutable governed snapshot, including all 3,144 records (3,109 in scope).
The manifest records source/fixture hashes and release identity. Tests reconcile
every score and displayed component, plus in-scope national ordering, against
that research slice. It is regression evidence, not a fresh production read.
