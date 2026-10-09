# FurryPattern CAD
# Furry 兽装数字打版商业化桌面软件——完整实现设计与软件工程规格文档

> 文档版本：1.0.0
> 
> 文档状态：Implementation Baseline / 软件工程实施基线
> 
> 目标：以本文件作为后续 PRD、架构设计、数据库设计、算法设计、API 设计、前端实现、Rust 几何核心实现、测试和商业化部署的统一依据。
> 
> 产品形态：Windows / macOS / Linux 桌面端，Electron 主体；核心几何与拆板算法独立为 Rust Geometry Core；AI 推理通过 ONNX Runtime 本地执行；所有高价值能力模块化并由授权系统控制。

---

## 0. 文档使用规则

本文件不是单纯的产品说明书，而是后续工程实现的“单一事实源（Single Source of Truth）”。

开发中遵循以下规则：

1. 新需求必须先归入本文件定义的模块；没有归属模块的需求不得直接写业务代码。
2. 任何涉及毫米、纸样、缝线、曲面、UV、拆板、布料、身体参数的核心数据，禁止以 UI 像素作为真实数据单位。
3. UI 只是 Geometry Core 的一个客户端。纸样算法、拆板算法、花纹映射算法不得依赖 Vue 组件状态。
4. AI 输出永远属于“候选结果”，不能成为不可逆的最终几何结果；任何 AI 识别结果均必须可人工修正。
5. 商业授权属于独立模块，业务模块必须通过 Feature Entitlement 检查能力，而不是散落 `if vip`。
6. 对第三方开源库必须记录许可证、版本、用途、链接和发布义务；涉及 GPL/强 Copyleft 的组件不得未经审查直接进入闭源商业核心。
7. 所有算法都必须支持确定性测试（同输入、同参数、同版本得到可比较的结果）。
8. 所有导出的制造尺寸必须以毫米为最终语义单位。

---

# 1. 产品定义

## 1.1 产品名称

暂定名：**FurryPattern CAD**

产品简称：**FPCAD**

定位：

> 面向 Furry 兽装制作者、兽装工作室、数字打版师、爱好者和商业定制团队的参数化兽体 + 2D Pattern CAD + 3D 试装 + 花纹识别 + UV/曲面拆板 + 排料 + 制造输出平台。

---

## 1.2 核心工作流

```text
兽设双视图 / 多视图图片
        ↓
参考图管理
        ↓
角色与物种定义
        ↓
尺寸标定 / 身体参数
        ↓
参数化 Furry 3D Body
        ↓
花纹识别与颜色区域分割
        ↓
花纹语义分类
        ↓
2D/3D 映射
        ↓
自动拆板 / UV 展开 / 缝线规划
        ↓
2D Pattern CAD
        ↓
花纹切割路径生成
        ↓
人工调整节点 / 曲线 / 路径
        ↓
3D 穿着与花纹复核
        ↓
泡棉 / 毛皮 / 填充补偿
        ↓
排料
        ↓
PDF / SVG / DXF / PNG / 项目文件
        ↓
制作
```

---

## 1.3 核心差异化能力

第一原则：软件不是“把图片抠出来”，而是把**二维兽设视觉信息转化为可编辑、可度量、可制造的几何数据**。

核心壁垒：

### A. Furry 参数化身体引擎

支持犬科、猫科、兔科、熊科、鹿科、龙类及 Custom Species，并支持：

- 身高
- 胸围
- 腰围
- 臀围
- 肩宽
- 头宽/头长
- 吻部长度
- 耳朵尺寸/角度
- 尾巴长度/粗细/根部
- 四肢长度
- 植腿 / 趾行（Plantigrade / Digitigrade）
- 胸部、臀部、大腿等泡棉/填充体积
- 毛厚
- 泡棉厚度
- 内衬厚度

### B. 双视图花纹识别

从 Front / Back 等参考图识别：

- 主体颜色区域
- 装饰花纹
- 内耳/肉垫/爪尖等特殊区域
- 花纹边界
- 连通区域
- 对称关系
- 身体区域归属
- 花纹方向候选

### C. 2D Pattern CAD

纸样是“几何实体”，不是图片。

### D. 3D ↔ 2D 双向关联

用户在 2D 修改纸样后，3D 应同步；3D 上选中缝线/花纹/区域，可以回到对应的 2D Pattern。

### E. 面向制造的自主拆板算法

不是游戏 UV 展开，而是：

> 以可缝制、低变形、少拼片、合理毛向、合理缝线位置为目标的制造型曲面展开。

---

# 2. 对标研究结论

## 2.1 CLO 3D：学习交互模型，不复制实现

CLO 当前的工作流已经形成成熟的“3D Garment Window + 2D Pattern Window + 属性面板 + 工具栏 + 历史”等双窗协作模式，并提供 2D Pattern、3D Sewing 等完整工具体系。其官方文档还支持在 3D 服装上绘制线条，并将该线同步作为 2D Pattern 的基线。citeturn276222search48turn276222search11

因此 FPCAD 在交互层采用相似的高层思路：

```text
2D Pattern Workspace  ↔  3D Body Workspace
          ↕                       ↕
       Pattern                  Body
          ↕                       ↕
     Seam / Marking / Material / Property
```

但不得：

- 复制 CLO 源代码；
- 提取或逆向其私有实现；
- 将 CLO 专有格式当作自己的原生格式；
- 使用其 SDK 作为 FPCAD 核心算法依赖。

CLO 自身是商业软件，其官方开发者页面提供 API/SDK 用于插件扩展；这不等于 CLO 本身是开源软件。当前官方 SDK 文档展示 Windows/macOS 插件方向，并按版本提供 SDK。citeturn276222search3turn276222search8

**结论：参考 CLO 的产品交互与工作流，不依赖 CLO 来实现核心能力。**

---

## 2.2 Seamly2D / Valentina：学习参数化打版思想，不直接复制核心

Seamly2D 是开源服装打版软件，支持个人尺寸及多尺寸文件，定位就是数字化服装 Patternmaking；当前仓库采用 GPL-3.0。citeturn787272search3

Valentina 同样是参数化服装打版方向的代表性开源项目，采用 GPL-3.0。citeturn276222search0

其最值得借鉴的不是界面，而是：

```text
Measurements
    ↓
Parametric Formula
    ↓
Pattern Geometry
```

FPCAD 应将其进一步扩展为：

```text
Furry Measurements
        ↓
Morph / Anatomy Parameters
        ↓
3D Body
        ↓
Seam Graph
        ↓
Pattern Geometry
```

**商业化原则：Seamly2D / Valentina 只作为产品设计研究参考；不把 GPL 代码直接并入 FPCAD 的闭源核心。**

---

## 2.3 Blender：参考网格处理能力，但避免把 Blender 本体作为核心依赖

Blender 是 GPL 项目。它适合研究网格建模、Modifier、UV 等流程，但若产品目标是闭源商业客户端，不应未经法律与架构审查，把 Blender 的 GPL 代码直接嵌入核心产品。Blender 源码仓库包含 GPL 授权文件。citeturn573828search1

建议：

- 可作为开发人员研究工具；
- 可作为离线验证工具；
- 可导入/导出 glTF/OBJ/FBX 等通用格式；
- 不把 Blender Runtime 当作 FPCAD 的基础运行时。

---

# 3. 商业化开源许可策略

## 3.1 推荐依赖

### Electron

Electron 当前仓库声明 MIT，可用于商业桌面产品，但仍需按其发布要求保留许可证/版权信息。citeturn573828search4turn573828search3

### Three.js

Three.js 当前仓库为 MIT License；适合作为 3D WebGL/WebGPU 渲染层。citeturn573828search2turn573828search0

### ONNX Runtime

ONNX Runtime 当前仓库为 MIT License，适合作为本地 AI 推理运行时。citeturn447249search0turn447249search1

### Clipper2

Clipper2 当前仓库采用 Boost Software License 1.0，可作为 2D Polygon Boolean / Offset 等基础组件候选。citeturn447249search10

### Earcut

Mapbox Earcut 采用 ISC License，适合作为 2D 多边形三角剖分基础组件，但它本身不负责解决制造型曲面展开。citeturn787272search0turn787272search2

### meshoptimizer

meshoptimizer 为 MIT，适合网格压缩、索引优化、LOD 等辅助任务。citeturn787272search1turn787272search9

