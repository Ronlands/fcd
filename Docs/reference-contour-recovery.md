# Reference contour recovery audit

The extractor recovers raster geometry from the classified original-resolution pixels. It does not beautify outlines or impose smoothness. Straight spans remain lines. A cubic is accepted only when the original span cannot be explained by a digital straight segment and a geometric least-squares fit remains within the original boundary envelope.

## Primary algorithm references

- Peter Selinger, [Potrace: a polygon-based tracing algorithm](https://potrace.sourceforge.net/potrace.pdf), 2003, sections 2.2.1–2.2.4: digital straight paths and polygon reconstruction. The aesthetic curve smoothing stage is intentionally excluded.
- DGtal, [Digital straight segment recognition](https://www.dgtal.org/doc/stable/moduleArithDSSReco.html), and [StabbingLineComputer](https://dgtal-team.github.io/doc-nightly/classDGtal_1_1StabbingLineComputer.html): recover lines from digital boundary evidence instead of treating alternating raster edges as physical corners.

This implementation uses bounded numerical strip recognition and data fitting; it does not claim to be a complete implementation of either reference or a universally optimal tracer.

## Contract

The 0.8-pixel caller argument remains compatible with the old API. The native pixel grid is inferred from traced raster edges, including rotated/calibrated inputs. The recognition strip is at most 1.8 native pixels wide. This is distinct from the final, conservative bidirectional boundary-error bound of 1.05 native pixels, including curve flattening and unsampled-distance margins.

Every reconstructed ring must retain winding, its corresponding hole, containment and nonintersection, with at most 3% measured area error. Small holes below 16 native pixel squares stay exact. Native contact bevels and very acute tips remain protected. Other corners are reconstructed from supporting lines inside the pixel uncertainty, without averaging anchors or enforcing C1 continuity.

A narrow, nearly parallel straight strip can be ill-conditioned after an image-edge truncation. When independent intercepts violate the area bound, the recovery can apply a minimal one-dimensional thickness adjustment to reach the existing 3% measurement constraint. It retains edge directions and native clipping coordinates, caps the total width adjustment at half a native pixel, and still requires the full topology and 1.05-pixel boundary checks. It does not round edges or optimize appearance.

The fitter first keeps the compact outline and restores original holes if a hole fit fails. It can retain supporting corner anchors locally before considering the exact raster boundary. An irreducible outer contour above 2000 editable nodes reports RESOURCE_LIMIT rather than silently saving an invalid source.

## Regression evidence

The earlier single-region recovery check covered nine test files and 71 tests, all passing, plus TypeScript checking. Coverage includes the actual replacement character's blue diamond; straight slopes 0.13, 0.3, 0.6, 1, 1.5 and 2.7 at pixel scales 0.05, 1 and 10 after rotation and a large translation; small pointed markings; true notches; near-contact bevels; curved rings and holes; the original ear, body and yellow thigh; complete claws; and native validation of both real images. Current full-suite results are recorded separately in the final task audit.

The immutable old extractor yielded 11 cubics for the real blue diamond, with control-handle bow up to 1.13 pixels. The native-pixel algorithm sample used for the three-panel comparison has 12 line nodes and no cubics, with conservative boundary error 0.99435 pixels. The separate public-API import calibrated to 1800 mm uses 10 line nodes and no cubics, with boundary error 0.962717 pixels (the same 1813 classified blue pixels). These are different calibrated reconstruction runs, not interchangeable node-count evidence. It preserves a small notch in the classified blue pixel mask instead of silently erasing it.

The real blue body has 216 nodes and four data-fitted cubics, with boundary error 1.02494 pixels. The yellow ear has 14 nodes and one cubic, with error 0.98989 pixels. The yellow thigh has 79 line nodes instead of 470 raster nodes, with error 0.96110 pixels. Source-supported local corners remain; these results are not described as universally smooth or always below one pixel.

The saved-project manufacturing regression independently uses `tests/fixtures/legacy-curved-character-piece.json`, captured from the immutable old algorithm: 318 cubics and six holes. It retains coverage of more than 2000 derived samples at three scales after the new extractor stops adding gratuitous curves.

Visual evidence: `test-results/contour-recovery/blue-diamond.png`, `yellow-thigh.png`, `yellow-ear.png`, `black-claws.png`, `blue-body.png`, with separately clipped original / old / new panels, corresponding SVGs and `visual-metrics.json`.

## Shared material boundaries

Dual-view extraction now recovers the whole per-view material network together. It splits collinear traced edges at every material junction, builds maximal chains with fixed junction coordinates, fits each chain once, and reuses its nodes and reversed controls for both owners. A closed loop touching another material also retains that junction. Shared holes and their enclosing-material edges use the same polygon samples because saved holes cannot contain cubics. Invalid fits restore the complete shared chain for every owner; sources are never expanded to conceal a gap.

The previous independent fitting produced 56.68 pixel-square gaps and 17.08 pixel-square overlaps on a simple curved two-material interface. The joint-chain regression requires zero native boolean gap and overlap on open curves, closed ellipse/diamond interfaces and three-material junctions. Shared long straight strips at slopes 0.13, 1.5 and 2.7 require at most 20 central-material nodes, no cubics, unchanged area/topology limits and the same 1.05-pixel fidelity bound. Large translated and rotated junction tests account only for floating-point coordinate roundoff.

An independent raster/native-vector audit of the real blue-white 133-source image and original JPEG 102-source image found no unsupported internal seam gaps, overlaps or wrong-owner colors after joint recovery. It samples saved native flattened geometry rather than matching chain signatures. The disclosed <=0.01 mm diagonal contact bevel remains; true background holes are never filled. The single-region examples above describe the earlier native-pixel fitter evidence, rather than the new batch network's node counts.

The network design is consistent with the topology-aware primal/dual boundary graph discussed by [He, Kang and Morel (2024)](https://arxiv.org/abs/2409.15940). This implementation uses shared chains and bounded data fitting only; it does not adopt their smoothing or region merging.

## Limits

Anatomical metadata is separate from recovered geometry. A missing hand without visible pink pads can be identified from a compact neutral arm-terminal component and at least two independently supported distal dark tips on the same side. Existing paw evidence takes precedence; ambiguous, head, tail, single-tip and opposite-side clusters do not qualify. Only those exact components change classification, without expanding a box over the adjoining cuff or changing their pixels or curves. The regression retains pre-change geometry hashes for both real images and complete metadata/frame hashes for the unaffected blue-white image.

Geometry fidelity is relative to the classified source pixel mask. Antialiasing, painted shadows, gaps in source color classification and low resolution can retain small source-supported turns. The geometric constraints intentionally take precedence over an idealized shape. Extremely detailed or invalid inputs can remain above the editable-node budget and require explicit correction. Successful regression fixtures do not establish that every arbitrary illustration is semantically or geometrically recoverable.
