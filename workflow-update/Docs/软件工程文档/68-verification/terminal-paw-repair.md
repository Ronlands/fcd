# Missing neutral paw metadata repair

The original JPEG has two hands without visible pink pads: the front hanging hand and back raised hand. The existing pink-pad detector identified the opposite hands but left these neutral palms and their separate dark claws classified as arm. Consequently, their colours were placed on the forearm and the actual model palm remained gray.

## Scoped change

`packages/reference/terminal-paw-support.ts` supplies conservative metadata evidence only for a missing paw side in an already supported full character. It requires a compact neutral instance already classified as that arm, located at its outward distal PCA end, plus at least two spatially separate compact dark tips. Each tip must independently be arm/paw on the same side. Head, tail, unknown and opposite-side dark instances are not borrowed. Competing neutral candidates remain editable without inference. Existing confirmed paws take precedence.

`packages/reference/illustration.ts` applies the result after pigment instances have been finalized. Only the qualifying whole neutral and claw instances gain paw metadata at confidence .78. Those exact pixels supply the new paw registration frame and leave the arm frame. No padded positional box is added, so the neighbouring yellow cuff retains arm metadata. No label, palette, pixel ownership, source contour or shared boundary is changed.

## Actual source evidence

| View | Neutral hand (zero-based source index) | Separate claws | Source/anatomy side | Species model side |
|---|---|---|---|---|
| Front | 7: 2340 pixels, witness (390,435) | 47:251 pixels (410,451); 48:111 pixels (378,455) | left after front-view conversion | right |
| Back | 2: 2722 pixels, witness (560,265) | 37:255 pixels (586,244); 38:142 pixels (600,269) | right | left |

Witnesses are local coordinates in the front 666×750 crop starting at x=609 and back 609×750 crop starting at x=0. UUIDs change on fresh extraction; indices, witnesses and pixel counts identify the actual original materials. Yellow cuff sources front24 and back26 retain their arm classification. Source counts remain JPEG102 and blue-white133.

## Verification

`tests/integration/terminal-paw-support.test.ts` first reproduced both actual hands as arm instead of paw, then passed all 11 tests after repair. It verifies the neutral hand, both claws, cuff, actual paw frame and complete material ownership. Negatives cover a single dark tip, no neutral palm, existing paw precedence, nearby head/tail/unknown/opposite-side components, and displaced clusters near the head or tail.

The immutable pre-change hashes in `tests/fixtures/terminal-paw-baseline.json` establish that both real images retain byte-identical colour/pixel ownership and full saved contour coordinates/control geometry (with random node IDs excluded). Blue-white source anatomy/context metadata and all partBounds also remain byte-identical, preserving the inputs to its existing 152 placement transforms.

The targeted 11-test suite and TypeScript checking pass. The final 40-file reference-related run passed 253 tests and encountered one 15000 ms timeout in the unrelated visible-colour-cut workflow during concurrent full-unit gates. That unchanged workflow case subsequently passed in 10.10 seconds with one worker and the original timeout. No timeout or production implementation was relaxed. Root's full-unit gate remains the final package acceptance.

The public-workflow acceptance is separately owned by root/final_mapping_checks: substantial original hand area must project onto actual palm faces, and both claws must project inside the correct paw regions. Semantic classification alone is not presented as proof of complete visible hand coverage. Other unsupported sources retain manual review; this detector does not claim arbitrary pose reconstruction.