### libigl

libigl 以 MPL-2.0 为主，同时仓库包含 GPL 相关文件；因此必须在“实际使用的组件/文件级别”执行许可证审查，而不是只看项目主页。它适合参考几何处理、网格算法和研究原型。citeturn787272search12

### CGAL

CGAL 同时提供开源许可证路线和商业许可证路线；其官方说明指出 GPL/LGPL 部分有对应义务，且在 GPL 约束不适用时可购买商业许可。FPCAD 如果使用 CGAL 必须针对具体 Package 进行许可证矩阵评估；不默认把 CGAL 作为闭源核心依赖。citeturn787272search11

---

## 3.2 依赖白名单策略

正式商业发行版只允许三类第三方依赖：

1. MIT / BSD / ISC / Apache / Boost 等宽松许可证，满足 notice 要求即可；
2. 经法务批准并有明确隔离策略的 LGPL/MPL 组件；
3. 专门采购商业授权的第三方库。

对于 GPL/AGPL 依赖：

- 不进入闭源 Geometry Core；
- 允许作为开发环境辅助程序；
- 允许独立进程方式使用，但必须进行法律/架构审查；
- 不允许直接复制粘贴核心算法代码。

**注意：许可证满足 ≠ 专利自由。**

自主拆板算法在商业化前还需要独立进行专利检索、FTO（Freedom to Operate）评估和第三方组件的专利条款检查。

---

# 4. 总体技术栈

## 4.1 技术选型

| 层 | 技术 | 选择理由 |
|---|---|---|
| 桌面框架 | Electron | 跨平台、Node 生态成熟 |
| 前端 | Vue 3 + TypeScript | 适合复杂桌面 UI |
| 构建 | Vite | 快速开发 |
| 状态 | Pinia | Vue 官方生态、可测试 |
| UI | TailwindCSS + Headless UI 风格组件 | 快速构造 CAD UI |
| 3D | Three.js | WebGL/WebGPU，MIT |
| 2D CAD | 自研 Geometry Engine + SVG/Canvas/WebGL Renderer | 需要精确毫米几何 |
| 核心算法 | Rust | 内存安全、性能、WASM/Native 双形态 |
| AI Runtime | ONNX Runtime | MIT、本地推理 |
| 图像处理 | Rust + image/opencv 兼容桥接，可选 OpenCV | 识别预处理 |
| 2D Polygon | 自研 + Clipper2 | Boolean / Offset |
| Triangulation | Earcut / 自研高质量 Triangulator | 2D→Mesh |
| Mesh | 自研 Half-Edge / BMesh-like 数据结构 | 控制拆板算法 |
| 数据库 | SQLite | 本地单机 CAD 项目天然适合 |
| DB Driver | rusqlite 或 sqlx（Rust Core）+ IPC | 避免复杂 ORM 依赖 |
| 网络 | HTTPS REST / WebSocket | 账号、授权、云同步 |
| License | Ed25519 签名 License Token | 离线验证 + 在线吊销 |
| 安装 | electron-builder | Windows/macOS/Linux |
| 自动更新 | 自建 Update Service | 商业版本控制 |
| 日志 | tracing + 前端 logger | 可诊断 |
| 测试 | Vitest + Playwright + Rust tests + golden files | CAD 可重复性测试 |

---

# 5. 为什么采用 Electron + Rust，而不是纯 TypeScript

FPCAD 中 CPU 密集型任务包括：

- Bézier 几何运算；
- Polygon Boolean；
- Offset；
- 曲线相交；
- 网格遍历；
- 曲面分割；
- UV 展开；
- Distortion Optimization；
- Seam Graph 优化；
- Nesting；
- 大量 pattern 的批量导出。

这些能力最终应该成为可复用的 Native/WASM Core：

```text
                ┌───────────────┐
                │ Rust Geometry │
                │     Core      │
                └───────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
      Electron       WASM CLI       Server
          ↓
       Vue UI
```

核心算法不得与 Vue 生命周期绑定。

---

# 6. 系统总体架构

```text
┌──────────────────────────────────────────────────────────┐
│                        FPCAD Desktop                      │
├──────────────────────────────────────────────────────────┤
│ Electron Main                                             │
│ ├─ Window Manager                                         │
│ ├─ File System                                             │
│ ├─ SQLite                                                  │
│ ├─ License / Update                                        │
│ ├─ Worker Manager                                          │
│ └─ Native Bridge                                           │
├──────────────────────────────────────────────────────────┤
│ Preload / Secure IPC                                       │
├──────────────────────────────────────────────────────────┤
│ Vue Renderer                                               │
│ ├─ Project Manager                                         │
│ ├─ Character Studio                                        │
│ ├─ Pattern CAD                                             │
│ ├─ 3D Studio                                               │
│ ├─ Marking Editor                                          │
│ ├─ UV / Unwrap                                              │
│ ├─ Nesting                                                  │
│ └─ Export                                                   │
├──────────────────────────────────────────────────────────┤
│ Rust Geometry Core                                         │
│ ├─ geometry                                                │
│ ├─ path                                                     │
│ ├─ polygon                                                  │
│ ├─ mesh                                                     │
│ ├─ unwrap                                                   │
│ ├─ pattern                                                  │
│ ├─ nesting                                                  │
│ └─ simulation                                               │
├──────────────────────────────────────────────────────────┤
│ AI Runtime                                                 │
│ └─ ONNX Runtime                                             │
├──────────────────────────────────────────────────────────┤
│ Cloud Services (Optional / Commercial)                    │
│ ├─ Account                                                  │
│ ├─ License                                                  │
│ ├─ Subscription                                             │
│ ├─ Model Registry                                           │
│ ├─ Update                                                   │
│ └─ Telemetry (opt-in)                                      │
└──────────────────────────────────────────────────────────┘
```

---

# 7. 模块化体系

所有功能按模块注册。

## 7.1 Feature Module Interface

每个功能模块最少包含：

```ts
interface FeatureModule {
  id: string;
  version: string;
  capabilities: string[];
  initialize(ctx: ModuleContext): Promise<void>;
  dispose(): Promise<void>;
}
```

能力示例：

```text
character.basic
character.advanced
body.parametric
body.digitigrade
marking.basic
marking.ai
pattern.basic
pattern.advanced
pattern.seam
pattern.seam-allowance
uv.basic
uv.auto
uv.optimized
nesting.basic
nesting.advanced
export.pdf
export.svg
export.dxf
simulation.preview
simulation.physical
cloud.sync
team.workspace
```

---

# 8. 功能模块详细定义

## 8.1 Project Module

负责：

- 新建/打开/保存项目；
- 自动保存；
- 版本历史；
- 资源引用；
- Undo/Redo；
- Recovery。

项目原则：

```text
Project
 ├─ Character
 ├─ Body
 ├─ References
 ├─ Markings
 ├─ Patterns
 ├─ Seams
 ├─ UV
 ├─ Materials
 ├─ Nesting
 ├─ Simulation
 └─ Exports
```

---

# 9. 项目文件格式

推荐原生格式：`.fpcad`

文件本质采用 ZIP Container：

```text
project.fpcad
├─ manifest.json
├─ project.json
├─ character.json
├─ body.json
├─ markings.json
├─ patterns.json
├─ seams.json
├─ uv.json
├─ materials.json
├─ nesting.json
├─ simulation.json
├─ thumbnails/
├─ references/
├─ assets/
└─ history/
```

## 9.1 manifest

```json
{
  "format": "fpcad",
  "formatVersion": 1,
  "applicationVersion": "0.1.0",
  "unit": "mm",
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601",
  "projectId": "uuid",
  "contentHash": "sha256"
}
```

---

# 10. 单位系统

**唯一内部真实单位：毫米（mm）。**

浮点几何不要长期依赖 JavaScript `number` 的裸值语义。

建议：

- Rust Core 使用 `f64` 毫米；
- 关键序列化尺寸可以按 0.001mm 或更高精度保存；
- UI 展示默认 0.1mm；
- 纸样、缝份、花纹参数全部显示 mm；
- 导出 PDF/DXF/SVG 时进行明确的单位映射；
- 禁止通过 CSS px 作为几何真值。

---

# 11. Character / 兽设系统

## 11.1 Character

