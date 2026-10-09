# Neutral terminal paw placement review

Production and focused tests are frozen after the successful fresh public JPEG workflow.

The strengthened JPEG audit first exposed a real failure after the metadata repair: back source index 37 (name suffix `/ 38`, 255 original pixels) retained only 47.905 mm² of its 478.222 mm² scaled source area, or 10.017%. Its registration correctly targeted the left species paw, but the unrotated group lost most of this claw outside the visible paw.

The repair in `apps/desktop/main/anatomical-placement.ts` aligns the complete neutral hand group using its adjacent source arm frame and the actual visible target paw axis. Both axes point from the adjacent arm toward the hand, so a raised hand does not borrow its direction from the torso. A single uniform rotation and scale applies to every material in the group. Source pixels, contours and relative pigment arrangement are unchanged.

The branch requires one neutral source plus at least two distinct dark sources, all confident silhouette paw classifications, no colored pads, a species template, and supported source and target arm anchors. Manual/imported placements, missing anchors, a single or duplicated tip, low confidence, and existing colored paws retain their established behavior.

The final fresh public workflow used `.local/tests/isolated-paw-repaired-ZStRpt`. `tests/real-mapping-preview-e2e.mjs` passed with 102 original sources, 78 markings, and the original source-partition audit passing. The saved cutting fixture SHA-256 is `3a0fb795895d32e0dc547c0b58fdda9bae490bae3168e7254f68c4a8bb78e127`. It remains an automated calibration/review test fixture; no cutting flow was run by this agent.

| View | Source index | Original pixels | Projected area mm² | Scaled source area mm² | Retained fraction | Arm station |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Front | 7 neutral hand | 2340 | 1954.400 | 1984.259 | 98.495% | 1.0834 |
| Front | 47 claw | 251 | 209.043 | 212.841 | 98.215% | 1.1203 |
| Front | 48 claw | 111 | 95.760 | 94.125 | 101.737% | 1.0883 |
| Back | 2 neutral hand | 2722 | 1879.465 | 1893.420 | 99.263% | 1.0894 |
| Back | 37 claw | 255 | 177.378 | 177.378 | 100.000% | 1.1223 |
| Back | 38 claw | 142 | 97.089 | 98.775 | 98.293% | 1.0995 |

The small fraction above 100% comes from saved source contour recovery versus original pixel area, within the existing 3.1% material-area budget. All source identities and both separate claw attachments are asserted explicitly. Front source side left maps to species right; back source side right maps to species left. Actual fragments must use correct-side palm/finger/hand-claw faces. Neutral hands retain substantial actual palm area: front 1686.518 mm²; back 1309.603 mm². Stations remain normalized by the original arm shoulder/wrist frame, and yellow cuffs remain beyond their original blue arms.

Focused verification: the combined extraction/placement/coverage/limb run passed all 42 tests. Six additional boundary/import/duplicate-tip cases were then added; the final placement/coverage/limb run passed all 37 tests, including 16 terminal-paw-placement cases. The original 11 extraction cases had passed in the combined run. Final `npm run typecheck` passed. A diagnostic comparing the production placement function with the same code before the new paw branch found all 152 blue-and-white placements exactly JSON-identical, including rotation, uniform scales, centers, sides, regions and registration hash. Diagnostic script: `.local/tests/paw-fit-diagnostic.mjs`.

Frozen public evidence: `test-results/real-jpeg-mapping-3a0fb795895d/report.json`, source-partition audit, front/back/side screenshots and front/back detail screenshots. Main SHA-256: `31d0e00877998baf59d75820087aaf94909f0d642ad963a67314260ac7fa8764`. Surface worker SHA-256: `d7e4c60d3b9f284b717444eec64d29380717cbcd186b32074aeed983aad4399d`. Native worker SHA-256: `6dc74bd654b98c30212655296012fbb271fbcd303259314dfc1d5cc4f8c8a67b`.

Root owns the final full unit run, final package, 64 desktop suites, and real cutting flows. No further production changes are pending from this agent.
