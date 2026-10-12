# Final independent review

Reviewed 2026-10-09 by the existing GPT-6.1-sol high integration reviewer. Scope: assembly, selected-cut overview, marking rendering, draft/document undo, public-flow evidence, and the previously audited shared-source → material → native numerical contracts. No heavy cut/native suite was rerun for this final review. Git was read-only; every Electron test ran hidden.

## Findings and fix

One concrete regression was found and fixed with root authorization: the overview uses `.overview-backdrop`, while App's document shortcut guard recognized only `.print-preview-backdrop`. Ctrl+Z could undo underlying pieces behind an unchanged read-only overview. The existing `large-preview-e2e.mjs` regression failed on isolated app BqoIPw: project revision changed from 1 to 2 while the overview remained open.

The only production edit in this review adds `.overview-backdrop` to that guard. On fresh isolated app zbvlBH, Ctrl+Z, Ctrl+Y and Ctrl+Shift+Z preserve revision and every underlying piece while the overview is open; after closing, actual undo removes the 267 pieces and redo restores their exact geometry. Native worker was copied, not rebuilt. The expanded test also verifies original contours, visible SVG/footer bounds at 1440×960 and 1000×680, bounded single-piece print tiling, and invisible windows. It passed. Evidence: `large-preview.json`, `.local/tests/overview-shortcuts-red.log`.

No further confirmed blocker was found in this reviewed scope.

## Contracts and regression coverage

- Assembly reconstructs actual binding trim triangles; missing/edited pieces remove their own physical area. Current display colors may change without invalidating geometric bindings. Historical previews check saved surface and piece geometry fingerprints, beyond matching IDs/topology. Active gating cancels superseded async hash results and releases the hidden page's canvas. Existing archive E2E covers a package with valid checksums but deliberately mismatched saved geometry, switching to intact current cuts, deactivation/reactivation, and reopening the intact archive.
- Existing closed-cube E2E checks substantive colored pixels, occlusion, an exactly missing panel, explosion/reset, orbit, clear preview, and marking holes. This is stronger evidence than a thin plane screenshot. Assembly is saved-position reconstruction, not cloth/sewing simulation.
- GPU batches preserve EvenOdd rings within a fragment and union repeated same-face fragments through separate stencil clears; ordinary distinct-face markings still require one batch. Pure buffer replay tests cover overlap, holes, later-color ordering, and source immutability.
- Overview keeps exact contours in a screen layout and requests millimetre print pages only for the selected piece. It does not bypass output-instance or page-budget guards.
- Undo coverage includes interleaved draft A / committed B / draft C order, redo invalidation after a new branch, focused numeric edits, grouped gestures, deferred child updates, inactive synchronization, session resets, and source/attached/cut-path/model/settings drafts. This establishes the tested scopes; it is not proof of every possible interaction sequence.

This review independently reran five focused files: assembly-preview, pattern-overview, surface-marking-union, draft-history and draft-history-routing. **22/22 tests passed.** The expanded hidden overview E2E and `npm run typecheck` also passed. Prior 64-suite desktop report is green on HyyxOh, an earlier snapshot; it must not be described as a final-package run.

## Keep the actual runs separate

| Evidence | Input / build | Result and limits |
|---|---|---|
| Frozen blue core | Exact project SHA `e21aa68cc859510a48dd5ed9e6de31f9da5e84ba957f51c8393feef15cd5f85e` | **483 pieces**, 102 needsReview; zero geometry/binding errors; 22,620 actual trim triangles and approximately 100% physical area coverage. |
| Public blue desktop flow | BqoIPw; original blue PNG SHA `274a203ba64db2fe3c949d585f949396d030ed27902826eee781174b43dcd11b`; independently generated through public API | **482 pieces**, 106 needsReview; nine checks passed: import/mapping, bounded candidate, acceptance, undo/redo archive identity, project/bundle save, SVG export, reopen, assembly coverage, all-piece overview. Report does not record an exact input-project hash; do not equate this run with the 483-piece frozen project. |
| Frozen JPEG core | Exact project SHA `9b6e3a40d41f44bf2a97a3867eb0cf75d7522a0bc34b8741df34831443df85b6` | **277 pieces**, 59 needsReview; zero geometry/binding errors; 15,912 actual trim triangles and approximately 100% physical area coverage. |