```ts
interface Character {
  id: UUID;
  name: string;
  species: SpeciesDefinition;
  measurements: BodyMeasurements;
  morphology: MorphologyParameters;
  markings: MarkingId[];
  referenceImages: ReferenceImage[];
}
```

## 11.2 SpeciesDefinition

```ts
interface SpeciesDefinition {
  id: string;
  family: string;
  displayName: string;
  baseBodyAsset: string;
  supportedLegTypes: LegType[];
  morphTargets: MorphTargetDefinition[];
}
```

---

# 12. Furry 参数化身体系统

## 12.1 Body Parameter Categories

### 基础尺寸

```text
height
neckGirth
chestGirth
waistGirth
hipGirth
shoulderWidth
armLength
legLength
footLength
headWidth
headLength
```

### 动物形态

```text
snoutLength
snoutWidth
earHeight
earWidth
earAngle
tailLength
tailBaseGirth
tailTipGirth
```

### 肢体

```text
upperArmGirth
forearmGirth
thighGirth
shinGirth
pawLength
pawWidth
clawLength
```

### Furry Padding

```text
chestPadding
hipPadding
thighPadding
bellyPadding
shoulderPadding
```

### Material Layer

```text
foamThickness
furThickness
liningThickness
bufferAllowance
```

---

# 13. Morph 系统

推荐使用：

```text
Base Mesh
+
Morph Target
+
Parameter Blend
+
Constraint
```

不允许直接对任意顶点随意缩放，否则身体变形后拓扑和缝线会崩。

## 13.1 Morph 示例

```json
{
  "chestWidth": 1.12,
  "hipWidth": 0.96,
  "snoutLength": 1.24,
  "earScale": 1.11,
  "tailLength": 1.32,
  "digitigrade": 1.0
}
```

## 13.2 Parameter Constraints

例如：

```text
chestGirth > waistGirth * 0.8
footLength > 0
snoutLength >= 0
furThickness >= 0
```

约束分为：

- Hard Constraint：违反后拒绝；
- Soft Constraint：允许但显示警告；
- Design Rule：提醒制作风险。

---

# 14. 双视图参考图模块

支持：

```text
Front
Back
Left
Right
Top
Bottom
Custom
```

第一阶段最低支持：

```text
Front + Back
```

## 14.1 Reference Calibration

用户需要先校准比例：

```text
已知角色身高 = 1800mm
图片人物像素高度 = 1200px
scale = 1.5mm/px
```

以后所有从该参考图提取的像素坐标必须进入毫米映射。

---

# 15. 花纹识别系统

## 15.1 总体流程

```text
Input Image
   ↓
Background Removal
   ↓
Color Normalization
   ↓
Semantic Segmentation
   ↓
Connected Components
   ↓
Boundary Extraction
   ↓
Curve Fitting
   ↓
Noise Removal
   ↓
Region Classification
   ↓
Body Projection / Mapping
   ↓
Editable Marking Geometry
```

---

## 15.2 三层识别策略

### Level 1：传统视觉

- 色彩聚类；
- HSV / Lab 分区；
- 连通组件；
- 边缘检测；
- Morphological cleanup。

优点：快、可解释、无需 GPU。

### Level 2：AI 分割

本地 ONNX：

```text
Image
 ↓
Segmentation Model
 ↓
Multi-class Mask
```

类别可以为：

```text
body_base
body_white
marking
ear_inner
paw_pad
claw
eye
accessory
background
unknown
```

### Level 3：人工修正

支持：

- Brush Add
- Brush Erase
- Polygon Add
- Polygon Remove
- Point Edit
- Smooth
- Fill Hole
- Split Region
- Merge Region

---

# 16. 花纹数据模型

```ts
interface MarkingRegion {
  id: UUID;
  name: string;
  semanticType: MarkingSemanticType;
  sourceImageId: UUID;
  view: ViewType;
  sourceMask: MaskRef;
  contour: Path2D;
  bodyRegion?: BodyRegionId;
  projectedSurface?: SurfacePatchId;
  color: ColorRGBA;
  directionDeg: number;
  scale: number;
  mirrorMode: MirrorMode;
  enabled: boolean;
  confidence: number;
}
```

---

# 17. 花纹可编辑切割路径

这是产品第一优先级功能之一。

点击 2D 或 3D 花纹后，应显示：

```text
Region
Boundary
Cut Path
Seam Path
Notch
Direction
```

## 17.1 Path Editor

支持：

- 节点拖动；
- Bézier 控制点；
- 节点插入；
- 节点删除；
- 自动平滑；
- Corner / Smooth / Tangent；
- Segment Length；
- 曲线长度；
- 等距 Offset；
- 镜像；
- 对齐；
- 吸附到身体结构线；
- 吸附到已有缝线。

## 17.2 Path 不等于 Region

必须保持：

```text
Visual Region
     ↓
Boundary
     ↓
Seam Line
     ↓
Cut Line
```

否则无法正确表达：

- 花纹视觉边界；
- 颜色拼接线；
- 缝线中心；
- 缝份；
- 实际切割线。

---

# 18. Pattern CAD 数据模型

```ts
interface PatternPiece {
  id: UUID;
  name: string;
  bodyRegion: BodyRegionId;

  outerBoundary: Path2D;
  holes: Path2D[];

  seamLine?: Path2D;
  cutLine: Path2D;
  seamAllowance: number;

  internalLines: InternalLine[];
  notches: Notch[];

  grainDirection: number;
  furDirection: number;

  materialId?: UUID;
  sourceSurfacePatch?: UUID;
  mirrorOf?: UUID;

  labels: PatternLabel[];
  metadata: Record<string, unknown>;
}
```

---

# 19. 2D CAD 操作集合

最低支持：

```text
Select
Move
Rotate
Scale
Mirror
Translate
Duplicate
Split
Trim
Join
Boolean Union
Boolean Difference
Offset
Fillet
Chamfer
Bezier Edit
Polyline Edit
Dimension
Measure
Align
Snap
Add Notch
Add Grainline
Add Label
```

---

# 20. 缝份系统

支持：

- 全局默认缝份；
- 单边缝份；
- 单段缝份；
- 不同材料缝份；
- 负缝份/吃量（高级）；
- 内缝 vs 外切线。

数据：

```ts
interface SeamAllowanceSegment {
  edgeId: UUID;
  widthMm: number;
  mode: 'constant' | 'variable';
  values?: number[];
}
```

---

# 21. 缝线与 Seam Graph

3D 身体上所有制造接缝形成图结构：

```text
SeamGraph
├─ Nodes
│  ├─ shoulder
│  ├─ armpit
│  ├─ hip
│  ├─ knee
│  └─ ankle
└─ Edges
   ├─ seam_A
   ├─ seam_B
   └─ seam_C
```

每条 Edge 包含：

```text
3D Curve
2D Mapping
PatternA
PatternB
Sew Direction
Notch Strategy
Seam Allowance
Priority
```

---

# 22. 3D 与 2D 联动

## 22.1 ID 双向关联

```text
3D Surface Face
      ↕
SurfacePatchId
      ↕
PatternPiece.sourceSurfacePatch
```

```text
3D SeamId
      ↕
2D SeamLineId
```

```text
3D MarkingId
      ↕
2D MarkingPathId
```

## 22.2 交互要求

点击 3D 花纹：

```text
Highlight Surface
→ Highlight Pattern
→ 打开对应 Path
```

点击 2D Pattern：

```text
Highlight Pattern
→ Highlight 3D Surface
→ Camera focus
```

---

# 23. UV / 制造型拆板算法

这是 FPCAD 的核心技术壁垒。

## 23.1 目标

给定一个参数化 Furry 3D 身体曲面，自动产生适合制作的 Pattern Pieces，使：

1. 曲面展开畸变尽可能低；
2. 缝线长度合理；
3. Pattern 数量不过度增加；
4. 缝线位置符合制作习惯；
5. 毛向/布向合理；
6. 关节区域活动性足够；
7. 花纹切割尽量连续；
8. 尽量减少复杂拼接；
9. 可以加入人工 seam constraints；
10. 输出可制造毫米纸样。

---

# 24. Mesh 数据结构

采用 Half-Edge Mesh。

```text
Vertex
Edge
HalfEdge
Face
FaceGroup
SurfacePatch
```

每个 Face 记录：

```text
normal
curvature
bodyRegion
material
markingId
```

---

# 25. Surface Analysis

对每个 Face 计算：

