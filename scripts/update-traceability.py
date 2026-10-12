"""Apply actual partial implementation references without accepting any parent REQ."""
import csv, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'Docs'/'软件工程文档'
paths={1:'apps/desktop/main/repository.ts;apps/desktop/main/archive.ts',2:'apps/desktop/main/repository.ts',3:'apps/desktop/main/archive.ts',4:'apps/desktop/main/repository.ts',5:'crates/geometry-core/src/lib.rs',6:'packages/schema/index.ts;apps/desktop/main/main.ts',7:'apps/desktop/src/App.vue',8:'crates/geometry-core/src/lib.rs',9:'packages/schema/index.ts;apps/desktop/src/App.vue',10:'apps/desktop/main/export.ts',22:'apps/desktop/main/export.ts;apps/desktop/main/png.ts',23:'scripts/independent-export-check.py',31:'apps/desktop/main/archive.ts;apps/desktop/main/preload.ts',32:'apps/desktop/main/main.ts',33:'packages/modules/index.ts',35:'apps/desktop/main/worker.ts;apps/desktop/main/jobs.ts',42:'apps/desktop/src/i18n.ts',43:'apps/desktop/src/App.vue'}
paths.update({8:'crates/geometry-core/src/allowance.rs;apps/desktop/src/AllowancePanel.vue',9:'crates/geometry-core/src/lib.rs;apps/desktop/main/export.ts',11:'apps/desktop/main/species.ts',12:'apps/desktop/main/surface.ts',13:'apps/desktop/main/species.ts',14:'packages/surface/mapping.ts',15:'apps/desktop/main/seams.ts',16:'apps/desktop/main/seams.ts;crates/geometry-core/src/lib.rs',17:'apps/desktop/main/references.ts',18:'apps/desktop/main/reference-segmentation.ts',19:'crates/geometry-core/src/surface.rs',20:'apps/desktop/main/markings.ts',21:'apps/desktop/main/markings.ts',24:'packages/manufacturing/material.ts;apps/desktop/src/MaterialsPanel.vue',25:'apps/desktop/main/nesting.ts',36:'apps/desktop/main/jobs.ts;apps/desktop/main/surface.ts'})
paths.update({11:'apps/desktop/main/custom-template.ts;apps/desktop/main/species.ts',12:'apps/desktop/main/custom-template.ts;apps/desktop/main/surface.ts',18:'packages/reference/mask.ts;apps/desktop/src/MaskEditor.vue',21:'apps/desktop/main/markings.ts;apps/desktop/src/MarkingEditor.vue'})
paths.update({7:'packages/pattern/path-operations.ts;apps/desktop/main/topology-edit.ts',11:'apps/desktop/main/body-edit.ts;apps/desktop/src/MeshEditPanel.vue',12:'apps/desktop/main/body-edit.ts;apps/desktop/main/topology-edit.ts',16:'apps/desktop/main/seam-notches.ts;apps/desktop/src/SeamsPanel.vue',17:'packages/reference/alignment.ts;apps/desktop/src/ReferencesPanel.vue',34:'apps/desktop/main/worker.ts;apps/desktop/src/SurfacePanel.vue;tests/integration/performance.test.ts',37:'tests/integration/surface.test.ts',38:'tests/completion-e2e.mjs',40:'scripts/package.mjs',41:'scripts/notices.mjs',44:'apps/desktop/main/species.ts;apps/desktop/main/custom-template.ts',45:'apps/desktop/main/export.ts',46:'apps/desktop/main/svg-import.ts;apps/desktop/main/glb.ts'})
paths.update({6:'apps/desktop/main/surface-runtime.ts;apps/desktop/main/main.ts',14:'apps/desktop/src/SurfacePanel.vue;packages/surface/preview.ts;tests/picking-e2e.mjs',18:'packages/reference/color-cluster.ts;packages/pattern/bezier-fit.ts;apps/desktop/src/ReferencesPanel.vue',19:'crates/geometry-core/src/surface.rs;apps/desktop/main/automatic-cuts.ts;tests/large-mesh-benchmark.ts',20:'apps/desktop/main/markings.ts;packages/surface/spatial.ts',34:'apps/desktop/src/SurfaceCanvas.vue;packages/surface/preview.ts;tests/large-mesh-e2e.mjs',35:'apps/desktop/main/surface-runtime.ts;apps/desktop/main/worker.ts',37:'tests/large-mesh-benchmark.ts'})
paths[7]='apps/desktop/src/App.vue;apps/desktop/src/style.css;packages/pattern/path-operations.ts;apps/desktop/main/topology-edit.ts'
paths.update({3:'apps/desktop/main/archive.ts;apps/desktop/main/repository.ts',7:'packages/pattern/corners.ts;packages/pattern/shapes.ts;apps/desktop/src/AdvancedTools.vue',17:'packages/reference/image-input.ts;packages/reference/resources.ts;apps/desktop/main/references.ts',20:'apps/desktop/main/texture-markings.ts;apps/desktop/main/markings.ts;apps/desktop/src/SurfacePanel.vue',21:'apps/desktop/main/texture-markings.ts;apps/desktop/main/markings.ts',34:'apps/desktop/src/SurfaceGpu.vue;apps/desktop/src/SurfaceCanvas.vue;apps/desktop/main/repository.ts;tests/resources-e2e.mjs',40:'apps/desktop/src/SurfaceGpu.vue;tests/resources-e2e.mjs'})
paths[20]+=';apps/desktop/main/marking-completion.ts;packages/surface/spline.ts;tests/inference-e2e.mjs'
paths[34]+=';tests/full-performance-e2e.mjs'
paths[43]='apps/desktop/src/App.vue;apps/desktop/src/SurfacePanel.vue;tests/ui-workflow-e2e.mjs'
csvpath=root/'traceability.csv'
with csvpath.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for row in rows:
    number=int(row['需求ID'].split('-')[1])
    if number in paths:
        row.update({'实现位置':paths[number],'代码版本':'0.8.0; SHA256见evidence/0.8.0/source-manifest.json','证据':'34-实现进度与验证记录.md;35-离线增量0.2与剩余工作.md;36-离线0.3模板展开花纹与轮廓排料.md;37-离线0.4材料与变宽缝份.md;39-离线0.6交换格式与路径编辑.md;41-离线0.7大模型与颜色曲线.md;42-离线0.7.1工作区交互整理.md;43-离线0.8功能核对与图像纹理链.md','状态':'部分实现/子用例已执行/父需求未验收'})
with csvpath.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
for filename in ['01-prd.md','23-需求追踪矩阵.md']:
    file=root/filename;lines=file.read_text(encoding='utf-8').splitlines()
    for i,line in enumerate(lines):
        if any(line.startswith(f'|REQ-{n:03d}|') for n in paths):
            cells=line.split('|');cells[-2]='部分实现；[增量及边界](43-离线0.8功能核对与图像纹理链.md)；未整体验收';lines[i]='|'.join(cells)
    file.write_text('\n'.join(lines)+'\n',encoding='utf-8')
