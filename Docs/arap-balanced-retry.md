# Optional balanced ARAP retry

The ordinary `arap` solve is unchanged. The internal worker method
`arap-balanced` first runs the same ordinary solve, then retries once only if
at least one face exceeds an existing hard maximum. It does not repair an
invalid initial chart or supply new topology cuts.

For each ordinary face, let `r` be the maximum of area error / 0.15,
edge error / 0.10, and combined distortion / 0.15. The retry fixes the
weight `min(64, max(1, r)^6)` before solving. Rest area times this weight is
used consistently in the FEM normal equations, local/global objective,
right-hand side and line search. The weight is a bounded proposal heuristic,
not a guarantee that a curved panel can be flattened without seams.

The single translation pin and positive-orientation line search remain.
The retry replaces the ordinary geometry only if it converged, every face
passes all three hard maxima, and the complete chart has no triangle overlap.
A failed solve, rejected candidate or overlap-check error retains the ordinary
geometry and report. A passing ordinary solve skips the retry entirely.
Existing p95 soft review warnings remain. Retry energy values describe the
fixed weighted objective and must not be compared to unweighted energy as
proof of manufacturing quality.

The permanent fixture `tests/fixtures/arap-balanced-real-domain.json` contains
57 vertices and 62 original material faces from the real character workflow,
with input order preserved. At 30 iterations ordinary ARAP's maximum edge
error is 0.11914667; the retry obtains area 0.13511852, edge 0.09602899 and
combined distortion 0.08377547, with all 62 faces still in one patch. At 100
iterations the same ordinary failure persists and the retry also passes.
The soft p95 warning remains. Native tests also verify that a passing ordinary
plane and a rejected one-iteration retry keep identical serialized results.

An independent diagnostic of the last 40 failed domains in the current real
workflow found 16 still exceeding hard maxima under ordinary ARAP. This retry
rescued one domain at a 30-step budget and two at 100 steps. It is a modest
reduction in required seams, not a solution to every real workflow domain.