- Mean Curvature；
- Gaussian Curvature；
- Principal Curvature；
- Normal；
- Area；
- Geodesic neighborhood；
- Body region。

用于后续 seam cost。

---

# 26. Seam Candidate Generation

对于任意身体网格，自动生成候选缝线。

候选来源：

```text
A. 高曲率方向
B. 解剖区域边界
C. 关节天然折线
D. 腋下 / 腹侧等制造优选线
E. 用户指定线
F. 花纹边界
G. 镜像中心线
```

---

# 27. Seam Cost Function

建议定义：

```text
Cost(S) =
  w1 * DistortionCost(S)
+ w2 * SeamLengthCost(S)
+ w3 * PieceCountCost(S)
+ w4 * SewingDifficultyCost(S)
+ w5 * GrainDeviationCost(S)
+ w6 * FurDirectionCost(S)
+ w7 * JointMobilityCost(S)
+ w8 * MarkingFragmentCost(S)
+ w9 * VisualSeamCost(S)
```

其中权重由 Preset 控制。

例如：

```text
Studio Easy Sewing
Professional
Minimal Piece
Pattern Accuracy
Fur Direction Priority
```

---

# 28. 初始拆板算法

第一阶段使用可解释的启发式算法，而不是直接上黑箱 AI。

```text
Mesh
 ↓
Surface Segmentation
 ↓
Candidate Seam Generation
 ↓
Graph Construction
 ↓
Seed Selection
 ↓
Region Growing
 ↓
Seam Optimization
 ↓
Patch Extraction
 ↓
Flattening
 ↓
Distortion Evaluation
 ↓
Iterative Improvement
```

---

# 29. Surface Segmentation

先根据身体区域拆成：

```text
Head
Ear
Neck
Torso
Chest
Abdomen
Hip
UpperArm
ForeArm
Hand
UpperLeg
Hock
Foot
Tail
```

再允许用户重新合并/拆分。

---

# 30. Region Growing

起始点来自：

- Body region seed；
- 用户指定 seam；
- 对称 seed；
- 自动 curvature seed。

扩张条件：

```text
angle(normalA, normalB) < threshold
curvature difference < threshold
sameBodyRegion == true
```

---

# 31. 曲面展开方法

每个 Surface Patch 至少支持：

### LSCM

适合一般 patch 的初始展开。

### ARAP

用于保持局部形变更稳定的优化。

### Developable / nearly developable approximation

对接近可展开表面使用更低失真方案。

最终不要暴露算法名字给普通用户，而是提供：

```text
快速
平衡
高精度
制造优先
```

---

# 32. 展开失真评价

对每个三角形计算：

```text
AreaDistortion
AngleDistortion
EdgeLengthDistortion
```

最终：

```text
DistortionScore =
  a * AreaError
+ b * AngleError
+ c * EdgeError
```

UI 显示 Heatmap：

```text
低失真 → 正常
中失真 → 警告
高失真 → 必须拆分/重新优化
```

---

# 33. 自动再切算法

如果：

```text
DistortionScore > threshold
```

则：

```text
Find high-distortion island
↓
Search candidate seam around island
↓
Simulate split
↓
Compare score
↓
Accept if improvement > delta
```

重复直到：

```text
acceptable
OR
pieceCount > maximum
OR
iteration > limit
```

---

# 34. Pattern Manufacturing Rules

每个 Pattern 必须满足：

```text
Closed
Valid Orientation
No Self Intersection
Cut Line Valid
Seam Line Valid
Notch Valid
Grainline Valid
Area > minimum
```

如果存在错误，禁止导出制造版。

---

# 35. UV 和 Pattern 的关系

注意：

```text
UV Coordinate
≠
Manufacturing Pattern
```

UV 是曲面参数化坐标；Pattern 是制造几何。

FPCAD 必须同时保存：

```text
UV Map
+
Surface Patch
+
Pattern Geometry
+
Distortion Map
+
Seam Mapping
```

---

# 36. 花纹从 2D 双视图映射到 3D 的策略

由于只有 Front/Back 时通常无法直接得到完整侧面投影，必须采用“参考约束 + 参数化身体”的方案。

## 36.1 投影流程

```text
Front Mask
 ↓
Body-aligned Camera
 ↓
Ray Cast
 ↓
Nearest Surface
 ↓
Surface UV Coordinates
```

Back 同理。

## 36.2 冲突处理

Front 与 Back 投影存在重叠或侧面空白时：

1. 根据法线方向判断可靠性；
2. 使用视角权重；
3. 对侧面做 geodesic interpolation；
4. 对纹理边界做 smooth field；
5. 由用户选择“自动延伸”“沿身体对称”“手工补齐”。

**绝不能假设双视图可以无歧义恢复完整 3D 花纹。**

---

# 37. 花纹尺寸、方向与制造参数

每个花纹支持：

```text
Width mm
Height mm
Scale %
Rotation °
Mirror
Offset mm
Seam Margin mm
Fur Direction °
Grain Direction °
Priority
```

支持直接输入：

```text
宽度：150.0 mm
高度：230.0 mm
旋转：15°
```

并实时预览。

---

# 38. 一体填充系统

一体填充通过“身体 + Padding Volume”方式处理。

```text
Base Body
    ↓
Padding Field
    ↓
Offset Surface
    ↓
Outer Shell
    ↓
Pattern Surface
```

### Padding Field

按身体区域定义：

```text
Chest +25mm
Hip +40mm
Thigh +35mm
Shoulder +20mm
```

支持：

- 全局厚度；
- 局部体积；
- 曲线控制；
- Brush Sculpt；
- 参数化预设。

---

# 39. Foot / Paw / Claw 打版系统

## 39.1 Foot

支持：

- Plantigrade；
- Digitigrade；
- 宽脚；
- 长脚；
- 蹄状；
- 自定义。

## 39.2 Paw

支持：

```text
Palm
Finger1..N
Pad
Claw
```

支持“整片/分指”两种打版方案。

## 39.3 Tail

尾巴建议采用：

```text
Centerline
Cross Section
Length Parameter
Taper
Curvature
```

根据截面序列生成曲面后，再由算法确定缝片。

---

# 40. 3D 展示系统

Three.js 用于：

- 参数化身体显示；
- 网格检查；
- Pattern Overlay；
- Surface Picking；
- Seam Highlight；
- Marking Projection；
- UV Visualization；
- Distortion Heatmap；
- Material Preview。

Three.js 当前为 MIT，并支持 WebGL/WebGPU 渲染方向。citeturn573828search2turn573828search0

---

# 41. 3D 模型层级

```text
Scene
├─ ReferenceBody
├─ Body
│  ├─ Skeleton
│  ├─ BaseMesh
│  ├─ Padding
│  └─ OuterSurface
├─ GarmentShell
├─ PatternOverlay
├─ MarkingOverlay
├─ SeamOverlay
└─ DebugLayer
```

---

# 42. Simulation 范围

第一阶段不追求 CLO/Marvelous 等级的物理布料模拟。

MVP：

```text
Pattern → Surface Conform
```

第二阶段：

```text
Mass
Stretch
Bending
Collision
Pressure
```

第三阶段才考虑：

```text
Full Cloth Solver
```

因为物理布料模拟不是本产品的第一核心壁垒，过早实现会极大拖慢项目。

---

# 43. 2D Renderer 方案

不要把 SVG DOM 当作唯一几何模型。

推荐：

```text
Geometry Data
      ↓
Scene Graph
      ↓
Renderer
 ┌────┴───────────┐
SVG Overlay   Canvas/WebGL
```

### SVG

用于：

- 选中元素；
- 编辑控制点；
- 文本；
- 标注；
- 打印预览。

### WebGL/Canvas

用于：

- 大型 Pattern；
- 高性能缩放；
- Heatmap；
- 大量节点。

---

# 44. Undo / Redo

必须采用 Command Pattern。

```ts
interface Command {
  id: string;
  execute(): void;
  undo(): void;
  serialize(): SerializedCommand;
}
```

例：

```text
MoveNodeCommand
RotatePatternCommand
SetSeamAllowanceCommand
ChangeBodyParameterCommand
SplitPatternCommand
```

这样可以实现：

- Undo/Redo；
- History；
- 可恢复项目；
- 调试；
- 自动保存。

---

# 45. AI 系统

## 45.1 AI 模块

