import type { IllustrationRegion } from './illustration';
/** Conservative ownership refinement guided by original image edges. Material labels remain a
 * complete partition; only confidently located internal color transitions can
 * move. No coordinate averaging, region closing or contour smoothing occurs. */
export function refineImageEdgeOwnership(width: number, height: number, rgba: Uint8Array, regions: IllustrationRegion[]) {
    const size = width * height;
    if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || size > 4096 * 4096 || rgba.length !== size * 4)
        throw Error('IMAGE_LIMIT');
    const labels = new Int32Array(size).fill(-1);
    for (const [id, region] of regions.entries()) {
        for (const index of region.indices) {
            if (!Number.isInteger(index) || index < 0 || index >= size || labels[index] >= 0)
                throw Error('INVALID_MASK');
            labels[index] = id;
        }
    }
    // Proposals are collected before labels are changed, so the original
    // ownership can share this buffer instead of copying the entire raster.
    const initial = labels;
    const palette = regions.map(region => {
        const rgb = [1, 3, 5].map(i => parseInt(region.color.slice(i, i + 2), 16));
        const sum = rgb.reduce((a, b) => a + b, 0) || 1;
        return { rgb: rgb.map(v => v / sum), dark: Math.max(...rgb) < 80 };
    });
    const targets = new Int32Array(size).fill(-1), scores = new Float32Array(size);
    let supportedEdges = 0;
    function probe(i: number, j: number, stride: number, coordinate: number, limit: number) {
        const a = initial[i], b = initial[j];
        if (a < 0 || b < 0 || a === b || palette[a].dark || palette[b].dark || coordinate < 7 || coordinate + 7 >= limit)
            return;
        const delta = palette[a].rgb.map((v, c) => v - palette[b].rgb[c]), norm = Math.hypot(...delta);
        if (norm < .12)
            return;
        const dir = delta.map(v => v / norm);
        // Confirm broad support on both sides. A third owner, exterior, an ink
        // separator, or a narrow tip excludes the search corridor entirely.
        for (let t = -6; t <= 7; t++) {
            const owner = initial[i + t * stride];
            if (owner !== a && owner !== b)
                return;
        }
        if (initial[i - 6 * stride] !== a || initial[i + 7 * stride] !== b)
            return;
        // Normalize only the narrow color profiles actually examined. A full
        // three-channel Float32 raster costs 192 MiB at the image size limit.
        const value = (t: number) => {
            const offset = (i + t * stride) * 4;
            const sum = rgba[offset] + rgba[offset + 1] + rgba[offset + 2] + 1;
            return (dir[0] * rgba[offset] + dir[1] * rgba[offset + 1] + dir[2] * rgba[offset + 2]) / sum;
        };
        const gradient = (t: number) => (value(t - 2) + 2 * value(t - 1) - 2 * value(t + 1) - value(t + 2)) / 8;
        const contrast = value(-5) - value(6);
        if (contrast < .08)
            return;
        let peak = 0, position = 0;
        for (let t = -4; t <= 5; t++) {
            const g = gradient(t);
            if (g > peak) {
                peak = g;
                position = t;
            }
        }
        if (peak < .025 || peak < contrast * .10 || position === -4 || position === 5)
            return;
        const l = gradient(position - 1), r = gradient(position + 1), denominator = 2 * (l - 2 * peak + r), offset = denominator ? (l - r) / denominator : 0;
        if (!Number.isFinite(offset) || Math.abs(offset) > .6)
            return;
        // A blurred color step can have two nearly equal derivative ridges.
        // Selecting the larger ridge jumps between their sides as JPEG blocks
        // vary. Locate the half-contrast crossing of the original color profile
        // instead; accept only one crossing supported by the two owner sides.
        const level = (value(-5) + value(6)) / 2;
        const crossings: number[] = [];
        for (let t = -4; t < 5; t++) {
            const left = value(t), right = value(t + 1);
            if (left >= level && right < level)
                crossings.push(t + .5 + (left - level) / (left - right));
        }
        if (crossings.length !== 1)
            return;
        const edge = crossings[0], original = 1;
        if (Math.abs(edge - original) > 4.5)
            return;
        supportedEdges++;
        for (let t = -4; t <= 5; t++) {
            const p = i + t * stride, target = t + .5 < edge ? a : b;
            if (initial[p] === target)
                continue;
            if (peak > scores[p]) {
                scores[p] = peak;
                targets[p] = target;
            }
        }
    }
    for (let y = 0; y < height; y++)
        for (let x = 0; x < width; x++) {
            const i = y * width + x;
            if (x + 1 < width && initial[i] !== initial[i + 1])
                probe(i, i + 1, 1, x, width);
            if (y + 1 < height && initial[i] !== initial[i + width])
                probe(i, i + width, width, y, height);
        }
    const offsets = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]];
    function localComponents(i: number, owner: number, equal: boolean, eight: boolean) {
        const active = offsets.map(([dx, dy]) => (labels[i + dy * width + dx] === owner) === equal), seen = new Set<number>();
        let count = 0;
        for (let a = 0; a < 8; a++) {
            if (!active[a] || seen.has(a))
                continue;
            count++;
            const queue = [a];
            seen.add(a);
            for (let q = 0; q < queue.length; q++) {
                const p = queue[q];
                for (let b = 0; b < 8; b++) {
                    const dx = Math.abs(offsets[p][0] - offsets[b][0]), dy = Math.abs(offsets[p][1] - offsets[b][1]);
                    if (active[b] && !seen.has(b) && (eight ? Math.max(dx, dy) === 1 : dx + dy === 1)) {
                        seen.add(b);
                        queue.push(b);
                    }
                }
            }
        }
        return count;
    }
    const proposals: number[] = [];
    for (let i = 0; i < size; i++)
        if (targets[i] >= 0)
            proposals.push(i);
    proposals.sort((a, b) => scores[b] - scores[a]);
    let movedPixels = 0;
    for (let pass = 0; pass < 5; pass++) {
        let changed = 0;
        for (const i of proposals) {
            const a = labels[i], b = targets[i];
            if (a === b)
                continue;
            const x = i % width, y = Math.floor(i / width);
            if (x < 1 || x >= width - 1 || y < 1 || y >= height - 1)
                continue;
            // Four-connected regions and eight-connected complements must both retain
            // one local component. These simple-point tests preserve holes, components
            // and junctions throughout sequential ownership changes.
            const meetsAnotherOwner = offsets.some(([dx, dy]) => {
                const owner = labels[i + dy * width + dx];
                return owner !== a && owner !== b;
            });
            if (meetsAnotherOwner)
                continue;
            if (![i - 1, i + 1, i - width, i + width].some(n => labels[n] === b))
                continue;
            if (localComponents(i, a, true, false) !== 1 || localComponents(i, a, false, true) !== 1 || localComponents(i, b, true, false) !== 1 || localComponents(i, b, false, true) !== 1)
                continue;
            labels[i] = b;
            changed++;
            movedPixels++;
        }
        if (!changed)
            break;
    }
    const indices = regions.map(() => [] as number[]);
    for (let i = 0; i < size; i++)
        if (labels[i] >= 0)
            indices[labels[i]].push(i);
    return {
        regions: regions.map((region, id) => ({ ...region, indices: indices[id] })),
        labels,
        report: { supportedEdges, movedPixels }
    };
}