The frozen core results satisfy unchanged hard limits: area error ≤15%, edge error ≤10%, combined distortion ≤15%, piece count ≤500. They retain review flags. Independent source-partition audits of both exact projects have zero unsupported interior gap, overlap and wrong-color samples. Independent post-cut trim/color audit finds zero substantial blue mismatch (one boundary-budget sample, area 4.465×10⁻⁶ mm²) and zero JPEG mismatch. These are sampled color/source checks plus independent numerical area/coverage guards, not a pixel-perfect texture claim.

Files: `.local/tests/design-cut/validation-bluewhite.json`, `validation-jpeg.json`, `source-partition-blue-cut-final.json`, `source-partition-jpeg-cut-final.json`, `independent-final-trim-colors-blue.json`, `independent-final-trim-colors-jpeg.json`; public evidence is `real-blue-white-cut.json`.

As of this review, `real-artwork-cut.json` still records the older nyqNR2 public JPEG failure at DEGENERATE_MESH; the later successful frozen JPEG core run does not validate JPEG public acceptance/export. The neutral-paw extraction correction is concurrent and outside these frozen-input results. Final source snapshot, complete suite, packaged application and refreshed public evidence remain root's responsibility; this review does not certify those pending artifacts.

## Release-unit follow-up, 22:37

Root subsequently requested investigation of two failures in the release-unit run. The captured original result was 733/735 passing. Both failures were reproduced independently; the full-model probe below was explicitly authorized for this follow-up.

- `color-contact-triangulation.test.ts` expected every reliable tiny triangle to fail the removed native absolute 1e-6 mm² area gate. This was an obsolete expectation, not a geometry failure. It now tests native acceptance of positive tiny cells at 0/1000 mm translation with both windings, preserved total material area and immutable input. A separate explicit caller-policy callback still rejects every singleton/pair and requires complete neighbourhood repair. No production geometry rule changed. File: **5/5 passed**.
- `cut-line-workflow.test.ts` still timed out at 120 s with one worker. A diagnostic copy of its exact default-design, uncolored whole-canine fixture completed **all its original assertions**: 133 pieces, 8,534 actual trim triangles, original markings/holes preserved, acceptance and independent workflow restoration valid. Measured stages: assembly 0.36 s, projection 0.42 s, cutPreview 220.42 s, acceptance/exchange 3.99 s; total 225.22 s. Request tracing recorded 1,210 native requests, including 1,175 chart requests; maximum single request 4.94 s. This is a long complete design pipeline, not one stuck native solve. Evidence: `.local/tests/cut-line-stage-probe.json` and its diagnostic `.mjs`/log.
- This exposed a **public runtime deadline defect** too: `runCutPreview` allowed ten minutes only with color inserts, even though its default design strategy without color also legitimately needs longer than two minutes. With root authorization, default/explicit design now use the same bounded 600 s complete-job deadline. Explicit uncolored mesh and projection jobs retain 120 s; colored jobs retain 600 s. Native per-request limits, immediate cancellation/child termination, atomic commits, 500-piece ceiling and distortion rules are unchanged. Fake-clock default/explicit design and cancellation tests failed before the edit and pass afterward. The whole-canine test and equivalent real-dual-view UI wait now match the measured production budget; its small planar testcase retains 120 s.

Final focused run: color-contact plus runtime-budget, **14/14 tests passed**; typecheck passed. No second heavy whole-model run was made after the successful diagnostic, as requested by root; the amended full-model Vitest testcase and real-dual-view desktop testcase await root's final suite. No broader caching/performance edit was made: alternate methods and opened dart topology make repeated face counts insufficient evidence of identical chart inputs.