```text
AI Runtime
├─ Segmentation
├─ Classification
├─ Keypoint Detection
├─ Body Ratio Estimation
└─ Marking Projection Assist
```

ONNX Runtime 作为本地推理基础运行时，当前为 MIT。citeturn447249search0

## 45.2 本地优先

默认：

```text
用户图片
 ↓
本地模型
 ↓
本地结果
```

不强制上传用户兽设。

云端 AI 作为商业增强能力时，必须得到明确授权。

---

# 46. AI 模型版本管理

项目记录：

```json
{
  "modelId": "fpcad-marking-seg-v1",
  "modelVersion": "1.0.3",
  "runtime": "onnxruntime",
  "inputResolution": 1024,
  "createdAt": "..."
}
```

这样旧项目不会因为 AI 模型更新而结果不可追溯。

---

# 47. 排料系统

输入：

```text
Pattern Pieces
Material Width
Material Length Limit
Grain Direction
Fur Direction
Mirror Requirement
```

目标函数：

```text
Waste
+
Material Length
+
Rotation Penalty
+
Fur Direction Penalty
+
Pattern Separation Penalty
```

第一阶段：启发式算法。

第二阶段：遗传算法 / Simulated Annealing / Local Search。

第三阶段：Hybrid Optimization。

---

# 48. 输出系统

必须支持：

```text
PDF
SVG
DXF
PNG
FPCAD
```

## 48.1 PDF

支持：

- A4
- A3
- A2
- A1
- A0
- 自定义纸张
- 真实毫米比例
- 自动切页
- 拼接标记
- 页码
- 校准尺

### 48.2 DXF

用于：

- CAD；
- 激光切割；
- CNC；
- 其他数字制造设备。

输出必须标明：

```text
UNIT = MM
```

---

# 49. 2D Pattern 标注标准

每个 Pattern 默认显示：

```text
PART NAME
SIZE
MATERIAL
GRAIN LINE
FUR DIRECTION
CUT QTY
MIRROR
SEAM ALLOWANCE
NOTCH
REFERENCE
```

例如：

```text
TORSO FRONT L
Material: Blue Fur
Cut: 1
Mirror: No
Fur Direction: →
Seam: 10 mm
```

---

# 50. 项目数据库模型

推荐核心表：

```text
projects
characters
species
body_models
body_parameters
reference_images
markings
marking_paths
surface_patches
pattern_pieces
pattern_edges
seams
seam_links
uv_maps
materials
nesting_sheets
exports
licenses
feature_entitlements
app_settings
```

---

# 51. License / VIP 系统

## 51.1 核心思想

商业权限必须是独立领域模型：

```text
User
 ↓
Organization
 ↓
Plan
 ↓
Entitlement
 ↓
FeatureGate
```

## 51.2 推荐套餐

### Free

```text
项目创建
基础身体
基础 2D CAD
基础 PDF
有限 AI
```

### Pro

```text
高级身体
花纹识别
3D Pattern Preview
自动拆板
高级 PDF
SVG
DXF
```

### Studio

```text
批量项目
高级拆板
排料
批量导出
自定义模板
商业 AI
云同步
```

### Enterprise

```text
团队
SSO
私有部署
License Server
API
审计
本地模型
定制功能
```

套餐只是示例，真正商业定价不写死在客户端代码中。

---

# 52. Feature Entitlement 数据结构

```ts
interface FeatureEntitlement {
  featureId: string;
  enabled: boolean;
  quota?: number;
  expiresAt?: string;
  source: 'plan' | 'addon' | 'trial' | 'admin';
}
```

客户端只检查：

```ts
featureGate.require('uv.auto');
```

不要写：

```ts
if (user.vip === true) {}
```

---

# 53. License Token

建议采用：

```text
License Payload
      ↓
Canonical JSON
      ↓
Ed25519 Signature
      ↓
License Token
```

客户端内置公钥，只能验证，不能签发。

Payload 示例：

```json
{
  "licenseId": "...",
  "subject": "...",
  "plan": "studio",
  "features": [
    "uv.auto",
    "nesting.advanced",
    "export.dxf"
  ],
  "expiresAt": "..."
}
```

---

# 54. 离线授权

考虑商业工作室可能断网，必须支持离线授权缓存。

策略：

```text
首次激活
 ↓
在线签发 License
 ↓
本地安全存储
 ↓
离线工作
 ↓
定期在线刷新
```

Enterprise 支持完全离线私有 License Server。

---

# 55. 数据安全

用户项目可能包含客户兽设，属于商业敏感数据。

默认：

- 本地保存原图；
- 本地 AI 优先；
- 不默认上传；
- 云同步明确开关；
- 云端上传前显示资源范围；
- License Server 与项目数据服务器分离。

---

# 56. 插件体系

未来允许：

```text
plugins/
├─ custom-body
├─ custom-pattern
├─ export-dxf-pro
├─ laser-cut
├─ ai-model
└─ material-library
```

插件接口：

```ts
interface FPCADPlugin {
  id: string;
  version: string;
  minAppVersion: string;
  capabilities: string[];
  activate(ctx: PluginContext): Promise<void>;
  deactivate(): Promise<void>;
}
```

安全原则：

- 默认沙箱；
- 文件系统权限需声明；
- 网络权限需声明；
- 第三方插件不能直接访问 License 私钥；
- 插件版本与 App 版本兼容检查。

---

# 57. 工程目录

推荐 Monorepo：

```text
fpcad/
├─ apps/
│  ├─ desktop/
│  └─ web-admin/
├─ packages/
│  ├─ ui/
│  ├─ schema/
│  ├─ protocol/
│  ├─ command/
│  └─ feature-gates/
├─ crates/
│  ├─ geometry-core/
│  ├─ path-engine/
│  ├─ polygon-engine/
│  ├─ mesh-core/
│  ├─ unwrap-engine/
│  ├─ pattern-engine/
│  ├─ nesting-engine/
│  ├─ export-engine/
│  └─ ffi/
├─ models/
│  ├─ segmentation/
│  └─ keypoint/
├─ tests/
│  ├─ golden/
│  ├─ integration/
│  └─ fixtures/
├─ docs/
├─ scripts/
└─ tools/
```

---

# 58. Rust Core 模块划分

```text
geometry-core
├─ scalar
├─ point
├─ vector
├─ line
├─ circle
├─ arc
├─ bezier
├─ polyline
├─ polygon
└─ transform

path-engine
├─ offset
├─ boolean
├─ simplify
├─ smooth
└─ intersection

mesh-core
├─ halfedge
├─ topology
├─ normals
├─ curvature
├─ subdivision
└─ raycast

unwrap-engine
├─ segmentation
├─ seam-graph
├─ parameterization
├─ distortion
└─ optimization

pattern-engine
├─ piece
├─ seam
├─ notch
├─ allowance
├─ marking
└─ labels

nesting-engine
├─ placement
├─ collision
├─ optimization
└─ score
```

---

# 59. FFI / IPC

不让 Renderer 直接调用任意 Rust 函数。

统一走 Command API：

```text
Renderer
 ↓
IPC
 ↓
Application Service
 ↓
Rust Core
```

例如：

```ts
pattern.generateFromSurface(request)
pattern.offset(request)
uv.unwrap(request)
uv.optimize(request)
marking.project(request)
export.dxf(request)
```

---

# 60. Geometry API 示例

```ts
interface OffsetPathRequest {
  path: SerializedPath;
  distanceMm: number;
  join: 'miter' | 'round' | 'bevel';
}
```

```ts
interface UnwrapRequest {
  mesh: SerializedMesh;
  seamGraph: SerializedSeamGraph;
  options: UnwrapOptions;
}
```

```ts
interface UnwrapOptions {
  method: 'fast' | 'balanced' | 'highPrecision';
  maxDistortion: number;
  maxPieces: number;
  prioritizeFurDirection: boolean;
}
```

---

# 61. 自动保存

保存策略：

```text
编辑命令
 ↓
Command Log
 ↓
Debounced Save
 ↓
Snapshot
```

推荐：

- 普通操作 2~5 秒自动保存；
- 大型计算完成后立即保存；
- 导出前保存；
- 崩溃恢复保留最近 10 个恢复点。

---

# 62. 性能策略

## 62.1 大模型

支持：

```text
LOD0: Editing
LOD1: Preview
LOD2: Display
```

## 62.2 大量 Pattern

使用空间索引：

- R-tree；
- BVH；
- Spatial Hash。

## 62.3 长耗时任务

全部进入 Worker：

```text
AI
UV
Unwrap
Nesting
DXF Export
Large PDF Export
```

UI 不能因为一次拆板而冻结。

---

# 63. 状态管理原则

Pinia 只管理应用状态和编辑 session，不作为 Geometry Core 的数据结构。

```text
Pinia
 ├─ ProjectState
 ├─ SelectionState
 ├─ ViewState
 ├─ ToolState
 ├─ FeatureState
 └─ UIState
```

Geometry 真值存在 Rust/Serialized Domain Model。

---

# 64. UI 信息架构

```text
Home
├─ Projects
├─ Templates
├─ Materials
├─ Bodies
└─ Settings

Workspace
├─ Reference
├─ Character
├─ Body
├─ Marking
├─ Pattern
├─ 3D
├─ UV
├─ Nesting
└─ Export
```

---

# 65. 核心工作台布局

```text
┌───────────────────────────────────────────────────────┐
│ File Edit View Character Body Pattern 3D UV Export   │
├──────┬───────────────────────────────┬───────────────┤
│      │                               │               │
│Tool  │       Main Workspace          │ Property      │
│      │                               │ Inspector     │
│Bar   │       2D / 3D                │               │
│      │                               │               │
├──────┴───────────────────────────────┴───────────────┤
│ Timeline / History / Diagnostics / Task Progress      │
└───────────────────────────────────────────────────────┘
```

---

# 66. 关键交互：点击花纹看路径

用户操作：

```text
3D 点击黄色花纹
```

软件：

```text
识别 MarkingId
 ↓
找到 SurfacePatch
 ↓
找到 PatternPiece
 ↓
找到 MarkingPath
 ↓
2D 自动聚焦
 ↓
打开 Path Editor
```

用户拖动节点：

```text
2D Path 改变
 ↓
Remap to Surface
 ↓
3D Marking 更新
```

必须做到端到端可追踪。

---

# 67. 关键交互：点击 2D 缝线看 3D

```text
点击 Seam Edge
 ↓
SeamId
 ↓
3D Curve
 ↓
Camera Focus
 ↓
Highlight
```

---

# 68. Pattern Validity Checker

导出之前运行：

```text
Topology Check
Geometry Check
Seam Check
Grain Check
Notch Check
Scale Check
SelfIntersection Check
Duplicate Check
OpenPath Check
```

返回：

```text
Error
Warning
Info
```

例如：

```text
ERROR: Pattern P003 has self-intersection.
ERROR: Seam S012 length mismatch 4.7 mm.
WARNING: Fur direction differs 31° from neighbor.
WARNING: Pattern area is below recommended minimum.
```

---

# 69. Seam Length Matching

这是制造可靠性的关键。

对于一对相接缝线：

```text
Length(A) ≈ Length(B)
```

允许由于 easing 产生差值：

```text
Δ = Length(A) - Length(B)
```

如果：

```text
|Δ| > tolerance
```

则提示：

```text
Need ease / redistribute / edit.
```

---

# 70. 花纹连续性检查

跨 Pattern seam 时需要保证：

```text
Pattern seam crossing
      ↓
3D shared seam
      ↓
Marking continuity
```

高级功能：自动生成 pattern matching notch。

---

# 71. 毛向系统

每块 Pattern 必须支持：

```text
FurDirection
```

3D 身体定义：

```text
SurfaceFurVectorField
```

拆板以后将向量场投影到 2D。

如果方向变化过大：

```text
显示箭头
+
警告
```

---

# 72. 材料系统

```ts
interface MaterialDefinition {
  id: UUID;
  name: string;
  category: 'fur' | 'foam' | 'lining' | 'other';
  thicknessMm: number;
  stretch?: StretchProperty;
  furDirectionRequired: boolean;
  grainRequired: boolean;
}
```

不同材料影响：

- 缝份；
- 花纹拼接；
- 展开；
- 排料；
- 3D 预览。

---

# 73. 模板系统

模板分为：

```text
System Templates
Studio Templates
User Templates
Purchased Templates
```

每个模板记录：

```text
Species
Body Parameters
Morphs
Seam Rules
Pattern Rules
Material Rules
```

商业化后可以形成模板市场，但第一版只做本地模板。

---

# 74. 版本兼容

项目文件采用：

```text
formatVersion
schemaVersion
migrationVersion
```

以后：

```text
v1 → v2
Migration Script
```

禁止直接破坏旧项目。

---

# 75. 测试战略

CAD 软件最重要的不是“页面测试”，而是几何结果测试。

## 75.1 Unit Test

测试：

- Point；
- Line；
- Bézier；
- Offset；
- Boolean；
- Intersection；
- Transform。

## 75.2 Golden Test

保存：

```text
input.json
expected.json
expected.svg
```

用于确保算法升级后不会悄悄改变大量历史 Pattern。

## 75.3 Geometry Regression

记录：

```text
Area
Perimeter
BoundingBox
Centroid
SeamLength
DistortionScore
PieceCount
```

---

# 76. 拆板算法测试集

必须建立：

```text
Flat Surface
Cylinder
Sphere
Capsule
Torso
Leg
Digitigrade Leg
Paw
Tail
Compound Curvature Surface
```

每个样本测试：

```text
展开面积误差
边长误差
角度误差
片数
缝长匹配
```

---

# 77. 商业级算法验收指标

目标不是一开始就达到工业 CAD 全部标准，而是建立阶段性指标。

### Alpha

- 自动拆板能生成封闭 Pattern；
- 大多数基础曲面可展开；
- 用户可以手动修 Seam。

### Beta

- 常见躯干/四肢/尾巴自动拆板稳定；
- Seam Length Error 默认 < 2mm；
- 一般区域可编辑；
- 3D/2D 关联稳定。

### Commercial 1.0

建议目标：

- 典型样本 Seam Length Error ≤ 1mm；
- Pattern 几何无自交；
- 导出比例误差 ≤ 0.1%；
- 关键曲面 Distortion 有可解释评分；
- 所有自动算法可回滚；
- 同版本同输入结果确定性。

以上是工程目标，不是对所有兽体/所有材料的数学保证。

---

# 78. 质量等级体系

每个自动算法输出：

```text
Excellent
Good
Acceptable
Needs Review
Invalid
```

而不是简单：

```text
success / fail
```

---

# 79. Diagnostics 面板

用户可以查看：

```text
Pattern ID
Surface Patch
Area
Perimeter
Seam Length
Distortion
Fur Direction
Material
Source
AI Confidence
```

高级用户可以打开 Debug：

```text
Mesh Faces
Curvature
Seam Cost
Optimization Iterations
```

---

# 80. 后端商业服务

虽然桌面端可以离线工作，但商业业务建议拆出：

```text
api.fpcad.com
 ├─ auth
 ├─ license
 ├─ billing
 ├─ update
 ├─ model-registry
 └─ cloud-project
```

服务之间保持职责分离。

---

# 81. License API

示例：

```http
POST /api/v1/license/activate
POST /api/v1/license/refresh
POST /api/v1/license/revoke
GET  /api/v1/license/me
GET  /api/v1/features
```

客户端启动时：

```text
local license
 ↓
verify signature
 ↓
check expiry
 ↓
optional refresh
 ↓
Feature Registry
```

---

# 82. 更新系统

支持：

```text
Stable
Beta
Nightly（内部）
```

更新包必须签名。

客户端验证：

```text
Update Manifest
 ↓
Signature Verify
 ↓
Hash Verify
 ↓
Install
```

---

# 83. Crash Recovery

保存：

```text
last-opened-project
last-command
last-snapshot
```

启动时：

```text
Detected incomplete session
↓
Recover
or
Discard
```

---

# 84. 日志

日志分级：

```text
ERROR
WARN
INFO
DEBUG
TRACE
```

商业发行默认：

```text
INFO / WARN / ERROR
```

用户主动开启 Debug 后才收集更多信息。

项目图片/兽设默认不得进入日志。

---

# 85. 隐私

默认不收集：

- 项目内容；
- 兽设图片；
- 纸样；
- 客户角色数据。

可选择上传：

- Crash stack；
- 软件版本；
- OS；
- GPU；
- 匿名性能数据。

---

# 86. 开发阶段路线图

## Phase 0：基础工程

目标：

```text
Electron
Vue
Rust
IPC
SQLite
Project File
```

验收：

- 创建项目；
- 保存；
- 打开；
- Undo/Redo；
- 自动恢复。

---

## Phase 1：2D CAD 基础

实现：

- Point；
- Line；
- Bézier；
- Path；
- Polygon；
- Offset；
- Boolean；
- Dimension；
- SVG；
- PDF。

这是整个产品的 Geometry Foundation。

---

# 87. Phase 2：参数化身体

实现：

- Base Body；
- Morph；
- Measurements；
- Canine；
- Feline；
- Plantigrade；
- Digitigrade；
- Tail；
- Paw。

验收：

调整 1 个参数后，所有关联系统可以追踪变化。

---

# 88. Phase 3：3D 与 Pattern 关联

实现：

```text
3D Surface
↔
SurfacePatch
↔
PatternPiece
```

完成：

- 3D Pick；
- 2D Highlight；
- Seam Graph；
- Pattern Overlay。

---

# 89. Phase 4：双视图花纹识别

实现：

```text
Front / Back
 ↓
Mask
 ↓
Contour
 ↓
Editable Path
```

先不做复杂 AI。

先把传统视觉 + 手工修正流程完全打通。

---

# 90. Phase 5：自主拆板 v1

实现：

```text
Mesh
↓
Segmentation
↓
Candidate Seams
↓
Patch
↓
LSCM/ARAP
↓
Distortion
↓
Optimization
```

完成基础躯干、四肢、尾巴。

---

# 91. Phase 6：花纹映射与切割路径

目标：

```text
3D Marking
↔
2D Marking
↔
Cut Path
```

这是对外演示价值非常高的版本。

---

# 92. Phase 7：排料和 DXF

实现：

- Nesting；
- Fur Direction；
- Grain；
- Mirror；
- DXF；
- Large PDF。

---

# 93. Phase 8：AI

实现：

- 分割模型；
- 身体比例辅助；
- 花纹分类；
- 自动 projection；
- AI Assist，不取代人工。

---

# 94. Phase 9：商业化系统

实现：

- Login；
- License；
- Feature Gate；
- Subscription；
- Offline License；
- Update；
- Analytics；
- Enterprise License。

商业系统不能反过来阻塞本地 CAD 的基础能力。

---

# 95. 第一版 MVP 定义

MVP 必须可以完整完成：

```text
导入双视图
 ↓
创建角色
 ↓
设置毫米尺寸
 ↓
生成 Furry Body
 ↓
识别颜色/花纹
 ↓
人工修改花纹
 ↓
生成基础 Pattern
 ↓
手工编辑 Pattern
 ↓
加入缝份
 ↓
3D 预览
 ↓
PDF / SVG 导出
```

MVP 不必须：

- 完整物理布料模拟；
- 全自动识别所有兽设；
- 完美自动拆板；
- 复杂云协作。

---

# 96. 1.0 商业版本定义

必须：

```text
双视图识别
参数化 Furry Body
2D CAD
3D Pattern Preview
Marking Path Editor
Seam Graph
Auto Unwrap
Manual Seam Control
Paw / Foot / Tail
Padding
Fur Direction
PDF
SVG
DXF
Nesting
License
VIP
Offline License
Auto Update
Crash Recovery
```

---

# 97. 未来高级功能

```text
AI 三视图理解
AI 身体比例估计
照片测量
Fabric/Performance Simulation
Motion Test
自动花纹匹配
自动缝线推荐
自动工艺单
材料用量预测
成本核算
激光切割
CNC
打印机直接输出
团队协作
模板商店
算法 SDK
```

---

# 98. 推荐的默认用户体验

用户打开软件后看到：

```text
┌───────────────────────────────┐
│       Create Furry Project     │
├───────────────────────────────┤
│                               │
│     [ Front View ]            │
│     [ Back View  ]            │
│                               │
│     Import Reference           │
│                               │
└───────────────────────────────┘
```

然后：

```text
1. 选择物种
2. 输入身高
3. 导入双视图
4. 对齐身体
5. 识别花纹
6. 检查花纹
7. 生成身体
8. 生成 Pattern
```

整个流程必须让新用户在不阅读文档的情况下完成。

---

# 99. 核心产品原则

### 原则 1：AI 辅助，不可逆

### 原则 2：几何数据永远可编辑

### 原则 3：毫米是真实单位

### 原则 4：3D 是验证环境，不是唯一真值

### 原则 5：Pattern 是制造实体

### 原则 6：UV ≠ Pattern

### 原则 7：核心算法独立于 UI

### 原则 8：商业授权独立于业务模块

### 原则 9：离线可用

### 原则 10：算法升级必须可回归测试

---

# 100. 第一阶段最重要的技术难点排序

优先级从高到低：

```text
P0
几何内核
2D Pattern 数据模型
参数化 Body
3D↔2D ID 关联
Path Editor

P1
Seam Graph
Mesh Core
UV/Unwrap
花纹投影

P2
自动拆板优化
Nesting
AI Segmentation

P3
高级布料模拟
AI 自动三维理解
团队协作
```

**不要先做登录页面，也不要先做 VIP UI。**

真正影响产品护城河的是 P0 / P1 的 Geometry Core。

---

# 101. 实现阶段的第一条垂直闭环

第一条可运行的工程闭环必须是：

```text
一个犬科角色
        ↓
身高 1800mm
        ↓
参数化身体
        ↓
躯干 Surface
        ↓
自动生成 3~6 片 Pattern
        ↓
2D 展开
        ↓
自动缝份
        ↓
SVG
        ↓
3D Overlay
```

然后加入：

```text
黄色花纹
 ↓
投影
 ↓
2D Cut Path
 ↓
节点编辑
 ↓
重新映射
 ↓
3D 查看
```

这条闭环跑通以后，再扩大到腿、脚、爪和尾巴。

---

# 102. 第二条垂直闭环

```text
Digitigrade Leg
 ↓
Surface Segmentation
 ↓
Seam Candidate
 ↓
Auto Unwrap
 ↓
Distortion Optimization
 ↓
Pattern
 ↓
Seam Matching
 ↓
3D Preview
```

这条闭环将直接验证自主拆板算法是否有真正商业价值。

---

# 103. 第三条垂直闭环：Paw

```text
Paw Parameters
 ↓
3D Paw
 ↓
Finger Separation
 ↓
Surface Patches
 ↓
Unwrap
 ↓
Pattern
 ↓
Claw/Pad Marking
 ↓
3D Preview
```

---

# 104. AI 训练数据体系

如果后期自研模型，需要建立内部 Dataset：

```text
Reference Image
Mask
Body Region
Species
Marking Type
Keypoints
Confidence
Corrected Result
```

每一次人工修正都可以形成经过用户授权的训练候选数据，但商业产品默认不得偷偷使用客户数据训练。

训练数据必须具备明确授权来源。

---

# 105. 算法版本管理

所有自动几何算法必须带：

```text
algorithmId
algorithmVersion
parameterPreset
seed
```

这样项目可以记录：

```text
Unwrap Algorithm v1.3
Preset = FurDirectionPriority
Seed = 12345
```

避免未来重新计算后图纸发生不可解释变化。

---

# 106. 确定性与随机性

需要随机搜索的算法（如 Nesting）必须显式保存 Seed。

例如：

```json
{
  "algorithm": "nesting.hybrid",
  "version": "1.0.0",
  "seed": 824761,
  "iterations": 2000
}
```

这样用户可以重现结果。

---

# 107. 软件异常恢复原则

任何一个算法失败都必须：

```text
不损坏项目

不覆盖原 Pattern

生成新的 Calculation Result

允许 Rollback
```

例如：

```text
Pattern v17
 ↓
Auto Unwrap
 ↓
Result v18
```

不要直接覆盖 v17。

---

# 108. 算法缓存

大型算法输出必须缓存：

```text
inputHash
algorithmVersion
optionsHash
resultHash
```

如果输入没变化：

```text
直接读取缓存
```

这对大型 3D 身体非常重要。

---

# 109. 资源引用系统

项目中的图片/模型可以：

```text
Embedded
External
Linked
```

默认建议 Embedded，防止用户移动项目后引用断裂。

大型素材可以采用 external link。

---

# 110. 大文件策略

对于高分辨率参考图：

```text
Original
Thumbnail
Proxy
```

3D 纹理：

```text
Original
Compressed Preview
```

项目打开优先使用 Proxy，再后台加载 Original。

---

# 111. 后期本地服务器模式

Enterprise 可提供：

```text
FPCAD Desktop
        ↓
Local Network
        ↓
FPCAD Enterprise Server
```

用于：

- License；
- Template；
- Model；
- Team Project；
- Audit。

这样可以满足工作室/工厂局域网部署。

---

# 112. Enterprise 私有部署

推荐 Docker Compose 起步：

```text
nginx
api
license-service
model-service
postgresql
redis
object-storage
```

第一版不强制云厂商绑定。

---

# 113. API 兼容策略

所有远程 API 使用：

```text
/api/v1/
```

Major Version 变化才 breaking。

桌面端至少支持 server 最近两个 API minor version。

---

# 114. 国际化

第一版：

```text
简体中文
English
```

内部所有 key 使用英文：

```text
pattern.seam_allowance
body.digitigrade
marking.cut_path
```

UI 翻译单独管理。

---

# 115. 用户数据导入导出

支持：

```text
PNG
JPG
WEBP
SVG
OBJ
GLB/glTF
```

商业版增加：

```text
DXF
```

未来：

```text
FBX
USD
```

---

# 116. 原生文件与交换格式原则

原生项目：

```text
FPCAD
```

交换：

```text
SVG / DXF / PDF / GLB
```

不要把 SVG 作为原生工程格式，因为 SVG 无法充分表达：

- Body Surface Mapping；
- Seam Graph；
- Morph；
- UV；
- AI metadata；
- Material；
- Algorithm Version。

---

# 117. 工具开发顺序

建议：

```text
Select
Measure
Point
Line
Bezier
Path
Offset
Boolean
Notch
Dimension
Pattern Metadata
Seam
Marking
3D Pick
```

---

# 118. 第一版快捷键

```text
V  Select
M  Move
R  Rotate
S  Scale
B  Bezier
P  Path
O  Offset
N  Notch
D  Dimension
G  Grain/Fur Direction
Ctrl+Z Undo
Ctrl+Y Redo
Ctrl+S Save
```

---

# 119. GPU / 硬件兼容

最低建议：

```text
4-core CPU
8GB RAM
DX12 / Vulkan / Metal capable GPU
```

推荐：

```text
8-core CPU
16GB+ RAM
8GB+ VRAM
SSD
```

AI 高级功能：

```text
8GB+ VRAM recommended
```

无独显机器必须可以关闭 AI 与高质量渲染继续使用基础 CAD。

---

# 120. 不能依赖在线服务的核心功能

离线状态仍必须支持：

```text
打开项目
2D CAD
参数身体
3D Preview
基础花纹处理
基础 UV
PDF/SVG
```

以下可以需要联网：

```text
订阅校验刷新
云同步
在线模板
在线模型下载
高级云 AI
```

---

# 121. 后续实现必须产出的工程文档

基于本文件，正式开发阶段需要继续生成：

```text
docs/
├─ 01-prd.md
├─ 02-system-architecture.md
├─ 03-frontend-architecture.md
├─ 04-rust-geometry-core.md
├─ 05-data-model.md
├─ 06-ipc-protocol.md
├─ 07-pattern-engine.md
├─ 08-seam-engine.md
├─ 09-unwrap-algorithm.md
├─ 10-marking-recognition.md
├─ 11-body-parametric-system.md
├─ 12-3d-rendering.md
├─ 13-nesting.md
├─ 14-ai-system.md
├─ 15-license-system.md
├─ 16-cloud-services.md
├─ 17-plugin-sdk.md
├─ 18-testing.md
├─ 19-security.md
├─ 20-release.md
└─ 21-open-source-notices.md
```

本文件是这些文档的母文档。

---

# 122. 最终软件工程目标

最终软件不是一个“生成纸样的 AI 工具”，而是一套完整的 Furry 制造设计 CAD：

```text
             Furry Reference
                    │
                    ▼
          ┌────────────────────┐
          │ Reference Engine   │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Character Engine   │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Parametric Body    │
          └─────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
  Marking Engine          Body Surface
         │                     │
         └──────────┬──────────┘
                    ▼
             Seam / UV Engine
                    │
                    ▼
             Pattern Engine
                    │
             ┌──────┴───────┐
             ▼              ▼
           2D CAD          3D
             │              │
             └──────┬───────┘
                    ▼
                 Nesting
                    │
                    ▼
               Manufacturing
```

---

# 123. 最终开发结论

## 技术栈最终锁定

```text
Electron
Vue 3
TypeScript
Vite
Pinia
TailwindCSS
Three.js
Rust
SQLite
ONNX Runtime
Clipper2
Earcut
meshoptimizer
```

其中：

- Electron：桌面壳；
- Vue/TS：产品 UI；
- Three.js：3D 视图；
- Rust：商业核心几何/拆板；
- SQLite：本地数据；
- ONNX Runtime：本地 AI；
- Clipper2：2D Boolean/Offset 辅助；
- Earcut：2D triangulation 辅助；
- meshoptimizer：网格优化辅助。

Electron 和 Three.js 当前均为 MIT；ONNX Runtime 当前为 MIT；Clipper2 为 Boost；Earcut 为 ISC；这些许可证更适合构建闭源商业产品，但仍需在发行版中维护第三方 notices。citeturn573828search4turn573828search0turn447249search0turn447249search10turn787272search0

Seamly2D / Valentina / Blender 可以作为研究与交互参考，但不应直接把其 GPL 核心代码并入闭源商业 Geometry Core。citeturn787272search3turn276222search0turn573828search1

---

# 124. 最重要的开发顺序

绝对按以下顺序：

```text
1. Geometry Core
2. Pattern Data Model
3. 2D CAD
4. Parametric Furry Body
5. 3D ↔ 2D Mapping
6. Seam Graph
7. Manufacturing Unwrap
8. Marking Recognition
9. Marking Cut Path Editor
10. Nesting
11. Export
12. AI
13. License / VIP
14. Cloud / Enterprise
```

不要颠倒。

---

# 125. 下一阶段执行准则

正式进入编码后，每完成一个模块都必须同步更新：

```text
需求
架构
接口
数据结构
算法
测试
性能
许可证
版本迁移
```

所有代码实现必须以本文件中的模块边界和数据关系为基准。

如果后续发现某个算法路线不可行，优先替换内部实现，不随意破坏上层数据模型。

---

# 126. 设计参考来源

以下资料用于产品/技术方向研究，而非代码复制来源：

1. CLO 官方界面与功能文档：https://support.clo3d.com/
2. CLO API/SDK 官方文档：https://developer.clo3d.com/
3. Seamly2D：https://github.com/FashionFreedom/Seamly2D
4. Valentina：https://github.com/valentinaproject/valentina （以及其公开镜像）
5. Blender：https://github.com/blender/blender
6. Three.js：https://github.com/mrdoob/three.js
7. Electron：https://github.com/electron/electron
8. ONNX Runtime：https://github.com/microsoft/onnxruntime
9. Clipper2：https://github.com/AngusJohnson/Clipper2
10. Earcut：https://github.com/mapbox/earcut
11. meshoptimizer：https://github.com/zeux/meshoptimizer
12. libigl：https://github.com/libigl/libigl
13. CGAL License：https://www.cgal.org/license.html

---

# 127. 版本记录

| Version | 日期 | 说明 |
|---|---|---|
| 1.0.0 | 2026-09-11 | 初始完整实现基线 |

---

# 128. 工程实施声明

本文件定义的是一个可工程化落地的产品架构与实现路线，而不是声称已经解决全部计算几何、曲面展开、布料物理或 AI 三维理解问题。

尤其是“自主拆板算法”应按照：

```text
数学模型
→ 原型算法
→ Golden Dataset
→ 参数调优
→ 与人工纸样比较
→ 生产样本验证
→ 商业版本冻结
```

逐阶段验证。

在商业发行前，对第三方开源组件进行版本锁定、SBOM、许可证扫描、NOTICE 自动生成，并对自研算法开展专利/FTO 法律评估。

---

# End

**FPCAD 的核心目标：让 Furry 兽设从“图片”变成“可度量、可编辑、可试装、可拆板、可排料、可制造”的数字资产。**
