from pathlib import Path
import csv, hashlib, json, re, shutil

ROOT = Path(__file__).resolve().parent
if (ROOT/'34-实现进度与验证记录.md').exists():
    raise SystemExit('已有人工实现与验证记录，禁止重建覆盖。请直接编辑文档并运行 _validate_docs.py。')
DOCS = {}
def doc(name, title, source, body):
    DOCS[name] = (title, source, body.strip())

doc('00-文档总览与使用指南.md', '文档总览与使用指南', '全文，重点§121、125、128', r'''
## 交付边界与可信程度

本套文档服务于 FurryPattern CAD 的增量开发、测试、审查、验收、发布和维护。文档版本为 0.1.0，状态为“待评审工程基线”，不表示软件已经实现、算法已经验证或许可证已经获准。编制日期：2026-09-11。当前仓库检查时无既有代码或工程约定，本套设计不假设已有实现。

母文档作为需求资料保存于 [原始设计文档](sources/FurryPatternCAD_完整实现设计文档.md)。其中的指令性语句按产品约束和设计主张处理，不作为执行系统命令、发布产品或替用户批准商业决策的授权。原文失效的会话式引用不构成核验依据；本套文档未声称完成外部技术、法律或专利核查。

规范标签：**[源]** 表示母文档明确要求；**[补]** 表示为实现和测试新增的工程决策；**[目标]** 表示需要实验验证的阈值；**[待决]** 表示存在责任人和截止门禁的未决问题。未逐句标记的流程、协议细节及测试阈值均为[补]；需求表的来源列可定位原文。MUST/必须为本基线门禁；SHOULD/建议允许记录理由后偏离；MAY/可为可选范围。

## 阅读路径

|角色|先读|随后使用|
|---|---|---|
|产品与项目负责人|01、22、23|24、25、26、29|
|架构师与开发|02、05、06、04|各模块详细设计、27|
|前端开发|03、12、28|06、07、10、11|
|测试与制造验收|18、23、24、30|07、08、09、13、31|
|安全与发布负责人|19、20、21|15、16、25、26|
|后续自动化开发代理|00、22、23、27|仅领取当前增量中满足依赖的任务|

## 唯一事实源分工

需求范围以 01 和追踪矩阵为准；增量归属以 22 为准；数据与持久化以 05 为准；通信契约以 06 为准；算法数学口径以 04、07～14 为准；量化验收以 18、30 为准；冲突处理以 26 为准。母文档保持原样，工程修订不能偷偷改写母文档。所有文件采用 UTF-8。

每次修改必须更新需求—设计—接口/数据—测试—增量—证据关联。引用需求用 REQ-xxx、测试用 TC-xxx、风险用 RISK-xxx、决策用 ADR-xxx、变更用 CR-xxx。编号删除后保留墓碑，不重用。当前所有测试状态为“未执行”；没有代码提交、运行日志和输出哈希时不能改成通过。

## 审批与执行方式

文档准备完成不等于批准冻结。启动 I0 前由产品负责人、技术负责人、测试负责人登记评审结论；涉及材料工艺的阈值由制造顾问参与。每个增量独立经历需求细化→设计→实现→验证→评审→可运行发布→反馈。允许下一增量探索，但不得把未通过的核心安全/制造门禁留到后期补测。

审批角色尚未绑定具体人员，见 25；这是项目启动配置项，不影响阅读和建立开发任务。所有新增数字为可执行的候选验收值，变更必须通过 CR，不能因为当前结果不达标就直接降低标准。

## 文件索引

下方索引由构建脚本生成；sources 为只读语义的资料副本，contracts 为协议基础模式，templates 为实际记录模板，traceability.csv 可由表格工具打开，validation-report.json 仅报告文档结构检查。
''')

doc('01-prd.md', '产品需求与软件需求规格说明书（SRS）', '§1、7～23、34～56、64～73、86～120', r'''
## 产品目的与用户

把兽设图片转为可度量、可编辑、可检查和可制造的数字纸样。主要用户为个人制作者、工作室打版师和审查/制作人员；商业管理员管理账号和授权，不自动获得用户项目访问权。成功以完整制作闭环、毫米输出正确性、修改可追踪和数据可恢复衡量。

本地 CAD 不依赖在线账号启动。单机、单项目单写者是 1.0 编辑模式；云同步与实时协作不是同一能力。Windows/macOS/Linux 为目标桌面平台，各平台发布资格分别验收。

## 范围分层

|版本|承诺的用户价值|不计入该版本验收|
|---|---|---|
|I0|可靠创建、保存、恢复和撤销|身体与完整制造闭环|
|I1|毫米 2D 编辑与基础 PDF/SVG|自动拆板|
|I2～I3|参数身体和稳定的 2D/3D 关联|可制造性自动保证|
|I4|双视图传统识别及人工修正|神经网络准确率承诺|
|I5 Alpha|基础自动拆板、犬科第一条垂直闭环|所有兽体通用保证|
|I6 MVP/Beta|双视图到花纹切割、手工修正及预览输出|物理布料模拟、复杂云协作|
|I7|排料与 DXF 制造准备|机器直接控制|
|I8|本地 AI 辅助|无歧义三维重建|
|I9 Commercial 1.0|商业授权、更新及整体验收|团队实时协作、模板市场、完整物理解算|

全部编号需求见文末自动生成表和 23 追踪矩阵。需求优先级 Must 表示所属增量完成条件，Future 不构成 1.0 承诺。

## 主要用例

### UC-01 从参考图到制作文件

前置：用户具备来源合法的图片，材料和身体模板可用。导入 Front/Back→分别校准→选择犬科及 1800mm 身高→检查参数→分割颜色→人工修正侧面不确定区→生成身体/缝线/纸样→编辑路径→加入缝份→检查 3D Overlay→通过制造检查→输出 PDF/SVG。后置：项目存有输入、命令、算法版本、选用结果和输出清单。取消任一步不覆盖最后已接受状态。未校准图片不能直接产生带制造尺寸的输出。

### UC-02 编辑花纹并复核

选择 3D 黄色花纹→定位 MarkingId、Patch、Piece、Path→2D 修改节点→生成新 revision→重新映射→更新 3D。若修改后越界或映射不再有效，保留编辑结果并标为 needs-review，不伪造成功同步。跨片花纹连续性与缝线匹配分别检查。

### UC-03 算法失败与恢复

提交拆板任务→显示进度→可取消→候选结果独立保存→显式接受结果。任务失败、应用退出、磁盘满或撤销不改变旧纸样。重启从最后完整事务恢复，并显示未完成任务而非重复自动执行。

### UC-04 授权失效下继续工作

打开已有项目、读取已有高级几何、保存、基础 2D CAD 和基础 PDF/SVG 继续可用。新建高级计算按 entitlement 拒绝并说明原因；现有数据不删除、不加密锁死。套餐价格及配额配置由商业策略决定，不能硬编码到业务算法。

## 全局业务规则

BR-01：内部长度为 mm、角度存 rad、UI 显示 °，面积 mm²；图像像素仅存在图像域。

BR-02：Geometry Core 的已提交领域状态为几何真值；UI 预览不能绕过校验提交。UV、视觉轮廓、缝线和切割线不是同一个实体。

BR-03：AI 与自动几何均产生候选，可人工更正、可撤销、可追溯。源文档§99“AI 辅助，不可逆”与其余章节冲突，按“不得不可逆覆盖”解释，见 ADR-001。

BR-04：制造导出遇 Error 必须拒绝；Warning 必须显示并在用户确认后附入报告。非制造预览需明显标注用途，不能伪装为可加工文件。

BR-05：默认本地处理，遥测和训练授权独立、关闭默认值；项目图片不能进入默认日志。

## 非功能需求口径

精度、性能、可靠性和兼容性的量化门禁在 18 中统一定义，关联 REQ-034～041。母文档目标：Commercial 典型样本缝长误差≤1mm、制造输出比例误差≤0.1%、无自交和同版本确定性。物理打印机误差与数字导出误差分开评估。

## 用户输入与错误呈现

所有尺寸拒绝 NaN/Infinity、非法字符串和超出模板允许范围的数值；允许区域随模板版本登记。硬约束拒绝并指出参数，软约束给出可解释风险且允许撤销。删除被引用材料/曲面/参考图前必须展示依赖，并选择替换、解除关联或取消，不能形成静默悬空引用。

数据缺失时不得以默认猜测冒充用户确认；侧面空白、失配缝线和不支持的导入实体需要可定位诊断。复杂操作默认提供快速/平衡/高精度等用户语言，算法名称仅在高级诊断中显示。
''')

doc('02-system-architecture.md', '系统架构设计', '§4～8、50、57～63、80、107～113', r'''
## 架构与边界

```mermaid
flowchart TD
 U[Vue 编辑工作台] --> P[Preload 白名单 API]
 P --> A[Main 应用服务与命令协调器]
 A --> DB[(SQLite 工作库)]
 A --> W[隔离计算进程]
 W --> G[Rust 几何与制造核心]
 W --> AI[本地 ONNX 推理]
 A --> F[项目包与导出服务]
 A --> L[授权与更新客户端]
 L --> S[可选商业服务]
```

[补] I0 默认使用独立计算进程和版本化消息桥接 Rust 可执行程序；Main 不在事件循环内直接执行长耗时 FFI。后续如采用 Native binding 仍放在隔离进程内，以 ADR 和性能数据决定。WASM/CLI 复用是结构目标，不要求首版同时交付三种运行时。

## 组件职责

|组件|拥有的数据/行为|禁止职责|
|---|---|---|
|Renderer|选择、视角、工具会话、只读快照和临时拖动预览|直接访问文件、数据库、授权签名密钥|
|Preload|窄接口、请求与响应类型、订阅清理|任意 channel/任意代码执行入口|
|Main 应用服务|身份/权限检查、revision 检查、事务、任务编排、保存|计算曲线/展开求解|
|Rust Core|纯几何、拓扑、制造检查、可重复算法|Vue 状态、联网计费、UI 弹窗|
|SQLite 仓储|领域快照、命令与引用一致性|另一份独立几何算法|
|AI Worker|版本化模型推理和候选 mask|直接覆盖已接受路径|
|云端|账号、签发、计费、更新、可选资源服务|默认获取客户图片|

Rust 拥有几何语义，应用服务拥有提交权限；内存核心状态是当前已提交工作库的缓存，不产生两个独立写入者。数据库访问经 Main 仓储单一写队列；Rust 计算接收不可变快照并返回 delta/result。

## 关键写入时序

Renderer 发出命令（expectedRevision）→Main 验证请求、feature、project lock→读取快照→Worker 计算与校验→Main 再检查 revision→事务保存实体、逆向补丁、事件→提交 revision→广播新快照/差量→Renderer 刷新。计算期间发生编辑时旧结果成为 stale candidate，不能自动覆盖。

大计算采用 job.submit/job.cancel/result.accept。任务生成阶段与接受阶段是两次不同操作；接受需重新检查输入哈希、依赖版本、授权和制造有效性。导出同样固定某个 revision，清单注明该 revision，后续编辑不污染正在导出的快照。

## 失效图与恢复

Body 参数→Body mesh→Patch/Seam→UV→Pattern→Marking cut path→Nesting→Export。Marking 编辑仅使其投影与相关切割/连续性结果失效。材料厚度改变 Pattern Surface 和下游；仅颜色修改使渲染失效，不触发无意义拆板。

每个派生实体记录 dependencyHashes 和 status（valid/stale/invalid）。撤销恢复上游后只有哈希匹配才可复用缓存。损坏缓存可删除重算；用户已接受、手工编辑和迁移前数据不能作为缓存删除。

## 部署与质量属性

单机发行包含桌面壳、Rust worker、基础模板和基础传统视觉能力；AI 模型可独立下载。平台包独立签名与测试。云不可达不能阻塞本地打开。Worker 崩溃由 supervisor 标记任务失败，保留诊断并允许用户重试，禁止无限自动重启。

技术栈遵循母文档；具体版本在 I0 锁文件、工具链和 SBOM 中确定，未执行版本兼容核验。ADR-002 固定数据库/项目包分工，ADR-003 固定关联编辑语义，ADR-004 固定进程边界。
''')

doc('03-frontend-architecture.md', '前端架构与交互状态设计', '§43、44、63～67、98、114、117、118', r'''
## 组织结构

Vue 3/TypeScript，按 project、reference、character、body、pattern、marking、seam、unwrap、nesting、export 领域划分模块。每个模块含 views、tools、view-models、commands、tests，跨模块只使用 packages/schema 与 protocol 的公开类型。Pinia 保存 ProjectSession、Selection、Viewport、Tool、Jobs、Feature、UI；几何对象为带 revision 的只读投影。

2D Scene Graph 接收核心快照，Canvas/WebGL 绘制大量实体，SVG 叠加控制点/标签。Renderer 可以插值拖动预览，但提交位置必须经 core 校验；屏幕吸附半径转换到世界坐标，只作为交互公差，不改变制造公差。

## 工具状态机

Idle→Hover→PointerDown→Dragging/Creating→PreviewValid/PreviewInvalid→CommitPending→Idle。Escape 取消尚未提交的手势；失焦、窗口关闭和切换工具清理捕获与临时几何。一次拖动只形成一条领域命令；预览帧不能逐帧写 Undo。提交失败回到已提交位置并显示错误。

选中集合使用 {entityType,id,revision}；拆分或重建后按 remap 重选，无唯一后继时清空并解释，不按数组下标误选。相机移动不进入几何 Undo；可独立保留视图历史。Ctrl/Cmd+Z 只在工作台焦点且非文本输入时撤销工程命令。

## 前端命令与渲染

读取响应必须检查 revision，丢弃晚到的旧快照。长任务进度以 jobId+sequence 去重。视图组件卸载时取消订阅；任务属于项目会话而非 Vue 组件生命周期，切换面板不取消计算。

虚拟列表展示纸样和历史；仅更新 dirty 对象。大数组通过受控二进制传输，不在响应式对象中深层代理整张网格。编辑网格与显示 LOD 分离。

## 可操作交互

工作台含 2D/3D 分屏、属性、任务、历史与诊断。任何 Error 可以定位具体 Pattern/Seam/Path，显示原因与修复动作。任务面板显示阶段、取消和保留旧结果；进度未知使用不定进度而非虚假百分比。

快捷键按母文档设置 V/M/R/S/B/P/O/N/D/G，保存 Ctrl+S、撤销 Ctrl+Z、重做 Ctrl+Y；macOS 提供 Cmd 等价键。所有操作同时有菜单入口，支持中文/英文键值分离。输入框标明单位，颜色热图配文字等级与图例。

## 前端审查与验证

验证拖动取消、失焦、撤销合并、输入框快捷键隔离、事件订阅释放、旧响应丢弃、200% 缩放以及语言切换后未保存内容保留。禁止用像素截图作为几何精度依据；TC-007、TC-014、TC-034、TC-042、TC-043 覆盖主要行为。
''')

doc('04-rust-geometry-core.md', 'Rust 几何核心与数值规范', '§5、10、24～33、58～60、75～79、105～108', r'''
## 模块与类型

geometry-core 定义 ScalarMm、Point2/3、Vector2/3、Transform、Line、Arc、Bezier；path-engine 定义路径运算；mesh-core 管理 HalfEdge 与稳定 ID；pattern-engine 管理制造实体；unwrap/nesting/export 各自依赖基础层，基础层不能反向依赖 UI 或授权。

长度 f64 mm，角度 f64 rad，颜色线性/显示空间转换必须声明。2D 右手坐标 x 向右 y 向上；3D 右手坐标 +Y 向上、+X 角色左侧、+Z 角色正前方。Front 相机从 +Z 看向原点，Back 从 -Z。世界到 UI 的 y 翻转在适配器完成。

## 数值约束（候选基线）

|项|定义|用途|
|---|---|---|
|输入长度范围|绝对坐标≤10^6mm；尺寸范围另受模板约束|溢出和异常输入防护|
|几何容差 ε|1e-6mm + 1e-12×局部包围盒对角线|重合/退化判定，不作制造公差|
|曲线离散化|最大弦偏差 0.01mm，最大递归深度 24|Boolean、碰撞与输出折线|
|曲长积分|自适应积分绝对误差目标 0.001mm|缝长比较；不收敛返回错误|
|多边形整数缩放|10^4 单位/mm，舍入规则固定，乘法前检查 i64 范围|Clipper 类后端桥接|
|序列化|保留 f64 可往返表示，不统一截断到 UI 精度|避免重复编辑累积误差|

近退化输入不能只用固定 epsilon 猜测方向；方向/相交谓词采用稳健策略或明确返回 NUMERIC_UNSTABLE。每个桥接库固定版本、舍入和输入预处理，误差预算写入 golden 结果。

## 纯函数契约

输入包含几何、options、algorithmId/version、seed；输出 Result<T,DomainError> 和 diagnostics，不访问全局随机状态或系统时间影响算法。迭代顺序按稳定 ID 排序，浮点归约固定顺序。并行线程数、CPU/后端、构建标识记录到执行元数据。

同构建/同后端重复运行要求规范化结果哈希一致；跨平台采用 18 的公差比较，不承诺底层浮点逐字节一致。随机搜索用固定 PRNG 名称和版本，不能仅记录 seed 而忽略生成器。

## 几何和拓扑不变量

闭合边界末点与起点使用同一逻辑节点；外环 CCW、孔 CW；环不自交，孔在外环内且互不相交。三角形面积>ε²，半边 next/prev/twin 互反一致，face 环完整。默认只接受可定向二维流形曲面；非流形、多重边、重复面、退化面返回定位报告，修复作为独立可撤销命令。

Transform 先缩放再旋转再平移，组合顺序随类型测试锁定；非均匀缩放需重算曲长、缝份、材料方向与映射有效性。镜像翻转环方向并重新规范化，不丢失 notch 和关联 ID。

## 错误与性能

错误族：INVALID_GEOMETRY、NON_MANIFOLD、NUMERIC_UNSTABLE、SOLVER_FAILED、RESOURCE_LIMIT、CANCELLED。不得将 panic 穿越 FFI；进程级 panic 由上层隔离并保留旧状态。预分配必须受资源预算限制，超时/取消在迭代安全点检查。

验证包括解析形状、不变量性质测试、变换/逆变换测试、模糊输入和 golden；不能只以截图或求解器 success 判定正确。依赖桥接替换必须保留公开数据模型并重跑全部数值语料。
''')

doc('05-data-model.md', '数据模型、存储与项目格式设计', '§9～22、24、35、44、46、50、61、74、83、105～110', r'''
## 数据归属和生命周期

[补] 工作库 SQLite 保存当前可编辑项目和命令日志；.fpcad 是可携带的 ZIP 快照，不在 ZIP 内直接运行数据库。应用私有库保存设置、账号引用与授权缓存，禁止把许可证令牌、设备标识和账号凭据打入项目包。Main 仓储单写者维护事务，foreign_keys 开启，崩溃恢复使用 WAL 与完整性检查。

实体 UUID 字符串稳定，revision 为非负整数，时间为 UTC RFC3339。删除采用命令级 tombstone，引用重定向必须原子完成。项目快照与历史 GC 分开；只有不被当前状态、恢复点和保留历史引用的内容才可回收。

## 逻辑关系

```mermaid
erDiagram
 PROJECT ||--o{ CHARACTER : contains
 CHARACTER ||--o{ BODY_MODEL : builds
 CHARACTER ||--o{ REFERENCE_IMAGE : references
 BODY_MODEL ||--o{ SURFACE_PATCH : segments
 SURFACE_PATCH ||--o{ PATTERN_PIECE : maps
 PATTERN_PIECE ||--o{ PATTERN_EDGE : owns
 SEAM ||--|{ SEAM_LINK : pairs
 PATTERN_EDGE ||--o{ SEAM_LINK : links
 MARKING ||--o{ MARKING_PATH : derives
 MATERIAL ||--o{ PATTERN_PIECE : assigned
```

## 表字典（所有项目表带 project_id；所有可变实体带 revision）

|表|关键字段|约束与索引|
|---|---|---|
|projects|id,name,revision,format_version,schema_version,created_at,updated_at|id PK；revision 乐观锁|
|characters|id,project_id,name,species_id,measurement_json,morph_json|species_id FK；(project_id,id) 唯一|
|species|id,version,asset_hash,leg_types_json,constraints_json|项目内模板快照；不可悄悄跟随全局模板变化|
|body_models|id,character_id,topology_version,mesh_hash,parameter_hash,status|mesh_hash 引用内容寻址资源|
|body_parameters|body_id,key,value,unit,source|PK(body_id,key)；unit 枚举 mm/rad/ratio|
|reference_images|id,character_id,view,asset_id,calibration_json|scale>0，矩阵可逆；保留原图变换链|
|markings|id,source_image_id,semantic_type,mask_hash,color,confidence,status|confidence∈[0,1]；人工来源允许 null|
|marking_paths|id,marking_id,path_json,role,patch_id,mapping_hash|role boundary/seam/cut；按 marking_id 索引|
|surface_patches|id,body_id,face_ids_hash,topology_version,status|face IDs 必须属于该拓扑版本|
|pattern_pieces|id,patch_id,material_id,outer_path_id,cut_path_id,metadata_json|一片允许手工来源无 patch；制造状态单列|
|paths|id,role,nodes_json,segments_json,closed|节点/段有稳定 ID；closed 布尔|
|pattern_edges|id,piece_id,path_id,t0,t1,allowance_json|0≤t0<t1≤1；段参数相对于指定 path version|
|seams|id,name,expected_ease_mm,tolerance_mm,status|公差非负；吃量有符号|
|seam_links|id,seam_id,edge_id,side,direction|普通接缝恰有 A/B 两侧；边界缝单侧且显式分类|
|uv_maps|id,patch_id,map_hash,algorithm_run_id,unit|UV unit 明示；不可冒充 mm 纸样|
|materials|id,name,category,thickness_mm,fur_required,grain_required,properties_json|厚度≥0；属性含测量来源和版本|
|nesting_sheets|id,material_id,width_mm,length_mm,placements_json,dependency_hash|放置引用 piece+revision+instance_id|
|exports|id,project_revision,format,options_json,artifact_hash,validation_hash|仅成功生成后标 success|
|assets|id,mode,sha256,relative_path,external_uri,size_bytes,mime|embedded/external/linked；sha256 唯一索引|
|commands|id,project_id,base_revision,new_revision,type,payload,inverse,checksum|UNIQUE(project_id,new_revision)；有序可重放|
|algorithm_runs|id,input_hash,algorithm_id,version,options_hash,seed,result_hash,status|缓存 key 不包含随机运行时间|
|recovery_points|id,project_id,revision,snapshot_hash,created_at|仅引用完整提交|
|licenses / feature_entitlements / app_settings|本地私有库，key_id/token_ref/features/settings|不得导出到项目包|

复合外键或服务校验保证跨项目引用被拒绝。JSON 字段按 schemaVersion 验证，不能以“灵活 JSON”为由省去类型、范围和必填约束。大型 mesh/mask 放 assets，数据库存引用，提交前校验资源存在且 hash 一致。

## 关键结构语义

Path={id,revision,closed,nodes:[{id,xMm,yMm}],segments:[{id,type:'line'|'cubic',from,to,c1?,c2?}]}。控制点与节点坐标都为 mm；连续性以节点引用确定。PatternPiece 保存 outerBoundary、holes、seamLine、cutLine、逐边 allowance、notches、fur/grain rad、cutQty、mirror、material、来源和失效状态。Notch 以 edgeId+归一化弧长定位，不能仅保存屏幕坐标。

SurfaceBinding={bodyId,topologyVersion,faceId,barycentric:[u,v,w],side,sourceRevision}，u+v+w≈1 且分量在允许边界内。映射记录 patch→piece 的展开变换、缝线边界两侧副本和 orientation。拓扑变化必须提供旧新 ID remap；无可靠映射则 stale。

## .fpcad v1 内容

沿用母文档的 manifest.json、project.json、character.json、body.json、markings.json、patterns.json、seams.json、uv.json、materials.json、nesting.json、simulation.json 与 thumbnails/references/assets/history。未启用模块也输出带 schemaVersion 的空集合，不以缺失文件表示多种状态。

manifest 另含 schemaVersion、migrationVersion、files:[{path,size,sha256}]。contentHash 定义为按 UTF-8 路径排序后的 files 清单规范 JSON 的 SHA-256；清单不含 manifest 本身，避免循环哈希。ZIP 时间戳不进入内容哈希。hash 提供完整性，不提供来源真实性。

## 原子保存与自动恢复

编辑命令：校验→同一事务写 domain、command/inverse、revision→commit→内存快照发布。写临时资源先落盘再提交引用，失败产生的未引用资源稍后 GC。

自动保存：普通编辑防抖 3 秒、连续编辑最多 30 秒建立恢复快照，大计算接受后立即建立恢复点，默认保留最近 10 个。显式保存：固定 revision→写同目录临时 ZIP→校验每项 hash→flush→原子替换目标→更新成功标记。替换失败保留旧文件和恢复快照；禁止先删原文件。导出前固定并持久化快照，保存失败停止制造导出。

Undo 使用已保存逆补丁，Redo 使用原始确定性补丁；重做不重新运行可能升级的算法。Undo 后新编辑清空当前 redo 分支，但保留恢复策略要求的版本。磁盘不足时明确显示“未保存”，不能假报成功。

## 迁移与损坏处理

每次迁移 vN→vN+1 为可测试函数，先备份，写新工作副本，验证引用/几何/资源后切换；失败不改源包。不支持的新 major 以受限只读方式或明确拒绝打开，不覆盖保存。未知可选扩展字段原样保留；未知必需特性拒绝可写打开。外链缺失保留元数据和占位图，重定位时核验哈希并作为命令记录。

ZIP 导入拒绝绝对路径、..、符号链接、重复路径、大小写碰撞和超限解压；限额见 19。迁移测试至少覆盖最早支持版本到当前版本和中途故障。
''')

doc('06-ipc-protocol.md', 'IPC、任务与接口契约', '§7、44、59、60、81、113', r'''
## 信任边界和版本

唯一 Renderer 入口 window.fpcad 下的白名单方法，禁止 invoke(channel:any) 或传绝对输出路径。protocolVersion 当前为 1，schema 包生成 TS/Rust 校验类型；请求到 Main、Main 到 Worker 均执行运行时校验。连接握手交换协议 major、支持能力和构建版本，不兼容时拒绝写操作。

## 通用消息

请求：{protocolVersion:1,requestId:UUID,method:string,projectId?:UUID,expectedRevision?:integer,payload:object}。所有项目修改 expectedRevision 必填；project.open 用已由原生选择器生成的 fileHandle，project.create 无 projectId。requestId 为幂等键，作用域为会话+projectId+method，相同 ID 不同 payload 拒绝。

响应：{protocolVersion:1,requestId,ok:true,data,revision?} 或 {protocolVersion:1,requestId,ok:false,error:{code,messageKey,details,retryable}}。事件：{protocolVersion:1,eventId,projectId,sequence,type,data}。基础 JSON Schema 见 contracts/ipc-envelope.schema.json；该文件只验证外壳，方法 payload 必须按下表实现，不能视为完整运行校验器。

## 方法目录

|方法|payload 必填|结果/状态|权限/幂等|
|---|---|---|---|
|project.create|name,unit:'mm'|projectId,revision=0|本地基础；请求去重|
|project.open|fileHandle|projectId,revision,warnings|原生 handle，非任意路径|
|project.save|destinationHandle?|savedRevision,contentHash|基础；保存同 revision 幂等|
|project.snapshot|getRevision?|snapshot,revision|基础只读|
|command.apply|commandType,arguments|revision,changedIds,diagnostics|按命令 feature 检查|
|command.undo / redo|commandId|revision,changedIds|仅当前可撤销/重做命令|
|reference.calibrate|referenceId,pixelPoints[2],knownDistanceMm|calibration,revision|reference.basic|
|body.setParameters|bodyId,values,templateVersion|revision,invalidatedIds|body.parametric|
|pattern.offset|pathId,distanceMm,join,miterLimit|候选路径或 jobId|pattern.seam-allowance|
|pattern.boolean|operation:'union'/'difference',pathIds|候选路径和拓扑诊断|pattern.basic|
|seam.link|edgeA,edgeB,direction,expectedEaseMm,toleranceMm|seamId,diagnostics,revision|pattern.seam|
|job.submit|kind,inputRefs,options,algorithmVersion,seed|jobId,baseRevision|按 kind 检查|
|job.cancel|jobId|cancellationRequested:true|任务所属项目|
|result.accept|jobId,resultHash|revision,invalidatedIds|重新校验 feature 和 baseRevision|
|result.discard|jobId|discarded:true|幂等；不删已接受版本|
|validation.run|scope,profile,revision|reportId,issues,blocking|只读|
|export.create|format,revision,options,destinationHandle,warningAckIds|jobId|格式 feature+制造门禁|
|feature.list|无|entitlements,offlineState|返回能力，不返回私密 token|

job.kind 白名单：uv.unwrap、uv.optimize、marking.recognize、marking.project、nesting.solve、ai.segment；不能任意拼接 Rust 函数名。各算法 options 由对应详细设计定义。

## Offset 与 Unwrap 具体约束

offset：distanceMm 有限、绝对值≤10000；join=miter/round/bevel，默认 round；miterLimit≥1 默认 2；负值为内缩。闭合 path 方可生成制造轮廓；空结果为合法诊断 EMPTY_RESULT 但不能接受为制造片。

unwrap options：method=fast/balanced/highPrecision 默认 balanced，maxPieces 整数[1,200] 默认 50，maxIterations[1,2000] 默认 100，maxDistortion 为 09 定义的无量纲分数，默认 0.05，prioritizeFurDirection 布尔，presetId+version 必填，timeBudgetMs 默认 60000。限额是保护边界；质量不足仍不得因算法结束标记合格。

## 长任务状态机

queued→running→succeeded / failed / cancelled；succeeded 的候选再进入 accepted / discarded / stale。每个 job 固定 baseRevision、dependencyHashes、algorithm/options/seed、资源预算。进度事件含 jobId、stage、completed、total?、sequence；UI 以序列去重。重复 cancel 返回当前状态；若已 succeeded 则取消不撤回结果。接受与取消竞争在 Main 单写队列线性化，只有一个终态生效。

默认同步请求超时 10 秒；复杂计算提交后立即返回 jobId，Worker 的预算独立计算。超时不等于事务未提交：客户端以原 requestId 查询/重试，不能换 ID 盲目重复。去重记录随项目命令持久化；非修改请求只需会话缓存。

## 错误约定

|code|含义|客户端动作|
|---|---|---|
|VALIDATION_ERROR|字段类型/单位/范围错误|定位字段，不自动重试|
|REVISION_CONFLICT / STALE_RESULT|项目或依赖已变化|刷新差异、重新计算或取消|
|FEATURE_DENIED|缺少当前高级能力|解释能力；基础操作继续|
|INVALID_GEOMETRY / NON_MANIFOLD|几何不满足算法前提|定位实体并手工修复|
|RESOURCE_LIMIT / TIMEOUT|内存/时间超预算|保留输入，可降低规格重试|
|IO_ERROR / DISK_FULL|存储失败|保持 dirty，展示恢复路径|
|CANCELLED / WORKER_CRASH|任务终止|保留旧结果；可手动重试|
|PROTOCOL_UNSUPPORTED|版本不兼容|禁止继续写入，提示更新|

二进制大对象以 Main 签发的 assetHandle+sha256+字节数引用，Renderer 不传任意磁盘路径；IPC JSON 上限 8MiB，超出返回 RESOURCE_LIMIT。传输分块和重试不改变语义内容哈希。
''')

doc('07-pattern-engine.md', '纸样、路径与制造导出详细设计', '§17～20、34、43、48、49、68、116、117', r'''
## 实体和操作

PatternPiece 是制造聚合根，包含外轮廓、孔、缝线、切割线、缝份、内部标记、对位剪口、材料和裁剪数量。视觉花纹区域、几何边界、拼接缝线和刀路必须分离。所有段/节点有稳定 ID；split/trim/join 输出 old→new remap，依赖不能按数组下标维护。

I1 支持点、线、三次 Bézier、闭合路径、移动/旋转/缩放/镜像/复制、分割/修剪/连接、Union/Difference、Offset、圆角/倒角、尺寸/测量/对齐/吸附、Notch/Grain/Label。复杂操作无法保持关联时事务提交新几何并标记关联 stale，不静默丢失。

## 缝份流程

优先级：单段设置>单边设置>材料默认>项目默认（候选 10mm）。缝份从 seamLine 计算到 cutLine；outerBoundary 表示无缝份基准，不能对已有 cutLine 再次偏移导致重复缝份。外环向外、孔向内；join 和 miterLimit 来自接口。可变缝份按弧长线性插值，必须记录采样点 (s,widthMm)，s 递增覆盖[0,1]。

处理顺序：检查基准路径→离散化→逐段偏移→连接角点→处理局部环→规范环方向→关联剪口→检查孔和窄区。不能无提示删除偏移产生的小区域。负缝份/吃量作为高级参数，必须区分 expectedEaseMm 与 cut offset，二者互不替代。

## 制造检查规则

|规则|等级|修复|
|---|---|---|
|外环未闭合、自交、退化、孔外置|Error|节点修复/重建轮廓|
|cutLine 缺失或不合法|Error|重算缝份|
|关联 stale / 关键资源缺失|Error|重新映射/补资源|
|缝长残差超过 profile 公差|Error|声明吃量或修改接缝|
|必须毛向/布向缺失、裁剪数量≤0|Error|补充制造参数|
|剪口越出有效边/形成危险窄口|Error|重新定位|
|面积<25mm²、最小宽度<2mm|Warning（候选工艺阈值）|确认材料工艺或合并|
|邻片毛向变化>30°|Warning|调整方向或明确确认|

每条诊断返回 ruleId、severity、entityIds、实际值、阈值、单位、修复动作。必须区分数学无效与工艺风险。工艺 profile 版本随输出保存。

## 输出契约

PDF：pt=mm×72/25.4；A4/A3/A2/A1/A0 与自定义页，1:1 默认，页边距 10mm、重叠 10mm 为候选配置；输出页码、拼接十字、裁剪/缝线图例、100mm 校准尺、版本和纸样 ID。大幅纸样按可打印矩形覆盖，边界至少有重叠且不会漏片。输出字体须满足嵌入权限，中英文均验证。

SVG：width/height 显式 mm，viewBox 数值对应 mm；外环/孔 winding 一致，Cut/Seam/Notch/Label 分组。PNG 仅作为带 DPI 和比例说明的预览，不将屏幕导图默认认定为制造真值。

DXF：候选 AC1015（R2000）子集，$INSUNITS=4；优先 LWPOLYLINE/LINE，曲线默认按 0.01mm 弦误差折线化；图层 CUT、SEAM、NOTCH、GRAIN、LABEL。不承诺任意第三方设备都接受，必须按 31 的外部解析回读和实体清单验证。机器驱动与设备 G-code 不在 1.0。

导出只使用固定 revision 的通过检查快照；Warning 需确认 ID 集，Error 禁止制造输出。生成至临时文件并成功校验后提交目标；报告记录比例、坐标范围、数量、材料、mirror、算法/工艺版本和 hash。数字比例合格不代表打印驱动“适合页面”后仍合格。

## 测试重点

矩形 100×200mm 外偏移 10mm 的 miter 轮廓应为 120×220mm；带孔图形检查偏移方向；尖角、极短边、重叠边、负偏移完全消失、切线相交和零宽缝份分别验证。TC-005～010、TC-022、TC-023、TC-045 为门禁。
''')

doc('08-seam-engine.md', '缝线图、缝长与对位设计', '§20～22、26～30、67～71', r'''
## 模型

SeamGraph 的节点是制造连接点，边包含 3D 曲线、两侧 2D edge 引用、方向、吃量、剪口策略、允许区域和用户锁定标记。开放制造边允许单侧且 type=boundary；普通拼接必须 A/B 两侧；三片交汇用多个成对 seam 和同一 junction 表达，不用未定义的三侧边。

边引用使用 {pieceId,edgeId,pathRevision,sStart,sEnd,orientation}，s 为归一化弧长。任何路径拓扑修改必须更新映射。用户指定 seam 为硬约束，自动优化不能为了分数更低而删除。

## 匹配与吃量

定义 Δ=L(A)-L(B)，声明吃量 e=expectedEaseMm，验收残差 r=|Δ-e|。e 正数表示 A 长于 B。普通无吃量 e=0。Beta r<2mm，Commercial 典型样本 r≤1mm；不以切割线周长代替缝线弧长。差量和公差都以 mm 展示。

e 非零时需记录分布函数 q(s) 与制作备注；默认按弧长均匀，局部集中吃量必须显式设置且 q 归一化。改变 e 会改变对位映射，但不得偷偷缩放原纸样。

## 剪口和连续性

对位位置按已声明 orientation 映射 A 的 s 到 B 的 s 或 1-s，再应用吃量分布。剪口有编号、类型、深度和 seamId；左右镜像改变方向并维持对位编号。候选深度 3mm，必须小于该处缝份且不造成无效切割线，否则 Error。

花纹跨缝交点投影到共同 seam 弧长参数，定义连续性残差为对应弧长位置差。候选普通无吃量样本≤1mm；有吃量按映射后比较。多次交点须保持排序与一一关联，无法唯一配对为 Needs Review。毛向是有向量，不能把相反方向当等价。

## 编辑事务

create/link/unlink/split/merge/lock/editEase 都通过 Command；删除 Pattern 或 Edge 必须先显示受影响接缝。拆分 seam 继承锁定、方向和映射并生成新 ID；原 ID 保留追踪墓碑。undo 恢复完整关系而不仅是曲线坐标。

## 验证

等长直线、不同参数化相同曲线、反向曲线、带吃量、三片交汇、镜像、路径分裂及 notch 越界作为测试集。输出同时展示 L(A)、L(B)、e、r 和 tolerance，允许人工审查是否误用总周长。TC-015、TC-016、TC-021 覆盖。
''')

doc('09-unwrap-algorithm.md', '制造型拆板与曲面展开算法规格', '§23～35、69、71、76～79、90、101～108、128', r'''
## 目标和前提

输入为带 bodyRegion/material/fur 字段的流形三角网格、用户 seam 约束和版本化 preset。输出为 SurfacePatch、UV、毫米 Pattern、SeamMapping、DistortionMap、诊断和 provenance；UV 不直接作为制造坐标。局部可展开曲面可精确或近似展开，双曲率区域必须暴露残余形变和制造风险。

## 可实现算法流程

1. 预检拓扑、单位、退化面和用户缝线连通性；拒绝非法输入，修复另建命令。
2. 计算面积、法线、曲率和区域邻接；固定 ID 顺序。
3. 从解剖边界、腋下/腹侧、曲率、花纹、对称线和用户线构造候选图；锁定线不可移除。
4. 按区域 seed 生长，以法线夹角和曲率差限制；阈值属于 preset，不散落硬编码。
5. 提取 patch；检查连通性与边界。非盘状 patch 添加显式切边形成可参数化域，记录新增 seam；不能把孔静默填平。
6. 快速模式优先平面/圆柱解析展开，否则 LSCM 初值；平衡/高精度在初值上做 ARAP。约束两个不重合锚点消除自由度，锚点按测地距离和稳定 ID 决定；毫米尺度由原 3D 边长拟合恢复。
7. 检查三角形翻转、重叠和数值收敛，计算每面指标。
8. 对超阈区域试切，比较归一化制造成本；改进达阈值才接受；不满足条件保留最好合法候选并标 Needs Review。
9. 构造毫米边界和缝线映射，独立检查封闭、自交、缝长和毛向；输出候选，等待接受。

## 误差和成本定义

对三角形 t，A3/A2 分别为原曲面和展开面积，e3/e2 为对应边长，θ3/θ2 为局部三角形内角：

EA(t)=|A2/A3-1|；EE(t)=max_edges |e2/e3-1|；Eθ(t)=max_angles |θ2-θ3|/π。D(t)=0.4EA+0.4EE+0.2Eθ。报告面积加权平均 D、p95、max；不只报告一个均值掩盖局部极端。零面积先作为无效输入拒绝。

全局 Cost=Σ wi×Ci，所有 Ci 必须无量纲。失真取面积加权 D；缝长除以输入总边长尺度；片数除以 maxPieces；毛向偏角除以 π；缝制复杂度使用短边/急角/交汇的归一化计数。关节活动和视觉 seam 代价暂为专家标注代理，不能宣称证明活动舒适度。权重归一化和版本必须保存。

候选初始 profile：D p95≤0.05、最大 EA≤0.15、最大 EE≤0.10、无翻转/重叠；仅是 I5 实验目标，商业制造适用性须由材料样本验证。自动再切接受改善 δ≥0.001，且硬约束不退化。最大片数/迭代/时间预算见 06；达到预算不等于质量通过。

## 等级

Invalid：翻转、自交、开放制造边界或数值失败。Needs Review：几何合法但超 profile 或关联存在不确定。Acceptable：硬规则和全部 profile 限值满足。Good：D p95≤0.03 且缝残差≤0.8mm。Excellent：D p95≤0.015 且缝残差≤0.5mm。后两档为候选展示等级，仍需通过制造检查，不能代替布料验证。硬错误优先于评分。

## 原型与增量验收

I3 用明确的解析/预制 patch 验证映射，不能冒充通用自动拆板。I5 使用 1800mm 犬科模板躯干基准生成 3～6 片、加入缝份、SVG 和 3D Overlay。I6 扩展完整 MVP 花纹闭环。第二条闭环为趾行腿，第三条为整片/分指 Paw，并在 I7 前完成制造验证。

失败时保留算法中间报告、最好候选和旧已接受纸样；永不覆盖旧版本。缓存 key=输入规范内容+依赖模板/材料版本+算法版本+options+seed+后端标识，缺任一项不能复用。

## 实验登记

每次实验保存 mesh hash、手工基准来源、参数、seed、backend、构建、运行耗时、峰值内存、各误差分布、片数、缝长以及人工缝制结论。LSCM/ARAP 求解器和具体实现许可仍待选，见 RISK-001 与 DEP-待核验；数学路线本身不代表生产可用实现。
''')

doc('10-marking-recognition.md', '参考图、花纹识别与双向映射设计', '§14～17、22、36、37、66、70、89、91', r'''
## 标定和图像管线

支持 PNG/JPG/WEBP，Front/Back 必须分别记录人物顶部/底部两点和已知长度。mmPerPx=knownDistanceMm/pixelDistance，例 1800/1200=1.5。拒绝重合标点、负长度和解码失败；图像 EXIF 旋转先规范化，并把裁切/缩放/旋转矩阵写入 calibration，不能在降采样图上误用原始像素比例。

I4 基础管线：背景候选→颜色空间归一化→Lab/HSV 聚类→连通区域→孔/噪声清理→轮廓→Bézier 拟合→语义候选。原图永不被预处理覆盖；每一步带参数和版本。拟合以毫米弦误差≤0.5mm 作为候选目标，细节被删除时显示变化预览。

## 人工修正

Brush Add/Erase、Polygon Add/Remove、节点编辑、平滑、填孔、拆分/合并区必须可撤销。mask 是像素分割资料，path 是可编辑几何；手工修改 path 后不能下一次自动推理覆盖。保存 source='manual'/'vision'/'ai'、锁定状态、confidence 可空、来源 mask 和模型版本。

投影不确定区域标 unknown，不能以默认主体色掩盖缺失。禁用区域保持原数据但不参与输出。

## 投影与逆映射

使用对齐相机射线与可见最近面求交，保存 faceId+重心坐标+topologyVersion。正背图重叠时以法线夹角和遮挡置信度生成候选；侧面无数据时用户选择自动延伸、对称或手绘，补全面保留 provenance='inferred' 和审核状态。双视图不能无歧义还原侧面。

3D→2D 通过 patch 参数化映射，跨 seam 的花纹必须拆成多个 path，仍归属同一 MarkingId。2D path 编辑逆映射到有效 patch；超出域、退化三角形、缝线歧义返回可定位错误或 Needs Review，不能映射到最近任意面。

3D 点击链：MarkingId→bindings→PatchId→PieceId→PathId；若一对多则同时高亮并允许选择，不武断打开任意片。修改宽高、旋转和镜像均以 mm/rad 领域参数提交，UI 百分比转换在边界执行。

## 性能和验证

图像 Original/Proxy/Thumbnail 分离，候选推理基于记录分辨率；反投影时还原完整变换。测试包含正背重叠、遮挡、透明背景、EXIF 旋转、噪声、侧面空白、跨缝路径、模板拓扑升级、人工锁定与撤销。TC-017～021、TC-046 为主要门禁。
''')

doc('11-body-parametric-system.md', '参数化身体、材料与模板设计', '§11～14、38、39、71～73、87、101～103', r'''
## 参数定义

模板版本包含基础网格、稳定拓扑、解剖区域、Morph Targets、测量路径、硬/软约束、物种/腿型兼容性和来源许可。项目保存模板快照，更新模板不直接改旧项目。

|类别|参数|单位/验证|
|---|---|---|
|身体测量|height,neckGirth,chestGirth,waistGirth,hipGirth,shoulderWidth,armLength,legLength,footLength,headWidth,headLength|mm，正数，范围由模板登记|
|动物形态|snoutLength,snoutWidth,earHeight,earWidth,tailLength,tailBaseGirth,tailTipGirth|mm，允许长度为零需模板明确|
|姿态|earAngle|rad，UI 为度|
|肢体|upperArmGirth,forearmGirth,thighGirth,shinGirth,pawLength,pawWidth,clawLength|mm；paw/指数量受模板约束|
|填充|chestPadding,hipPadding,thighPadding,bellyPadding,shoulderPadding|mm 局部厚度，非负|
|材料层|foamThickness,furThickness,liningThickness,bufferAllowance|mm 非负，按材料 profile 生效|
|Morph 权重|chestWidth,hipWidth,snoutLength 等 target 权重|ratio；与同名测量字段命名空间分离|

禁止把 snoutLength 的 mm 与 morph.snoutLength 的无量纲倍率混用。母文档 chestGirth>0.8×waistGirth 作为软约束示例，不作为所有体型的硬限制。

## 生成流程

读取已锁定模板→校验 Measurements→求解 Morph 权重→应用约束→计算 Base Body→局部 Padding Field→材料层参考面→生成 Pattern Surface→重算区域与 bounds→下游失效。基础位置和 Morph 保持同一拓扑；切换物种/腿型若改变拓扑则使用新 topologyVersion 并显式重新绑定。

测量到 Morph 的求解使用带范围限制的误差最小化，输出每项目标与实测残差。候选 I2 门禁：身高 1800mm 残差≤1mm，胸/腰/臀测量残差≤max(2mm,目标×0.5%)。不能满足时显示残差并拒绝声称已满足测量。

## 毛、泡棉与内衬

分别保存身体表面、填充外表面、制造参考面和毛发视觉外观。毛长不默认全量加到裁片尺寸；材料 profile 定义有效补偿厚度及来源。I2 先实现全局/局部参数化 padding，Brush Sculpt 高级编辑在 I7 范围内；任意雕刻可能改变拓扑时触发重新绑定。

材料包括 category、thickness、stretch（方向/测量条件）、fur/grain required、允许旋转和默认缝份。未经实验标定的弹性参数只能标“估计”，不能用于宣称真实试穿效果。

## 物种与特殊部位

I2 提供犬/猫基础与植腿/趾行、尾/爪参数；I5 起验证自动制造。兔/熊/鹿/龙/Custom 的模板扩充在 I7 纳入 1.0 目标，各自必须通过模板兼容和制造数据集，不允许只在下拉框列名称。Foot 支持植腿/趾行，宽/长/蹄与自定义作为模板变体；Paw 表达 Palm、Finger1..N、Pad、Claw，可整片/分指；Tail 用中心线、截面、taper、曲率生成曲面。

本地模板支持 System/User/Studio；Purchased/市场为未来。导入模板检查版本、资源 hash、许可和参数边界；“模板文件”不得执行任意脚本。

## 验证

参数最小/最大/组合边界、镜像、拓扑稳定、测量残差、非负厚度、自交、尾尖零半径处理、爪指分离以及旧项目模板冻结，分别执行 TC-011～013、TC-024、TC-044。
''')

doc('12-3d-rendering.md', '3D 展示、拾取与预览设计', '§22、35、40～43、62、66、67、71、119', r'''
## 场景和数据

Three.js 只负责展示与拾取适配。Scene 下分 ReferenceBody、Body/Skeleton/BaseMesh/Padding/OuterSurface、GarmentShell、PatternOverlay、MarkingOverlay、SeamOverlay、DebugLayer。网格顶点到领域 faceId 的映射与 buffer 一起版本化；不能以当前 draw index 作为持久 ID。

世界坐标遵循 04，渲染单位 1=1mm；深度精度通过相机 near/far 和局部原点管理，不改变制造数据。选中使用 ID overlay 或受控 raycast；显示 LOD 必须映回编辑网格，无法唯一定位时切换到编辑网格重新拾取。

## 2D/3D 修改语义

尺寸修改或纸样自由变形不自动“精确逆推”身体。对于仍在同一 patch 参数域的花纹节点，可逆映射实时更新；纸样边界或拓扑修改使贴合和缝线失效，需重新生成绑定/预览。Body 参数修改向下游传播 stale，而非强行变形已人工批准的纸样。此决策见 ADR-003。

MVP 为 Surface Conform 预览，明确标“几何贴合预览”，不表示受力、舒适性或真实布料垂坠。物理模拟在 Future 范围，质量等级不能误导用户。

## 热图与方向

按 09 的每面 D 显示固定刻度图例，同时可切换 EA/EE/角误差；Error 使用图案和文字，不只靠颜色。2D fur 向量由表面切向量通过映射 Jacobian 变换后归一化，奇异映射为无效。3D 材料预览改变颜色/毛外观不修改真实裁片。

## 资源与降级

切换项目时释放 geometry/material/texture/render target 和订阅。原始纹理异步加载，先 proxy；Worker 构建 BVH 等索引。GPU 不可用或 context lost 时保存当前领域状态，允许恢复渲染或关闭 3D 使用基础 2D；AI 可关闭。WebGL/WebGPU 后端选择必须通过平台测试，不把硬件宣传能力当兼容性证据。

TC-014、TC-020、TC-034、TC-035、TC-040 测试拾取正确性、映射失效、帧延迟、显存释放和设备降级。
''')

doc('13-nesting.md', '排料与材料利用率设计', '§47、49、71、72、92、106', r'''
## 输入和硬约束

输入为通过制造检查的 Pattern revision、实际 cutLine（含缝份）、cutQty、材料 ID/幅宽/长度上限、边距/片间距、fur/grain、允许旋转集合、mirror requirement、seed、算法版本。每个裁剪实例有 instanceId，镜像件为明确实例，不能把 Cut 2 自动当成同向重复。

不得跨材料合排；必须在有效布幅内，片间距离≥配置间隙，全部实例恰好一次。默认禁止利用内部孔洞放其他片，后续如支持须作为明确选项及工艺验证。毛向有方向性，180° 反转不是默认可行；有纹理材料的旋转集合由材料 profile 限定。

## 初始可实现算法

按面积降序、instanceId 打破平局→生成候选方向→底左放置与轮廓碰撞→对可行摆放做局部搜索→保留当前最好可行解。高级阶段再引入退火/遗传/混合；未证明更优不替换已存在更好结果。

碰撞使用 cutLine 扩张 gap/2 的保守多边形，空间索引先粗判，再精确检测；离散化误差加入安全裕量。纸样放不下时输出明确 unplaced 列表和原因，不能丢片后仍标 success。

## 指标

利用率=全部实例净 cutLine 面积之和/(布幅×实际占用长度)，孔面积按几何扣除但不因此允许嵌套。同时报告含边距占用、总长度、未放置件、方向违规数和碰撞数。优化目标先满足硬约束，再最小长度，再比较方向/分离等软代价；不能用加权低分抵消碰撞。

options 候选：sheetWidthMm>0，lengthLimitMm>0，gapMm≥0 默认5，marginMm≥0 默认10，rotationsRad 数组非空，iterations 默认2000，上限100000，timeBudgetMs 默认60000。成本和 seed 固定，预算到期返回最好可行候选；无完整可行解标 Needs Review 且禁止整单制造导出。

## 修改与验收

用户手动拖动/旋转同样走碰撞和方向检查；锁定实例不能被自动优化移动。纸样、数量、材料或毛向变化后既有排料 stale；导出必须再次检查全部实例。

测试空集、超宽片、孔洞、镜像、禁止旋转、混合材料、锁定实例、固定 seed 和已排料后修改尺寸。TC-025 要求零碰撞/越界/漏件，启发式对固定基准占用长度不劣于确定性底左基线；不承诺全局最优利用率。
''')

doc('14-ai-system.md', '本地 AI、模型和数据治理设计', '§15、45、46、85、93、104、119', r'''
## 范围

I8 为分割、语义分类、关键点、比例估计和投影辅助提供 ONNX 本地适配。传统视觉与手工修正仍是完整可用路径。模型缺失、显存不足或后端失败时可切 CPU 或传统流程，不损坏已接受花纹。云 AI 和客户数据训练默认关闭。

## 模型制品契约

ModelManifest 包含 modelId/version、sha256、文件大小、任务、输入名称/shape/dtype、颜色空间、normalization、resize/padding、输出名称/shape、类别映射、opset、运行时约束、模型许可、训练数据授权概要、支持后端和质量报告引用。推理需锁定 manifest，不仅保存 .onnx 文件名。

下载到临时文件，校验来源签名和 hash，再原子加入 registry。不自动执行模型附带脚本。模型升级不重跑旧项目；用户明确发起重新识别才生成新候选。结果保存模型/运行时/后端/输入 hash/预处理参数及时间。

## 推理管线

原图 proxy→固定归一化→尺寸适配→本地推理→mask/置信度→移除 padding→还原原始图变换→10 的轮廓管线。输出 logits 不直接当置信概率；适用时 softmax/阈值及校准方式写 manifest。unknown 必须保留。取消在阶段边界检查，Worker 受内存预算管理。

## 数据集与评估

样本包含 reference、mask、species、bodyRegion、markingType、keypoints、来源授权与人工修正版本。按角色/作者分组划分训练/验证/测试，禁止同角色不同视图跨集合泄漏。锁定测试集后调参使用验证集。

候选 I8 门禁：至少200张独立授权双视图相关图片、各主类至少20个有效样本；macro IoU≥0.80，重点小类单独报告，边界 F1 在2px容差下≥0.85；前提是固定评估分辨率1024和类别表。指标为拟议目标，当前没有模型或数据集，不声称已达到。低置信与域外样本必须展示人工审核入口。

确定性在同模型/后端/构建下比较；跨 GPU 后端报告容差与标签差异，禁止用不同浮点结果自动覆盖已存路径。

## 授权与撤回

训练贡献需独立明确同意，记录授权范围/版本/撤回方式；启用遥测不代表同意训练。撤回影响后续采集与可识别待训练副本，已训练模型如何处理需在数据政策明确，不能承诺不存在的自动反训练能力。TC-026、TC-032 和数据审查覆盖。
''')

doc('15-license-system.md', '授权与能力管理设计', '§7、51～55、81、94、120', r'''
## 能力模型

User→Organization→Plan→Entitlement→FeatureGate。Feature 注册表包含 ID、引入版本、能力说明、依赖和离线策略。Renderer 的禁用按钮仅为体验，Main 在命令/结果接受/导出边界执行真实检查。Rust 不判断 vip，但独立 SDK 商业分发需另行设计授权边界。

基础离线能力固定为项目打开/保存、基础2D、基础参数身体、3D几何预览、传统花纹处理、基础UV、基础PDF/SVG；高级自动优化/排料/DXF/AI按令牌控制。原文套餐示例中 SVG/预览收费与离线原则冲突，采用前述基础离线下限，见 ADR-005，定价仍待商业负责人决策。

## 令牌格式与校验

签名载荷包含 licenseId、subject、organizationId?、features、issuedAt、notBefore、expiresAt、offlineUntil、deviceBinding?、keyId、tokenVersion、nonce。采用固定规范 JSON UTF-8 字节做 Ed25519 签名，签名与 payload 分离。明确拒绝未知 keyId/算法、重复 JSON key 和歧义数值；公钥内置或由受信链轮换，私钥仅签发服务持有。

校验顺序：结构→keyId→签名→notBefore/expiry/offlineUntil→绑定（若配置）→feature。签名数据不能依赖客户端重排不一致的普通 JSON。令牌放 OS 安全存储；日志只写脱敏 licenseId 摘要，不写 token。

## 状态机

Unactivated→ActiveOnline→ActiveOffline→Expired / Revoked。网络错误不是 revoked；有效离线期限内照常使用已授权能力。超过有效期限停止新高级操作，已存在数据可读可保存、基础输出继续。在线确认 revoke 后立即禁止新高级任务；已运行任务可以完成为候选，但接受/高级导出重新校验。

记录最后可信服务器时间与单调时钟检查明显时钟回拨；不能声称纯离线客户端完全防篡改。异常仅限制新高级操作并给出修复方法，不锁死项目。离线期限候选30天，具体套餐到 I9 冻结；企业完全离线签发流程需手工请求/响应或局域网服务，服务部署属 Future。

## 配额与故障

能力开关和配额分离。基础本地编辑不按计费次数扣减；涉及在线配额需幂等 reserve/commit/release，只有任务成功交付才提交消耗，重试不重复扣减。离线计费配额策略未定前不发布此类收费功能。

测试签名篡改、过期、未来签发、未知密钥、断网、回拨、撤销、重复激活、设备更换和 Renderer 绕过（TC-027～029）。
''')

doc('16-cloud-services.md', '商业服务与可选云端设计', '§55、80～82、94、111～113、120', r'''
## 发布范围

I9 必需：账号、授权签发/刷新/吊销、订阅状态、更新清单和模型清单服务。cloud-project、团队、SSO、企业私有服务是 Future，接口预留不代表实现。api.fpcad.com 是母文档示例域名，不声称已注册或可用。

## REST 约定

统一 /api/v1，JSON UTF-8，错误 {code,message,requestId,retryable}，写入接口支持 Idempotency-Key。401 身份无效、403 无能力、409 冲突、422 参数错误、429 限流带 Retry-After、5xx 服务故障。重试限幂等操作，指数退避且有上限；客户端不得因商业服务失败阻断本地工程打开。

|接口|请求关键字段|响应关键字段|鉴权/行为|
|---|---|---|---|
|POST /auth/session|外部认证授权码+PKCE verifier|session/access expiry|采用成熟身份提供方，首版不自造密码算法|
|POST /license/activate|activationCode,devicePublicId,clientVersion|signedToken,serverTime|授权码交换；幂等|
|POST /license/refresh|licenseId,currentTokenDigest|signedToken,serverTime|有效会话；不得上传项目|
|POST /license/revoke|licenseId,reason|revokedAt|本人或组织管理员；审计|
|GET /license/me|无|licenseSummary|用户会话|
|GET /features|clientVersion|catalogVersion,features|公开目录不等于实际授权|
|GET /updates|platform,arch,channel,version|signedManifest|按平台签名与渐进发布|
|GET /models|runtime,platform|compatibleManifests|仅元数据；下载再校验|
|POST /billing/webhook|供应商签名事件|receiptId|验证签名/时间窗/eventId去重|

账号登出删除会话凭据，不删除项目。计费成功只能经服务端可信支付事件更新授权，不能相信客户端“支付成功”字段。真实支付供应商与税务流程为商业待决，不填入假接口密钥。

## 服务数据与运维

accounts、organizations、memberships、plans、subscriptions、licenses、activation_devices、revocations、webhook_events、audit_events 为服务端领域。支付卡数据由支付供应商处理，产品只存必要供应商引用。授权签名私钥使用受控密钥服务，管理员操作留审计且日志不存原 token。

候选服务目标：月可用性99.5%、授权响应p95≤2s、备份RPO≤24h/RTO≤4h；I9 压测与恢复演练后才能承诺。离线令牌缓解短时故障，不代替服务器备份。监控签发失败率、更新失败率、队列延迟及 webhook 重复率。

## 兼容和未来同步

客户端声明能力和 protocol/API 范围，至少覆盖最近两个服务端 minor；不得仅比较版本字符串就忽略字段兼容。新增字段向后兼容、删改字段升 major；弃用提前两个 minor 通告。

Future 云项目上传必须用户明确开启并展示资源范围。使用 revision/ETag 冲突检测和分支副本，禁止最后写入静默覆盖；离线更改不自动合并几何。私有部署可考虑 Docker Compose，但依赖与备份由独立版本设计和评审后纳入范围。
''')

doc('17-plugin-sdk.md', '模块注册与插件扩展契约', '§7、56、57、97', r'''
## 分阶段边界

1.0 交付可信内置模块注册，不开放任意第三方可执行插件安装。公共 SDK 和插件商店为 Future。母文档要求的模块化从 I0 建立，第三方沙箱不能仅依靠 TypeScript 类型或约定实现。

FeatureModule={id,version,capabilities,initialize(ctx),dispose()}。依赖由 dependsOn 显式声明，启动拓扑排序，循环依赖拒绝；一个可选模块失败不得使 project/basic CAD 不可用。dispose 必须释放订阅、worker和临时资源。

## 插件清单和权限设计

候选 PluginManifest={id,version,minAppVersion,maxApiMajor,capabilities,permissions,entry,sha256,signature,license}。permissions 区分 project.read、project.command、file.userSelected、network.allowlist；默认无权限。声明权限不等于自动授予，宿主负责授权和命令校验。

第三方插件未来放隔离进程，不可读取主进程内存、账号 token 或任意文件系统。插件不存在访问客户端 License 私钥的合理需求，因为客户端根本不保存签发私钥。宿主提供不可变快照和受控 Command API，不给数据库连接。

## 版本和失败

能力发现替代硬编码版本分支；不兼容 API major 拒绝加载。超时/崩溃终止插件进程，回滚未提交事务，保存项目不受影响。插件卸载只移除程序；其命名空间元数据按未知扩展保存，不能删除用户纸样。

## 扩展验收

I0 验证内置模块注册、顺序、重复 ID、循环依赖、失败隔离。Future SDK 必须额外通过越权文件/网络访问、恶意消息、CPU/内存耗尽和版本迁移测试；未通过不开放第三方插件。TC-033 和 TC-047 跟踪。
''')

doc('18-testing.md', '测试策略、质量门禁与性能验收', '§34、68～70、74～79、95、96、105～108、119、128', r'''
## 测试原则与层级

Rust 单元/性质/模糊测试验证数值与不变量；协议契约测试验证 TS/Rust 和跨进程边界；SQLite/项目包集成测试验证事务和恢复；Vitest 验证工具状态机；Playwright 验证完整用户流程；独立解析器和实际打印/缝制验证制造输出。截图回归只能检查展示，不证明毫米精度。

测试设计详见 30，黄金数据集详见 31。所有执行需记录环境、构建 hash、fixture hash、命令、实测值、期望、日志和附件；当前状态均为未执行。人工纸样参考不是无误差真理，需记录测量方法和工艺师意见。

## 通用进入/退出条件

进入：增量需求与契约已评审、依赖稳定、fixture 有来源授权与 hash、环境可复现。退出：该增量所有 Must 需求至少一条可复查测试证据；全部 P0/P1 用例通过；无未关闭 S0/S1 缺陷；新增与受影响模块回归通过；备份/恢复和制造核心检查通过。S2 仅允许记录影响、绕行、责任人与到期日的风险接受；不得豁免自交、错误比例、数据丢失等硬门禁。

缺陷等级：S0 数据损毁/密钥泄漏/错误制造文件被标合格；S1 核心闭环不可完成或安全边界突破；S2 非核心功能失效有绕行；S3 展示/文案问题。测试优先级与缺陷严重度分别登记。

## 数值验收

|指标|Alpha I5|MVP/Beta I6|Commercial I9|
|---|---|---|---|
|制造几何|闭合、无自交/退化、有效 cutLine|相同，所有核心部位回归|全部支持样本必须通过|
|无吃量缝长残差|报告数值，不隐瞒超限；制造 profile 仍执行|<2mm|典型锁定样本≤1mm|
|数字导出比例|≤0.1%（I1 即开始）|≤0.1%|≤0.1%|
|展开质量|09 的候选 profile；超限人工审核|通过锁定材料样本 profile|制造顾问签收 profile 与样衣证据|
|确定性|同构建/后端规范哈希一致|同上，跨平台几何比较|全平台回归无非预期变化|

跨平台几何坐标/曲长差≤0.001mm，拓扑 ID/片数一致，质量等级不能因误差越过硬门禁；边界结果需保守判定。AI 后端另按模型报告，不纳入几何逐位相等要求。比例误差=|输出测得长度/设计长度-1|，用100mm、500mm、1000mm校准对象检验；尺寸读取需使用独立解析器。

## 性能基准（均为待实测目标）

B-MIN：4核CPU、8GB RAM、SSD、集成GPU；B-REF：8核CPU、16GB RAM、SSD、8GB显存。执行前登记精确CPU/GPU/驱动/OS/显示缩放/电源模式和构建类型，不能仅写“普通电脑”。平台具体版本在 I0 兼容矩阵冻结。

|场景|数据规格|B-REF目标|B-MIN退化目标|
|---|---|---|---|
|2D拖动到下一显示帧|100片、每片100段|p95≤50ms|p95≤100ms|
|3D交互|20万三角形、2048纹理|中位≥30FPS|降LOD后≥20FPS|
|打开项目|100片、20万面、2张4096图、包≤200MB|冷启动后打开≤5s|≤10s，先proxy|
|基础拆板|5万三角形躯干|max60s|可降精度，max120s|
|排料|100个实例，固定preset|max60s|最多120s并提供进度|
|取消反馈|任一长任务|UI≤200ms，计算安全退出≤2s|同左；不响应可终止隔离进程|
|稳定内存|反复开关项目20次|释放后无单调增长，末次≤首稳态+10%|峰值RSS≤4GB目标|

性能每项冷运行1次、预热3次、测量20次；报告p50/p95/max与峰值内存。CI不具备真实硬件时只做回归趋势，不伪造性能通过。不得为了性能绕过几何检查。

## 可靠性、安全与兼容

注入事务前/中/后、ZIP写入/替换、资源写入、迁移中断、磁盘满和Worker崩溃；结果只能是旧完整状态或新完整状态，不能混合。恢复点只恢复已提交命令，最后未提交手势允许丢失但必须明确。

安全测试涵盖任意IPC、路径穿越、ZIP炸弹、脚本SVG、token篡改、更新降级、插件越权和隐私默认值。离线测试用禁网环境，不只模拟一个HTTP错误。Windows/macOS/Linux分别执行基础闭环、安装更新与Unicode路径测试。

## 持续集成门禁

每PR：格式/静态检查、Rust单元、TS类型、契约、受影响集成、关键golden。合并主干：完整golden、项目迁移/恢复、核心E2E。候选发布：平台安装/更新、独立导出解析、安全/依赖扫描、性能与人工制造验证。Rust建议cargo fmt/check/clippy/test；前端使用锁定包管理器的typecheck/test/e2e脚本；具体可执行命令在I0建好后写入27，当前不能声称已运行。

覆盖率作为诊断而非唯一放行条件；不得写仅重述实现的断言。每次缺陷修复增加可复现失败样本，黄金结果更新必须附数值差异与独立复核，禁止一键接受全部新快照。
''')

doc('19-security.md', '安全、隐私与威胁模型', '§6、53～56、59、82、84、85、104、109', r'''
## 资产与边界

保护用户兽设/身体测量/纸样、项目完整性、授权凭据、更新信任链和签发密钥。边界为不可信导入文件→解析器、Renderer→Main、Main→Worker、客户端→云、插件→宿主。项目内容不是可执行指令；SVG、模板和模型元数据不得驱动shell或动态代码。

|威胁|入口|控制|验证|
|---|---|---|---|
|Renderer执行恶意脚本后读文件|参考图/SVG/HTML|contextIsolation，关闭nodeIntegration，启用可用沙箱，限制CSP与导航|TC-031|
|伪造IPC越权导出/高级计算|preload|白名单、sender frame校验、schema、Main权限、handle|TC-006/028|
|ZIP目录穿越/炸弹|.fpcad|规范化路径、拒绝链接/重复路径、流式字节预算|TC-003/031|
|解析器崩溃/内存耗尽|图片/模型/几何|隔离进程、大小/数量上限、超时、模糊测试|TC-031/035|
|项目静默破坏|保存/迁移/恢复|事务、hash、临时文件原子替换、备份|TC-002/003/004|
|盗用或伪造授权|token/时钟|签名、keyId、期限、可信时间；基础数据保留|TC-027/029|
|恶意更新/回退旧漏洞版|更新服务|签名清单、hash、平台签名、最低安全版本|TC-030|
|客户图片泄漏|日志/遥测/云|默认关闭、脱敏、范围预览、独立同意|TC-032|

## 文件与进程限额（补充候选）

项目包默认≤2GiB、展开总量≤8GiB、单资源≤512MiB、条目≤100000；单图解码≤64MP；IPC JSON≤8MiB；压缩比异常>200触发拒绝/人工受控导入。先累计真实解压字节，不能只相信ZIP头。路径限制包括Windows盘符/UNC、保留名、大小写碰撞和NUL；目标路径必须保持在提取根目录内。

超限返回清晰错误，不静默截断。大型合法项目未来可增加受控配置，修改限额需性能与安全复测。SVG导入只支持白名单几何实体，去除script、事件处理器、foreignObject、外链引用；远程资源默认禁止。

## 密钥、依赖与隐私

客户端只持授权/更新公钥；私钥不得进入仓库、包或示例配置。系统安全存储保存会话凭据，服务端密钥定期轮换并保留受控撤销流程。日志使用requestId/jobId和脱敏错误，不写完整用户路径、图片、测量和token；用户提交诊断包前可预览内容。

遥测、崩溃上报、云同步、云AI、训练贡献分别开关，默认关闭。撤回后停止后续采集并清理未发送队列；服务端删除/保留期限需隐私政策登记。离线核心不发隐蔽网络请求。依赖安全和许可检查见21；此文是工程控制设计，不是法律合规认证。

## 安全事件处理

发现疑似密钥泄漏：暂停签发/受影响发布→隔离证据→轮换/撤销→评估已发令牌与更新包→修复并安全复验→按确认影响通知相关用户。禁止为收集证据上传全部客户项目。漏洞严重度、影响版本、缓解方案和修复证据写入缺陷记录，由安全/发布角色签收。
''')

doc('20-release.md', '构建、发布、更新与维护计划', '§4、74、82～85、94、96、114、119、120、125', r'''
## 版本和渠道

应用采用 SemVer；formatVersion、schemaVersion、protocolVersion、algorithmVersion 和 modelVersion 分开管理。算法输出改变即需算法版本变化，不因UI补丁号掩盖变化。Stable/Beta/Nightly 分渠道，Nightly仅内部，用户切渠道需明确选择。

I0 冻结构建工具链与锁文件，I1起产出可运行内部包，I5 Alpha、I6 MVP/Beta、I9商业候选。Windows/macOS/Linux各自拥有发布清单，某平台未通过不把其他平台成功当作其验证。

## 可重复构建输入

源提交、依赖锁、Rust toolchain、Node/包管理器版本、平台SDK、模板/模型hash、环境配置和构建命令必须归档。打包用electron-builder路线，具体签名/公证流程按选定平台官方要求核验后写操作手册；当前没有证书或流水线，不声称能直接发行。

## 候选发布检查单

1. 需求追踪无缺口，增量验收已签收；零开放S0/S1。
2. 全套关键golden、迁移、恢复、离线和导出比例通过。
3. 平台安装、启动、卸载、更新、Unicode路径、低权限用户测试通过；卸载默认保留用户项目。
4. SBOM、NOTICE、模型/模板授权、依赖漏洞和法律待决项完成发行审查。
5. 安装包/更新manifest签名、hash、公钥轮换、版本最小安全线验证。
6. 发布说明包含新增、已知限制、格式迁移、备份建议和回退边界；保留上一稳定包。
7. 实际工艺试做、数字输出、性能和隐私证据齐全；支持与事故响应值班角色就绪。

## 更新事务和回滚

下载签名manifest→验证keyId/签名/平台/渠道/版本策略→下载临时包→hash和平台签名检查→提示保存工作→关闭应用→安装→健康检查。任何校验失败停止并保留当前可运行版本。不能静默关闭未保存工程。

候选灰度5%→25%→100%，每阶段观察24h；失败率>2%或出现S0立即暂停（阈值在I9验证）。用户拒绝遥测不影响更新，只能依赖自愿报告与下载/服务指标。

应用回滚与项目格式回滚不同。迁移前保留旧格式备份；新版本已保存的不兼容项目不强制旧版本写入，需用备份或受支持转换。安全最低版本限制可能禁止自动降级，紧急修复走前向更新。

## 维护与支持

每个缺陷先复现和保存脱敏样本，修复同时更新用例与追踪。服务/模型升级独立兼容检查，已接受几何不自动重算。用户可导出本地诊断包（版本、构建、OS/GPU、日志、匿名性能，项目内容可选且默认不含）。备份恢复演练每个重大版本至少一次。

维护期、EOL与支持的OS版本为商业待决，不臆造年限。发布负责人在I9前填入25的支持矩阵。用户操作说明见28，验收模板见24。
''')

doc('21-open-source-notices.md', '第三方依赖、许可与软件物料清单管理', '§2、3、4、46、56、123、126、128', r'''
## 当前状态

本文件是依赖审查计划，不是已完成法律意见或真实发行NOTICE。没有安装/锁定软件依赖，因此精确版本、传递依赖和实际链接方式均未核验。母文档列举的许可证名称只作为待核验线索；发行结论必须基于实际制品、版本和文件。原文会话引用标记不能替代许可证正文。

## 候选依赖登记

|依赖|用途|母文档许可线索（未核验）|版本/处置|
|---|---|---|---|
|Electron|桌面运行时|MIT及所带组件义务|I0锁定并全量扫描|
|Vue/TypeScript/Vite/Pinia/Tailwind|前端|未在母文档逐项核验|I0查实际LICENSE和传递依赖|
|Three.js|3D|MIT|I2锁定|
|ONNX Runtime|本地推理|MIT|I8检查后端及模型独立许可|
|Clipper2|Boolean/Offset候选|Boost 1.0|I1检查Rust桥接/静态链接产物|
|Earcut|三角剖分候选|ISC|I1～I3检查实际移植版|
|meshoptimizer|网格优化|MIT|按实际启用版本审查|
|SQLite/rusqlite或sqlx|本地数据|未逐项核验|I0选择唯一仓储路线及传递依赖|
|image/OpenCV|图像处理|未逐项核验|I4只引入实际需要组件|
|LSCM/ARAP求解器|展开|实现库未选择|I5前阻断项，代码来源需审查|
|libigl/CGAL|研究或候选几何|组件级混合授权线索|未获具体批准不进入发行|
|Seamly2D/Valentina/Blender|研究比较|GPL线索|不复制其代码进入闭源核心|
|字体、物种网格、纹理、模型权重|制品资源|各自许可，不能沿用引擎许可|每项记录来源与分发授权|

## 管理流程

引入前登记名称、精确版本/commit、下载来源、hash、用途、链接/调用方式、许可证文件路径、修改文件、传递组件、NOTICE/源码提供义务与审查人。生成SPDX或CycloneDX SBOM，与最终安装包中的实际文件比对，不能只扫描package.json。

研发目标遵循母文档闭源商业核心方向；强copyleft或不明确条款交给专业审查。独立进程隔离不自动消除许可证义务，宽松许可也不代表无需声明或不存在专利风险。FTO为专业人员任务，不由本文宣称完成。

## 发行门禁与证据

每项许可状态须为approved/removed/commercially-licensed之一，pending阻断受影响制品发行。NOTICE生成基于锁定清单，不填“版权所有归原作者”代替具体要求。扫描报告、许可证文本副本、商业授权凭证引用和修改源码义务履行证据随版本归档。

sources保留原文参考链接，后续核验应读取对应版本官方仓库LICENSE；本文没有访问或验证这些站点，不以链接存在声称事实已确认。依赖记录模板见templates/依赖审查记录.md，TC-041验证制品闭环。
''')

doc('22-增量开发计划与工作分解.md', '增量模型、工作分解与里程碑', '§86～103、117、124、125', r'''
## 模型与执行节奏

采用增量模型，每次增加可运行用户能力并在已有版本上回归；不是先写全部需求、再一次性开发和测试。每个增量执行：确定需求和验收样本→风险原型→设计/契约评审→实现→单元/集成/端到端验证→制造/用户评审→内部发布→回收反馈建立CR。

为保留母文档Phase 0～9对应关系，命名I0～I9。母文档§124的算法依赖顺序作为技术依赖，§86～94作为交付顺序；I1早期输出是核心精度验证，I3采用预制patch验证关联，I5再交付通用拆板，不宣称提前解决所有算法。

## 工作包与验收

|增量|前置|可交付工作包|出口与演示|工期区间（补充估算）|
|---|---|---|---|---|
|I0 工程与可靠项目|本套基线评审|工程骨架、基础schema、IPC、Rust进程、工作库、文件包、命令/恢复、模块注册|创建→编辑测试实体→撤销→保存→强制退出→恢复；TC001～004/006/033|3～4周|
|I1 2D几何与基础制造|I0|点线Bezier/path、Boolean/Offset、工具、标注、检查器、PDF/SVG/PNG|100×200mm纸样→10mm缝份→导出100mm校准尺|5～7周|
|I2 身体与材料|I1|犬猫模板、测量/Morph、植腿/趾行、尾爪参数、padding、材料|1800mm犬科调整胸围→实测残差与失效传播|4～6周|
|I3 关联与缝线|I2|HalfEdge/patch、稳定ID、seam graph、拾取、预制展开overlay|点击3D片↔2D片；修改缝线检查残差|3～5周|
|I4 参考与传统识别|I3|Front/Back标定、传统分割、mask/path人工修正、资源管理|双视图→可编辑毫米花纹；侧面unknown|3～4周|
|I5 自动拆板Alpha|I3/I4|分区、候选seam、LSCM/ARAP、评分、重切、缓存|犬科躯干3～6片→缝份→SVG→3D Overlay|6～10周|
|I6 花纹制造MVP/Beta|I5|投影/逆映射、切割路径、连续性、完整引导|§95闭环完整；缝残差<2mm；用户试用|4～6周|
|I7 排料与制造扩展|I6|毛向排料、DXF、大PDF、趾行腿/Paw制造验证、其他物种模板、高级padding|完整裁剪数量、无重叠、方向合法、独立DXF回读|4～6周|
|I8 本地AI辅助|I7|模型清单/下载、分割/分类/关键点、评估数据治理|本地候选→手工修正→CPU退化、无自动上传|4～8周|
|I9 商业1.0|I8|账号/授权/订阅、离线令牌、签名更新、审计/诊断、全平台收敛|1.0范围全通过，≤1mm典型缝残差、许可/平台发行门禁|4～6周|

估算合计40～62周，假设稳定的前端、Rust几何、测试角色并有工艺顾问和发布支持；不承诺固定日期，不包含未知模型采购/法务/证书等待。I5风险高，原型失败需重新估算；团队规模、人员和预算由25登记。每增量内部可以1～2周小步演示，但不能把半成品当作该增量验收。

## 垂直闭环与范围控制

V1在I5：一个1800mm犬科、躯干3～6片、2D展开、缝份、SVG、3D Overlay；黄色花纹节点修改回映在I6完成。V2/V3在I7：趾行腿与Paw工艺样本。MVP明确是I6，不能以I1编辑器或I5拆板原型替代。

1.0包含母文档列出的主功能；完整物理模拟、多视图AI重建、云协作、模板市场、第三方SDK、机器控制和企业私有服务属于后续增量F1+，独立立项，不计入当前预算。I9的企业离线授权令牌支持与完整企业服务器部署分开。

## 任务拆分规范

工作项格式 WI-Ix-序号，必须包含 REQ、设计章节、输入输出契约、前置工作项、实现路径、验收TC、数据迁移/安全/许可影响、估算和负责人。单项宜1～3开发日，探索类SPIKE最长5日并交实验报告；无法收敛则上报风险，不连续滚动“快好了”。

增量容量先预留20%给回归、修复与评审（候选规划值）。完成比例按验收通过需求统计，不按文件数、代码行或“开发完成”口述。

## 每个增量的固定产物

可运行包/构建hash、更新后的需求与追踪、API/schema变化、迁移报告、测试与性能报告、缺陷清单、制造样本（适用时）、用户评审、依赖SBOM增量、发布说明、下一增量反馈。入口/出口评审模板见24；剩余风险必须有归属，不能靠“后续优化”隐去。
''')

doc('23-需求追踪矩阵.md', '需求、设计、测试与增量追踪矩阵', '全文', r'''
## 使用规则

下表与 traceability.csv 同源生成，每项REQ关联主要设计、最早交付增量和至少一条验收测试。量化目标以18/30为准。实现位置和证据当前未建立，明确写“未实现/未执行”；开发后填写真实路径、commit与测试报告，不能用设计文件替代实现证据。

增量后续仍需回归早期需求：本表增量为首次达到需求的时间，不代表此后免测。未来范围标F1+。修改编号关系须同步SRS、TC、CR与受影响设计。
''')

doc('24-评审验收与质量保证计划.md', '评审、验证确认与质量保证计划', '§75～79、95、96、125、128', r'''
## 评审类型

|评审|参加角色|必须检查|产出|
|---|---|---|---|
|需求评审|产品、测试、技术、工艺|范围、可测试性、术语、冲突与增量归属|基线或修改项|
|架构/接口评审|技术、前后端、测试、安全|真值归属、进程边界、兼容、恢复、错误契约|ADR与接口冻结|
|算法评审|几何、测试、工艺|数学定义、前提、退化情况、误差与数据集|实验复核结论|
|代码审查|非作者开发、相关责任人|REQ实现、失败路径、事务、数值、安全、迁移|PR意见与修复证据|
|测试就绪评审|测试、开发|fixture授权、环境、oracle、预期和覆盖|允许执行/补件|
|增量验收|产品、测试、技术、工艺|工作流、量化结果、回归、缺陷、剩余风险|接受/有条件接受/拒绝|
|商业发行评审|发布、安全、商业、工艺|签名、许可、数据政策、支持、全平台证据|发行决定|

作者不得独自批准自己的高风险算法/安全/迁移变更。小团队可兼任角色，但必须至少一次独立复核；无独立审查人员时记录缺口并不声称审查已完成。

## Definition of Ready

需求有编号、范围与验收；输入/输出和错误明确；依赖增量可用；设计关键待决已关闭或有不影响安全的限定方案；测试数据可用；任务大小可交付；第三方引入已登记。未决算法可先做隔离SPIKE，不直接合入生产路径。

## Definition of Done

代码和文档关联同一REQ；边界/错误路径测试通过；几何golden无未解释差异；IPC/schema兼容；失败不丢数据；日志脱敏；新增依赖审查；性能达到所属增量门禁；PR独立审查关闭；提供演示与可复查证据。仅编译通过或页面能打开不算完成。

## 验收记录

使用templates/增量验收记录.md，逐项写计划值/实测值/证据链接/结论。验收时间、构建和fixture hash必须固定。通过证据应包含最小复现项目和独立数值报告；对UI体验用录屏/截图辅助，对制造结果需回读和工艺试做。

MVP须独立非开发用户按28走完双视图到PDF/SVG，记录耗时、失败步骤和误操作；候选目标：5位有基础制作经验的试用者中至少4位无需开发人员接管完成。此为新增可用性目标，样本和结果当前未产生。

## 不合格品与豁免

失败建立缺陷并附fixture，不直接修改黄金文件适应错误。S0/S1、制造比例/自交/数据损坏/安全关键错误不可豁免。可接受低级缺陷需给责任人、到期增量、用户影响和回归计划；逾期自动进入下次评审阻断项。

评审状态：待评审→有修改意见→复核→通过/拒绝；“已提交评审”不等于“已批准”。所有待决项在26和25中有截止门禁。
''')

doc('25-项目管理风险与配置管理.md', '项目管理、风险、配置与变更控制', '§3、57、74、86～108、125、128', r'''
## 角色与责任

|工作|最终负责A|执行R|咨询C|
|---|---|---|---|
|需求范围/增量验收|产品负责人|产品/测试|技术、工艺|
|架构与数据契约|技术负责人|对应开发|测试、安全|
|几何/制造算法|技术负责人|Rust几何开发|工艺、测试|
|质量放行|测试负责人|测试团队|技术、产品|
|签名发行/回滚|发布负责人|构建运维|安全、测试|
|授权、许可和定价|商业负责人|商业/专业审查人员|技术、产品|

具体姓名、投入工时、开始日、预算、设备和签名凭据尚未提供；I0计划评审前填写，不能据此文虚构已承诺排期。发生角色兼任须记录独立复核人。

## 风险登记

|ID|风险/概率×影响|触发信号|缓解与回退|责任/截止|
|---|---|---|---|---|
|RISK-001|通用拆板不满足制造，高×高|I5躯干超阈或片数失控|解析样本→手工seam→启发式原型；限定模板而非宣称通用|几何/I5入口|
|RISK-002|2D/3D拓扑关联失真，高×高|模板改动后ID漂移|topologyVersion、remap、stale、拒绝旧结果|技术/I3|
|RISK-003|双视图侧面信息不足，高×中|遮挡/unknown过多|人工补齐，保留不确定性，不臆造确定几何|产品/I4|
|RISK-004|保存/迁移损坏，中×高|故障注入出现混合版本|原子写、备份、事务、恢复演练|技术/I0起持续|
|RISK-005|库/网格/模型许可不可发行，中×高|来源或条款不明确|替换或取得授权，pending制品不发布|商业/I1引入前、I9|
|RISK-006|低配机器卡死，中×高|RSS/帧延迟超预算|worker限额、LOD、proxy、CPU/传统降级|技术/I2起|
|RISK-007|AI数据不足/泛化差，高×中|各物种IoU差异大|传统流程优先，独立测试集，限制支持域|AI/I8|
|RISK-008|跨平台几何差异，中×高|golden拓扑/等级变化|固定归约/后端、容差门禁、保守判定|测试/I5|
|RISK-009|订阅故障锁死客户项目，中×高|断网无法保存|基础离线能力下限、已有数据保留|商业/I9|
|RISK-010|更新供应链攻击，低×高|签名异常/密钥泄漏|双重校验、轮换、暂停渠道、前向修复|安全/I9|
|RISK-011|工艺参数没有真实样本，高×高|数字合格却无法缝制|材料测试片、工艺师和样衣验证|工艺/I6～I9|
|RISK-012|范围扩张/人力不足，高×高|连续两轮工作包溢出|冻结增量、CR评估、调整后续排期|产品/每增量|

风险每周更新概率、触发状态、行动与证据。缓解措施未执行时不标“已解决”。

## 配置项与基线

纳管：需求/设计/ADR、源代码、schema/API、工具链锁、算法preset、模板、模型、fixture、golden、SBOM、构建脚本、发布清单。文档使用版本控制；大制品用内容hash+制品存储，不能仅依赖可变下载URL。

基线编号 BL-Ix-日期，含源commit、需求集、接口/数据版本、fixture hash、算法/模型版本与签收人。分支建议main可发布、短期feature分支，任何迁移/安全/算法变更必须PR；不规定未知托管服务。

## 变更控制

CR提出→影响分析（需求、接口、数据迁移、算法、测试、许可、性能、排期）→产品/技术/测试决策→更新设计/追踪→实现→回归→关闭。紧急修复允许先隔离故障，再补完整记录，不能跳过发行安全门禁。降低验收值属于需求变更，必须附实验和用户影响，不能仅因测试失败降低。

## 待补启动资源

I0：角色姓名/容量、OS具体支持版本、CPU/内存测试机、Node/Rust/包管理器版本、CI平台、基准模板来源。I5：求解器与golden来源。I8：模型/数据授权。I9：定价/离线期限、签名证书、服务地址、隐私保留期限、维护/EOL、支付供应商。每项责任见26，未定不伪造事实。
''')

doc('26-架构决策与待决事项.md', '冲突处理、架构决策与待决事项', '§6、9、42、50～56、86～103、120、124', r'''
## 决策状态

以下为本套文档采用的“拟议并用于细化”的工程决策，尚未经过项目团队签字批准。可据此建立任务和原型；相关增量入口需审查。修改时保留旧决策与替代原因。

|ID|问题和原文冲突|采用的处理|后果/验证|
|---|---|---|---|
|ADR-001|§99“AI辅助，不可逆”与§0/107可回滚冲突|解释为AI不得不可逆覆盖；候选+接受命令|撤销/候选测试TC018/026|
|ADR-002|§6Main SQLite、§4Rust驱动与§9ZIP并存|Main仓储单写，SQLite工作库；ZIP交换快照；Rust算几何|单事务真值和故障测试TC001～004|
|ADR-003|§22要求2D修改同步3D，任意逆变形无算法保证|花纹域内逆映射；纸样自由形变标映射stale后重建|不把预览同步等同物理求解TC014/020|
|ADR-004|Native/WASM与长计算隔离方式未定|首版Rust隔离进程+版本消息；不同时承诺全部宿主|增加序列化成本，换取崩溃隔离TC006/035|
|ADR-005|§51示例付费SVG/预览与§120离线核心冲突|基础SVG/预览和核心CAD离线下限，高级能力计费|商业定价需遵守此下限TC027～029|
|ADR-006|§86～94阶段顺序与§124绝对顺序冲突|阶段为增量交付，§124为依赖；早期导出验证数值，I3用预制patch|MVP在I6；I5才称自动拆板|
|ADR-007|§96 1.0与§97/111企业未来范围混杂|商业基础I9；完整企业服务/协作/SDK/物理F1+|范围变化走CR，不省略记录|
|ADR-008|§10可0.001mm序列化与长期精度|持久化f64往返，UI0.1mm；输出离散预算单独控制|避免累计量化误差TC005/023|
|ADR-009|“同版本确定性”未定义平台|同构建后端规范hash；跨平台数值容差+拓扑一致|建立可实现验收TC037|
|ADR-010|毛厚/填充与制造面语义未定义|分离视觉毛长与材料有效补偿，profile记录工艺来源|待实际材料验证TC024|

## 待决事项与门禁

|ID|待决问题|当前可执行默认/可继续范围|决定者/最晚时间|
|---|---|---|---|
|OPEN-001|团队规模、预算和发布日期|22采用区间估算，先做I0任务拆分|产品/I0计划评审|
|OPEN-002|具体OS/架构和依赖版本|目标三平台，候选x64/arm64按实测支持|技术+测试/I0出口|
|OPEN-003|SQLite JS驱动与Rust桥接细节|单写Main仓储；可用实验选择驱动，不能双写|技术/I0设计冻结|
|OPEN-004|LSCM/ARAP实现、许可和求解性能|先解析shape与独立SPIKE|几何+许可审查/I5入口|
|OPEN-005|材料失真、最小片宽和吃量规则|使用文内候选profile做实验，禁止称商业已合格|工艺+测试/I6与I9放行前|
|OPEN-006|其他物种模板资源和参数范围|I2犬猫，I7逐模板扩大|产品+工艺/I7入口|
|OPEN-007|AI模型、类别和训练数据|传统视觉可先完成；不虚构模型指标|AI+数据负责人/I8入口|
|OPEN-008|套餐/配额/离线期限|基础离线下限；高级期限候选30天|商业+产品/I9入口|
|OPEN-009|证书、服务域名、支付/身份供应商|接口与mock可开发，不能生产签发/收费|商业+发布/I9发行前|
|OPEN-010|隐私保留/删除策略和EOL|默认不采集；诊断本地，尚不承诺服务期限|商业+安全/I9发行前|

未决不影响无依赖工作；达到相应门禁仍未决定则该工作包不准验收。不能把本表待决项误称已实施的配置。
''')

doc('27-开发规范与任务执行手册.md', '开发规范与任务执行手册', '§0、57～60、74、105～108、125', r'''
## 建议仓库布局

```text
apps/desktop/                 Electron + Vue
packages/schema/              领域序列化模式与生成类型
packages/protocol/            IPC请求/响应与校验
packages/command/             命令定义与逆补丁
packages/ui/                  通用交互组件
packages/feature-gates/       能力目录
crates/geometry-core/         几何原语
crates/path-engine/           路径运算
crates/mesh-core/             网格拓扑
crates/pattern-engine/        制造实体
crates/unwrap-engine/         拆板
crates/nesting-engine/        排料
crates/export-engine/         导出
crates/worker/                隔离进程入口
tests/fixtures/ tests/golden/ tests/integration/
models/ templates/ scripts/
Docs/软件工程文档/              本工程基线
```

这是计划布局，当前未创建应用工程。母文档的ffi目录可在需要Native桥接时增加，不为结构完整而加入未使用代码。接口生成以schema单源，禁止手工维护两套漂移TS/Rust字段。

## 任务领取与实现顺序

读取00、22、23和所属模块→确认REQ/TC/增量依赖→检查26待决门禁→写工作项验收→先建立失败样本/接口样例→实现最小闭环→错误/恢复路径→测试→更新追踪与PR。遇母文档冲突引用ADR，不自行隐藏地改范围。不得把测试替身、预制曲面或假AI当生产算法交付。

## 编码约束

TypeScript启用strict，禁止any跨IPC边界，输入用运行时schema校验；错误采用稳定code/messageKey。Rust禁止正常错误路径panic，FFI不得传播panic，unsafe需局部理由和边界测试。每个长循环可取消，资源预算可观测。计算结果不得自动写入项目文件。

英文稳定key、中文/英文文案分离；长度变量使用Mm后缀或单位类型，角度使用Rad，显示Deg只在UI适配器。异步写入带expectedRevision；时间和随机源显式传入可重现逻辑。

## 本地/CI命令的落地要求

I0创建根README和bootstrap/check/test/build脚本，锁定包管理器与Rust toolchain。候选Rust命令：cargo fmt --check、cargo clippy --all-targets -- -D warnings、cargo test --workspace。前端定义typecheck、test、test:e2e、build脚本并在锁定安装后执行。此处为待落地规范，仓库目前没有这些可执行工程脚本，不能复制一条命令就声称验证成功。

Golden生成与验证分命令；更新golden必须指定案例并输出diff，禁止默认覆盖全部。外部包/模型下载需hash和来源登记。开发日志不可包含用户兽设；测试只用已授权或合成数据。

## PR要求

说明解决的REQ、具体触发与行为、接口/数据/算法版本影响、执行测试和未覆盖风险。大任务按可审查增量拆分，迁移与调用方兼容顺序写明。评审关注数值边界、事务一致、异步陈旧结果、失效图、安全权限与制造检查，格式细节交自动工具。

不得把未来工作标Done；若某条TC因缺环境无法执行，写blocked/未执行及原因，附可运行命令，保留门禁。
''')

doc('28-用户操作与故障恢复手册.md', '用户操作、制作检查与故障恢复手册', '§14、17、37、48、61、64～71、83、95、98、118、120', r'''
## 手册状态

本手册描述计划实现的用户流程，当前没有可操作软件截图。按钮名称为设计名称，开发完成后需由测试按实际界面校订并记录版本；不能把本手册当现有产品使用证明。

## 第一次完整制作

1. 新建项目，输入名称，确认单位毫米。导入Front与Back参考图，确认方向和图像旋转。
2. 在每张图上选已知长度两点并输入毫米值；确认100mm辅助标尺与角色高度合理。不要以整张画布高度代替人物高度。
3. 选物种模板，设置身高和围度，检查约束与残差。设置泡棉、内衬和有效材料补偿；毛发外观不等于裁剪增加量。
4. 识别颜色/花纹，逐一检查unknown、侧面与遮挡；用画笔或节点修正。自动补齐为候选，确认后再用于制造。
5. 生成缝线/纸样，查看片数、失真热图和缝长。锁定工艺要求的缝线，必要时手工切分重算。
6. 编辑2D路径与缝份，指定材料、毛向、裁剪数量、镜像和剪口。点击3D花纹定位2D路径并复核跨缝连续性。
7. 运行制造检查。逐项修复Error，对Warning确认工艺影响；预览贴合不证明布料实际效果。
8. 排料（相应版本提供）并检查所有实例、毛向和材料。保存项目后导出PDF/SVG或DXF。
9. 打印选择实际大小/100%，禁用适合页面。先测100mm校准尺，再拼接和裁剪；打印误差超出工艺要求时先校准设备。

## 日常操作

V选择、M移动、R旋转、S缩放、B曲线、P路径、O缝份偏移、N剪口、D尺寸、G毛向；Ctrl/Cmd+S保存、Ctrl/Cmd+Z撤销，重做有菜单入口。输入框操作以文字编辑为优先。参数修改后标为“待重算”的纸样不能直接作为制造版本。

## 常见问题

|现象|先做什么|保留的数据|
|---|---|---|
|拆板失败/质量不合格|查看诊断位置，调整手工缝线或降低输入复杂度后重算|旧已接受纸样保留|
|2D改完3D未更新|检查映射是否失效，执行重新绑定/预览|人工2D修改保留|
|找不到外链图片|按提示重定位原文件并检查是否同一hash|原引用和占位信息保留|
|保存失败/磁盘满|停止继续大量编辑，释放空间或另存至可写位置|旧项目包和工作恢复点保留|
|应用异常退出|重启选择恢复，核对恢复revision，再另存副本|最后完整提交，不保证最后未提交拖动|
|许可证到期/断网|继续基础打开、保存、CAD和基础导出；恢复网络刷新高级能力|已有高级几何仍可读取|
|GPU/AI不可用|关闭高质量渲染/AI，使用2D与传统识别|项目几何和人工结果保留|
|新版本项目无法在旧版打开|使用升级前备份或受支持版本|不要强行覆盖新格式|

## 支持资料

提交问题时提供应用版本、系统、发生步骤、错误code和jobId；可生成本地诊断包并预览再分享。客户原图和项目内容不默认附带。发生制造尺寸疑问时记录设计值、数字文件测量值和实体打印值，便于区分算法、导出和打印环节。
''')

doc('29-范围覆盖与母文档映射.md', '母文档覆盖、补充假设与范围核对', '§0～128', r'''
## 章节覆盖

|母文档章节|工程归属|处理|
|---|---|---|
|0～1|00、01、27|目标/工程原则纳入；原文保留|
|2～3|21、25|研究和许可线索；未声称核验|
|4～8|02、03、04、17|技术栈、进程和模块|
|9～10|04、05|包格式、单位与精度|
|11～13|11|角色、物种、Morph约束|
|14～17|10、07|标定、识别、可编辑路径|
|18～22|05、07、08、12|纸样/缝份/接缝/关联|
|23～35|04、09|制造拆板、拓扑与评分|
|36～39|10、11|双视图、补偿、Foot/Paw/Tail|
|40～44|03、05、12|渲染、预览、撤销|
|45～46|14|AI与版本|
|47～49|13、07、31|排料、导出与标注|
|50～55|05、15、19|数据、授权和隐私|
|56～60|17、27、04、06|模块/插件、工程、接口|
|61～63|05、18、03|保存、性能、状态|
|64～67|03、10、12、28|工作台与交互闭环|
|68～74|07、08、11、05|制造验证、方向材料模板、迁移|
|75～79|18、30、31、09|测试、指标、诊断|
|80～85|16、20、05、19|服务、更新、恢复、日志隐私|
|86～94|22、23|I0～I9增量|
|95～100|01、22、26|MVP/1.0/未来范围及原则冲突|
|101～103|09、11、22、30|犬科/趾行腿/Paw三条闭环|
|104～110|14、04、05|训练授权、版本/seed/cache/资源|
|111～113|16、17、26|企业后续范围、API兼容|
|114～118|03、07、28|双语、交换格式、工具快捷键|
|119～120|18、12、15|硬件降级与离线基础|
|121～125|00、21、22、27|工程文档21项全部对应，变更联动|
|126～128|sources、21、25、26|来源原样保留、验证阶段、未核验事项|

## 版本范围细化

本套没有把全部未来能力偷偷纳入MVP。原文1.0必须项均在I9前追踪：双视图、参数身体、CAD、3D预览、花纹路径、Seam、自动展开/手工缝线、Paw/Foot/Tail、Padding、毛向、PDF/SVG/DXF、排料、License/VIP/离线授权、更新和恢复。

OBJ/GLB/glTF导入和静态GLB交换在I3/I7推进；DXF I7只承诺明确子集，复杂实体按不支持清单报告。FBX/USD、物理模拟、照片测量、AI三视图、成本核算、工艺单、直接激光/CNC控制、模板市场、云实时协作、完整企业服务器与公共SDK归F1+，不是删除，见REQ-048。

## 证据不足的补充项

进程桥接、数据库写入归属、数值公差、HTTP字段、资源限额、性能样本、AI指标、工期和工艺阈值是新增工程方案或目标；必须经相应增量实验评审。未引用实时外部事实作版本/许可证结论。发布团队不得把“待评审基线”更名“最终已验证规格”而不补证据。
''')

doc('30-测试用例与验收规程.md', '可执行测试用例与验收规程', '§34、68～79、95、96、101～103、128', r'''
## 执行约定

每条TC列明输入/前置、操作、预期和证据；实际执行记录使用templates/测试执行记录.md。当前全部“未执行”。用例覆盖正常、边界、失败和恢复。预期中的数字为当前候选基线；禁止在未走CR时随实测更改。

测试数据命名和oracle见31；P0表示每次候选发布必测，P1表示所属增量与受影响回归必测，P2为后续范围。追踪矩阵以REQ/TC对应，开发时允许增加子用例 TC-xxx-a/b 并保持父编号。
''')

doc('31-黄金数据与制造验证规程.md', '黄金数据、导出回读与工艺试做规程', '§48、75～79、101～106、128', r'''
## Fixture登记

所有下列数据都是待创建规格，当前并未随文档提供实际网格/图片/纸样，不能报告测试通过。优先合成可解析样本，其次获得明确授权的模板/参考图；版权不清的客户图片禁止加入仓库。

|ID|规格|oracle与目的|最早增量|
|---|---|---|---|
|FX-01|100×200mm矩形、半径50mm圆、带20mm孔矩形|解析面积/周长、缝份方向|I1|
|FX-02|开放/自交/重复点/极短边/NaN路径|确定错误code与不变量|I1|
|FX-03|100×100mm平面、半径50高200mm圆柱侧面、可展开圆锥片|已知展开尺寸与曲长|I3/I5|
|FX-04|球面patch、胶囊曲面Capsule、鞍面/复合曲率、非流形/退化mesh|展示双曲率失真和拒绝非法输入|I5|
|FX-05|1800mm犬科躯干，≤5万三角形，模板参数锁定|3～6片闭环、人工seam基准与工艺复核|I5|
|FX-06|植腿/趾行腿、Paw整片/分指、Tail|各部位缝长/花纹/毛向与试做|I7|
|FX-07|合成正背图各1200px高角色，含黄色花纹、透明边、侧面unknown|1800mm标定=1.5mm/px、可解析轮廓|I4|
|FX-08|100裁片实例，多材料、定向毛、镜像、超宽片|计数/碰撞/方向/底左基线|I7|
|FX-09|旧版本项目、缺资源、hash坏包、恶意ZIP和迁移中断|原子性/安全/兼容|I0起|
|FX-10|≥200张已授权测试图，按角色分组|独立人工mask与AI评估|I8|
|FX-11|100片×100段、20万三角形、2张4096图≤200MB包|18的性能基准|I3起|

每个fixture配manifest：id、version、sha256、creator、license、units、expectedTopology、expectedMetrics、tolerance、生成脚本/来源、人工审核人。输入和oracle分离；算法自己导出的结果不能作为其唯一正确性依据。

## 几何golden比较

规范化ID和环方向、固定排序，比较实体数量/拓扑/引用关系和坐标/曲长/面积公差。每例保留input.json、expected.json、expected.svg及manifest；expected记录Area、Perimeter、BoundingBox、Centroid、SeamLength、DistortionScore、PieceCount。边界重采样比较Hausdorff距离，候选≤0.01mm用于离散导出；核心f64比较按18。重命名或优化导致几何等价时仍输出ID remap差异供审查，不能忽略关联损坏。

更新golden必须附旧新指标、可视化叠加、差异原因、工艺影响和非作者复核。保存algorithm/model/options/seed，基准不得随应用启动自动重算。

## 导出独立回读

PDF由独立解析器读取路径坐标和页面大小，换算mm后测100/500/1000mm基准；SVG解析width/height/viewBox与路径变换；DXF由独立库/目标CAD读实体、单位和闭合性，不使用同一导出模块自我验证。I7在指定目标CAD版本登记实际支持的DXF实体，任何丢失必须报告。

PDF切页验证可打印域并集覆盖完整纸样，页重叠内同一点坐标一致；页码/拼接标记与总页数一致。不同尺寸/横纵向、页边界落在曲线极值、单片超大幅面、中英文标签和小数单位都要覆盖。

## 实体工艺验证

先打印校准尺，记录打印机/驱动/纸张/100%设置、标尺读数和测量工具精度；数字通过而实体偏差时先定位打印链。至少躯干、趾行腿、Paw、尾四类各2种代表性材料配置、每类至少1件试做（候选最小8件），记录裁片数量、缝份、实际缝长差、对位偏差、毛向和可操作性。

材料伸缩、毛厚和填充会影响成品；记录操作者、缝法、材料批次、测量方法和工艺意见，不能用试穿照片代替尺寸表。样本失败回写材料profile/算法风险与CR。Commercial放行由工艺顾问签收“支持样本范围”，不声称所有物种/材料通用保证。
''')

doc('32-可行性与立项论证.md', '可行性分析、资源估算与立项判定', '§1～5、42、77、86～103、119、128', r'''
## 论证范围

本分析依据母文档和拟议工程方案，不含市场实访、第三方技术现状核验或真实成本报价。用于决定分阶段投资与原型门禁，不能作为已证实市场收益或算法可行性的报告。

## 技术可行性与验证成本

|方向|可行性判断依据|必须取得的证据|失败后仍可交付的范围|
|---|---|---|---|
|毫米2D CAD|明确几何原语与已知运算路线|解析shape、偏移/相交退化集、独立导出回读|限定工具集但不能牺牲精度|
|参数身体|受控拓扑与Morph可形成可验证输入域|犬科1800mm模板、测量残差、极值组合|限定已验证模板|
|2D/3D绑定|明确face/patch/barycentric映射|拓扑变化与边界双侧关联用例|只读overlay与显式重绑定|
|制造型拆板|LSCM/ARAP只是参数化路线，制造还需约束|解析样本、躯干V1、趾行V2、Paw V3与实际缝制|手工seam+受控自动展开；范围变化须CR|
|双视图识别|传统视觉与人工修正可独立闭环|已标定合成图、侧面unknown与修正流程|人工编辑优先，不承诺自动恢复完整3D|
|AI增强|运行时与模型/数据是不同问题|授权数据、独立IoU/边界指标、CPU退化|保留传统识别，AI未达标不能标已完成|
|商业化|技术方案可设计，运营条件未提供|证书、服务、许可、支付、支持人员|内部验证版，不冒充商业发行|

## 原型投资门禁

SP-01（I0前半，≤5工作日）：验证桌面→隔离Rust→SQLite提交→项目包恢复最小往返，测消息开销。失败优先简化桥接/选择驱动，不建立两个写入真值。

SP-02（I1前半，≤5工作日）：验证曲线偏移、孔、尖角和独立PDF/SVG尺寸。未通过数值门禁不扩展UI工具数量。

SP-03（I5入口，首轮≤5工作日）：解析圆柱/平面与犬科小patch的LSCM/ARAP、尺度恢复和候选缝线。输出实验结论、性能和求解器许可记录；若不满足预期则追加有界研究计划，由产品/技术重新排期，不能无限延续SPIKE。

SP-04（I7入口）：趾行腿/Paw工艺试做，验证片数、缝长、毛向和最窄拼接处。SP-05（I8入口）：数据授权及CPU/GPU推理基准，验证模型清单可复现。

## 人力与成本估算方法

22的40～62周是顺序交付区间，假设前端、Rust几何、测试三个稳定角色，额外工艺/产品/发布按需参与。若三个角色全程各1FTE，则基础工作量为120～186人周；这只是预算测算场景，并非招聘要求或实际已投入，尚未包含外部模型训练、法务和证书等待。

预算模型：总成本=Σ(角色人周×该角色周成本)+硬件/测试机+签名/模型/素材授权+服务资源+外部专业审查+工艺试做+风险准备。周成本、币种、税费、材料价格和供应商报价均待提供，因此不填虚构金额。可先以I0～I1形成第一投资段，再按SP与验收结果滚动拨付后续。

## 运行与组织可行性

离线工作可减少现场网络依赖，但用户仍需模板、材料profile和测量输入。制造顾问的参与是验收前提，不是发布后收集反馈的替代。三平台需要实际硬件/系统环境和签名资格；若资源不足，产品负责人须通过CR限定首发平台，不能在宣传中保留未验证支持。

## 立项结论与退出条件

拟议结论：适合按增量模型先开展I0/I1并验证核心几何；制造自动拆板与AI属于有明确研究风险的后续投入。I0计划批准前补足角色/资源；I5原型反复无法通过解析及躯干门禁时，应调整算法路线、缩小可声明输入域或停止该能力投资。MVP范围、1.0品质和客户数据保障不得因沉没成本被虚构通过。
''')

doc('33-领域命令与交换格式补充契约.md', '领域命令、查询与交换格式补充契约', '§16～22、39、44、59～60、115～118', r'''
## 类型字典

UUID使用标准字符串表示，Revision为≥0整数，Mm为有限f64，Rad为有限f64。Point2Mm={x,y}，Point3Mm={x,y,z}。RGBA={r,g,b,a}各∈[0,1]并声明色彩空间；ViewType=front/back/left/right/top/bottom/custom；LegType=plantigrade/digitigrade；MaterialCategory=fur/foam/lining/other；MirrorMode=none/linked/copy；MarkingSemanticType=body_base/body_white/marking/ear_inner/paw_pad/claw/eye/accessory/background/unknown。

Manual Marking可无sourceImageId/sourceMask，须source='manual'；AI/vision必须记录输入资源和版本。Direction采用单位切向量或角度，零向量不是有效毛向。Path/Binding/Notch结构以05为准，禁止在各模块重新定义同名不同单位字段。

## Command API的公共规则

command.apply payload={commandType,arguments}，外壳带projectId/expectedRevision。每条命令校验所属项目、实体revision和所有引用，再生成forward/inverse delta；接受前不得广播已提交状态。返回changedIds、invalidatedIds、diagnostics、新revision。命令改变几何就进入undo；仅相机/选择不写领域日志。

|commandType|arguments|前置/结果不变量|
|---|---|---|
|CreatePathCommand|path含nodes/segments/closed|ID不冲突、段引用完整；开放路径允许编辑但非制造片|
|MoveNodeCommand|pathId,nodeId,positionMm:{x,y}|节点存在；更新相邻曲线与下游失效|
|SetBezierHandlesCommand|pathId,segmentId,c1,c2,nodeMode|cubic类型；corner/smooth/tangent约束由core校验|
|InsertNodeCommand|pathId,segmentId,t|0<t<1；Bezier用精确分裂公式，不改变原曲线形状|
|DeleteNodeCommand|pathId,nodeId,joinMode|删除后最小有效节点数；可能改变形状需预览|
|TransformPatternCommand|pieceIds,matrix,originMm|矩阵有限且可逆；重算方向/曲长；非等距变换标关联stale|
|SplitPatternCommand|pieceId,cutterPathId|切割拓扑合法；新ID及old→new映射；引用原子重建|
|JoinPathCommand|pathIds,toleranceMm|端点满足几何容差或明确吸附；不静默跨远距离连线|
|SetSeamAllowanceCommand|pieceId,edgeIds?,mode,widthMm?,samples?|mode constant/variable；可变samples为递增{s,widthMm}|
|AddNotchCommand|pieceId,edgeId,s,type,depthMm,label|s∈[0,1]；深度受缝份限制；有稳定ID|
|SetMaterialCommand|pieceIds,materialId|同项目材料存在；影响制造/排料下游|
|SetManufacturingMetadataCommand|pieceId,cutQty,mirrorMode,furRad?,grainRad?,labels|cutQty正整数；材料必需方向不能缺失|
|ChangeBodyParameterCommand|bodyId,templateVersion,values|单位与范围按模板；结果含测量残差与失效列表|
|EditMaskCommand|markingId,operation,brushOrPolygon|操作为add/erase/fill/split/merge；资源不可变写入|
|AcceptCalculationCommand|jobId,resultHash|与result.accept同一内部命令，不重复提交|

Boolean/Offset通过06的候选接口计算，真正采用结果仍生成命令；前端临时预览不能以更低精度结果代替最终提交。Rename/Delete/Duplicate等通用命令同样遵守引用校验与inverse补丁。删除被引用对象默认RESTRICT，显式级联必须在预览中列出影响。

## 查询与差量

project.snapshot返回projectId、revision、schemaVersion、entities或受控assetHandles和diagnostics；大对象不强行塞入8MiB JSON。差量事件domain.changed包含baseRevision/newRevision、upserts、deletedIds、invalidatedIds、remap。Renderer若发现baseRevision不等于本地revision则重新请求快照，不拼接遗漏事件。Selection只映射ID，不改变真值。

job.progress包含stage、completed、total?；job.finished含status、resultHash?、diagnostics、runtimeMeta。errors不得包含未经清洗的文件内容或任意堆栈。后端恢复会话时发送新的sessionId，旧订阅不得继续写当前项目。

## 导入/交换支持矩阵

|格式|首交付|支持子集|不支持/错误处理|
|---|---|---|---|
|PNG/JPG/WEBP|I4|单图参考、alpha、受控EXIF旋转|损坏/超64MP拒绝，不执行外链|
|SVG导入|I3|path/line/polyline/polygon/rect/circle/ellipse及仿射transform转为核心路径|script/事件/外链/foreignObject禁止；滤镜/文本转轮廓不自动保证，列不支持清单|
|OBJ导入|I3|静态顶点、面、法线/UV；多边形需验证后剖分|单位通常需用户明确声明；不把未声明数值默认mm；材料文件外链须用户选择|
|GLB/glTF导入|I3|静态三角网格、层级transform、基础材质和UV|按格式米单位换算×1000为mm；骨骼/动画只列未支持，不声称身体参数化|
|GLB导出|I7|静态身体/预览网格、基础颜色、从mm转换到米|不等价项目；不承诺保留SeamGraph/参数/历史|
|PDF/SVG导出|I1|制造路径、单位、标尺与标签|按07执行，不能从截图导出制造尺寸|
|PNG导出|I1|预览和明确DPI|不作为几何原生文件|
|DXF导出|I7|07的R2000子集、图层与毫米|设备兼容需实际回读；本期不承诺DXF导入|
|FPCAD|I0|05定义完整工程快照|未知必需特性拒绝可写打开|
|FBX/USD|F1+|未承诺|不以更换后缀冒充转换|

导入模型仅作为参考静态几何，若要参与参数身体或制造展开，需经过单位确认、拓扑检查、解剖分区和材料/缝线配置。导入成功不等于可制造。资产URL不自动下载；GLTF外部资源使用受控目录选择和范围检查。

## 业务schema落地约束

contracts目录提供可执行外壳模式，具体命令参数必须在I0/I1把本表转为严格discriminated-union schema（additionalProperties=false、字段范围、条件必填）；复杂拓扑和跨实体规则由Core/仓储校验，JSON Schema无法替代。schema生成变更与TC-006同PR审查。下游模块接口在其入口增量细化时冻结，不用占位payload:object作为正式安全边界。
''')

# 每行：编号、需求、来源、增量、主要设计、测试编号。
REQS = [
('001','项目创建、打开与可携带快照往返一致','8～9、50','I0','05-data-model.md','001'),
('002','自动保存、10个恢复点与崩溃后完整恢复','44、61、83','I0','05-data-model.md','002'),
('003','项目完整性、外链资源、格式迁移与前向兼容','9、74、109～110','I0','05-data-model.md','003'),
('004','命令撤销/重做、分支和事务一致性','44、107','I0','05-data-model.md','004'),
('005','毫米真值、f64往返和明确坐标转换','10、48','I1','04-rust-geometry-core.md','005'),
('006','安全IPC、revision冲突与异步任务取消','59～60、62','I0','06-ipc-protocol.md','006'),
('007','2D全部基础工具、路径节点和变换','17～19、117','I1','07-pattern-engine.md','007'),
('008','Boolean/Offset及全局、逐边、可变缝份','19～20','I1','07-pattern-engine.md','008'),
('009','Notch、标注、数量、镜像与材料信息','49、68','I1','07-pattern-engine.md','009'),
('010','无效几何阻断制造导出、警告可定位','34、68','I1','07-pattern-engine.md','010'),
('011','角色测量与参数身体、硬软约束','11～13、87','I2','11-body-parametric-system.md','011'),
('012','Morph稳定拓扑与下游失效传播','13、22、87','I2','11-body-parametric-system.md','012'),
('013','犬猫基础、植腿/趾行与尾爪参数','12、39、87','I2','11-body-parametric-system.md','013'),
('014','Face/Patch/Piece稳定关联及双向拾取','22、66～67','I3','12-3d-rendering.md','014'),
('015','SeamGraph、人工缝线、方向与吃量','21、26、69','I3','08-seam-engine.md','015'),
('016','缝长匹配与对位剪口','69～70、77','I3','08-seam-engine.md','016'),
('017','正背参考图导入、尺寸标定和旋转链','14、89、115','I4','10-marking-recognition.md','017'),
('018','传统分割、人工修正与候选可回滚','15～17、89','I4','10-marking-recognition.md','018'),
('019','制造拆板、失真、再切、用户硬约束','23～35、90','I5','09-unwrap-algorithm.md','019'),
('020','花纹投影、节点逆映射、侧面不确定性','36～37、66、91','I6','10-marking-recognition.md','020'),
('021','花纹跨片连续性和匹配剪口','70','I6','08-seam-engine.md','021'),
('022','PDF/SVG/PNG输出及标尺/分页','48、95、115','I1','07-pattern-engine.md','022'),
('023','输出毫米比例误差≤0.1%','10、48、77','I1','07-pattern-engine.md','023'),
('024','材料、毛向、泡棉/填充和内衬补偿','38、71～72','I2','11-body-parametric-system.md','024'),
('025','按数量/材料/毛向/镜像约束排料','47、92','I7','13-nesting.md','025'),
('026','本地AI模型版本、质量评估和可编辑候选','45～46、93、104','I8','14-ai-system.md','026'),
('027','签名授权、离线期限与密钥轮换','51～54、81','I9','15-license-system.md','027'),
('028','FeatureGate集中执行与高级配额幂等','7、51～52','I9','15-license-system.md','028'),
('029','断网/到期时保留本地核心与已有数据','54、94、120','I9','15-license-system.md','029'),
('030','签名更新、安装失败回退及项目兼容','74、82','I9','20-release.md','030'),
('031','不可信导入、IPC和路径安全边界','55～56、59','I0','19-security.md','031'),
('032','隐私默认不上传、日志脱敏、独立同意','55、84～85、104','I0','19-security.md','032'),
('033','内置模块注册和故障隔离','7、56','I0','17-plugin-sdk.md','033'),
('034','2D/3D交互性能、LOD和proxy','43、62、119','I3','18-testing.md','034'),
('035','算法失败/取消/Worker崩溃不覆盖原数据','62、107','I0','02-system-architecture.md','035'),
('036','算法结果版本、哈希缓存与seed','105～108','I5','04-rust-geometry-core.md','036'),
('037','同后端确定性、跨平台几何回归','0、75～77、106','I5','18-testing.md','037'),
('038','MVP全流程与新用户可用性','95、98、101','I6','24-评审验收与质量保证计划.md','038'),
('039','账号/订阅服务、幂等与API兼容','80～81、94、113','I9','16-cloud-services.md','039'),
('040','三平台桌面及低GPU/无AI基础降级','4、119','I9','20-release.md','040'),
('041','SBOM、NOTICE、模板/模型授权和发行审查','2～3、123、128','I9','21-open-source-notices.md','041'),
('042','中文/英文、本地化单位与诊断可访问','79、114','I1','03-frontend-architecture.md','042'),
('043','快捷键/工具状态、取消与撤销合并','44、118','I1','03-frontend-architecture.md','043'),
('044','本地模板、其他物种及特殊部位制造扩展','1、39、73、102～103','I7','11-body-parametric-system.md','044'),
('045','DXF与大幅PDF制造互操作','48、92、96','I7','07-pattern-engine.md','045'),
('046','SVG/OBJ/GLB导入与GLB交换的明确子集','115～116','I3','12-3d-rendering.md','046'),
('047','第三方SDK沙箱、企业/协作扩展边界','56、97、111～112','F1+','17-plugin-sdk.md','047'),
('048','物理模拟、未来AI/格式/机器与市场范围管理','42、97、115','F1+','29-范围覆盖与母文档映射.md','048'),
]

# 编号、标题、fixture/前提、操作、可判定期望、证据。
TESTS = [
('001','项目往返','新空工作库和嵌入图片项目','创建→编辑名称/实体→保存→关闭→打开→再存','UUID、revision、几何和资源hash一致；manifest清单验证成功；不存在私有token','包内容hash、领域diff'),
('002','保存与恢复故障注入','FX-09与最近10个恢复点','连续编辑、等待3秒/30秒；在事务与ZIP替换各阶段终止；另测磁盘满','只能恢复完整revision；旧目标文件始终可读；错误时dirty不清除；10个完整点按策略保留','故障点矩阵、恢复日志、文件hash'),
('003','格式/资源/迁移','FX-09含旧版/新版/坏hash/缺外链','依次导入；迁移中断；重定位正确与错误资源','旧版迁移副本成功；中断不改原包；未知major不覆盖；坏hash拒绝；缺外链清晰提示','迁移diff、源文件前后hash、诊断'),
('004','撤销重做分支','三条编辑命令和已接受计算结果','执行A/B/C→undo两次→redo一次→新编辑D；重启恢复','状态A/B/C逆补丁精确；D后旧redo不再可用；算法redo不重新求解；事务/日志一致','每步revision与hash'),
('005','数值和坐标往返','FX-01、1e-5mm小数与边界坐标','序列化往返100次；缩放视图；变换及逆变换','UI缩放不变几何；f64往返不被0.1mm截断；坐标/曲长差≤0.001mm；NaN拒绝','数值报告、单位断言'),
('006','IPC和竞争','合法/非法消息、两个expectedRevision相同命令','非法方法/字段；重复ID不同payload；同时提交；取消与accept竞争','非法拒绝；同ID同payload不重复提交；冲突报REVISION_CONFLICT；只有一个线性化终态','契约响应与revision日志'),
('007','CAD工具完整性','FX-01与Bezier路径','逐项执行19的选择/移动/旋转/缩放/镜像/复制/分割/修剪/连接/圆角/倒角/编辑/标注/测量/对齐/吸附，并撤销','解析变换正确；节点ID/remap有效；所有工具可操作且撤销恢复；无隐式px制造值','工具×正常/边界矩阵、几何diff'),
('008','Boolean和缝份','100×200矩形、孔、尖角、短边','union/difference；miter外偏10；逐边/可变宽；负偏至消失','miter外框120×220mm；孔方向正确；拓扑不变量成立；空结果有诊断不成制造片','独立面积/边界比较'),
('009','标注与剪口','有10mm缝份的成对纸样','添加3mm剪口、标签、Cut2与mirror；修改边再导出','剪口随弧长/方向更新；越界阻断；输出包含全部制造字段与实际实例数','实体数据和输出标签回读'),
('010','制造错误门禁','FX-02与缺毛向/stale纸样','逐项运行检查后尝试PDF/SVG/DXF制造输出','每个Error定位rule/entity且阻断；Warning需确认并留报告；没有伪成功文件','错误矩阵、导出目录与报告'),
('011','测量求解','锁定1800mm犬科模板','改身高/胸腰臀；输入负值/异常比例/上限值','身高残差≤1mm；围度≤max(2mm,0.5%)；硬约束拒绝、软约束警告可撤销','参数与实测残差表'),
('012','Morph与下游失效','带patch/marking/nesting项目','改Morph；切换有拓扑差异模板；undo','同拓扑ID保持；拓扑变更版本更新；无法映射标stale；旧异步结果不可接受；undo恢复','ID/remap与依赖状态diff'),
('013','物种和部位参数','犬猫、植腿/趾行、尾爪模板','各参数最小/默认/最大组合生成身体','网格流形无退化、自交诊断可见；腿型和物种兼容检查；Tail/Paw参数实际改变对应区域','模板矩阵、网格检查'),
('014','双向拾取','I3预制patch和编辑/显示两级LOD','3D拾取→2D聚焦；反向拾取；自由改片边界','全部ID定位正确；一对多显示选择；自由变形使绑定stale而不伪造精确贴合','ID链日志、交互录像'),
('015','接缝与吃量','100/103mm两边和反向曲线','创建无吃量/吃量e=-3mm；反向；锁定后优化','Δ=100-103=-3；e=-3时r=0；方向正确；锁定seam不会消失','L(A)/L(B)/e/r和锁定diff'),
('016','缝长阈值与notch','残差0.999/1/1.001/1.999/2mm样本','按Beta/Commercial profile检查；反向映射剪口','Beta严格<2，Commercial≤1；比较seam非cut周长；notch配对残差在目标内','边界值报告、对位映射'),
('017','图像标定','FX-07和EXIF旋转/裁切版本','在1200px人物上标1800mm；标点重合；变换后识别','scale=1.5；无效点拒绝；同一花纹还原到一致毫米位置','矩阵与毫米轮廓diff'),
('018','人工修正保护','FX-07分割结果','添加/擦除/填孔/拆分/合并/改节点；undo；再识别','全部可撤销；手工锁定不覆盖；重新识别为候选；source与版本完整','命令历史和路径hash'),
('019','拆板闭环与异常','FX-03/04/05','固定seed展开；强制锁线；预算用尽；非流形输入','解析样本尺寸正确；犬科3～6片；合法闭合无自交；超阈Needs Review；非法输入拒绝；旧结果保留','每面误差、片数、SVG、overlay、算法meta'),
('020','投影与逆映射','FX-07映射到犬科，侧面留空','投影黄色区；跨seam拖节点；越界；改topologyVersion','域内映射正确；跨片共享MarkingId；侧面unknown；越界/旧拓扑拒绝或stale，不跳面','重心坐标、路径与3D差异'),
('021','跨片连续','两片缝线上的花纹交点和吃量样本','移动交点0.5/1.5mm；反向/吃量映射；生成对位标记','按共同弧长比较；≤1mm目标内合格，超限警告/修复；歧义不自动误配','交点配对表与残差'),
('022','基础导出','FX-01、跨A4纸样、中英文标签','输出PDF/SVG/PNG；更改页面方向/边距','文件可打开；PDF拼接覆盖完整；SVG显式mm；PNG带DPI且预览用途；标签不缺字','独立回读与页面覆盖报告'),
('023','比例验收','100/500/1000mm长度和圆','输出→独立解析数字尺寸→100%打印测量','数字相对误差≤0.1%；打印结果独立记录，驱动缩放造成超差不能归作数字通过','数字/实体双列测量表'),
('024','材料补偿和毛向','两种材料profile与padding身体','加25mm胸填充；改视觉毛长；更改内衬；缺方向导出','padding仅作用目标场；视觉毛长不自动加裁片；制造面按profile；依赖正确失效','表面距离/依赖diff、工艺签收'),
('025','排料约束','FX-08','固定seed排料；手动违规拖动；改数量/材料/尺寸','完整可行解零碰撞/越界/方向错/漏件；超宽列unplaced；修改使stale；长度不劣底左基准','实例清单、碰撞独立报告、利用率'),
('026','模型与AI评估','FX-10、模型manifest、CPU/GPU','校验模型；分割；升级模型；显存不足；人工改后重跑','坏hash拒绝；指标按14报告并达目标才验收；升级不改旧结果；CPU/传统降级；人工可回滚','分组评估、模型hash、网络/编辑日志'),
('027','令牌验证','测试专用密钥、签名/篡改/未知keyId/过期token','逐一校验并轮换公钥','只接受合法签名与期限；不记录原token；轮换策略覆盖当前/过渡/撤销key','用测试密钥的验证矩阵'),
('028','能力与配额边界','Free/Pro测试能力和重复job','绕过UI直调高级API；重复reserve/commit；取消任务','Main拒绝无能力；同任务不重复扣减；取消释放；业务不以vip分支代替feature','权限矩阵与配额账本'),
('029','完全断网与到期','已有高级项目；有效/过期离线token','禁网启动并打开编辑保存PDF/SVG；尝试高级计算；时钟回拨','基础全程可用、已有数据不丢；高级按期限；网络失败不当撤销；回拨有解释','禁网流程录像与文件hash'),
('030','更新失败与回滚','当前/候选包、坏签名/hash、旧安全版本','各路径下载/安装；中断；迁移后尝试旧版','坏包不装；保留旧可运行版；未保存项目先处理；旧版不覆盖新格式；安全降级拒绝','更新日志、包签名、项目备份hash'),
('031','恶意输入','路径穿越/链接/重复项/炸弹/SVG脚本/恶意IPC','在隔离测试目录导入全部样本','无越根写入、脚本/网络执行或任意channel；超限可控拒绝；进程故障不损项目','安全测试日志、目录diff、抓包'),
('032','隐私默认值','全新配置和敏感标记测试项目','默认操作抓包；开启单项遥测；撤回；生成诊断','默认无项目上传；遥测同意不启用训练；撤回停采集清队列；诊断无图片/token/完整敏感路径','脱敏扫描、网络记录、同意状态'),
('033','模块注册','重复ID/循环依赖/初始化失败模块','启动、重试、dispose','重复/循环拒绝；可选模块失败不阻基础CAD；订阅资源释放','模块状态与资源统计'),
('034','性能基线','FX-11、B-REF/B-MIN','按18预热/20次测量拖动、打开、3D操作','p95/FPS/耗时达到18；记录全部平台和硬件，不用单次最快值','性能CSV与环境清单'),
('035','Worker故障与取消','长计算进行中并含未保存编辑','取消、强杀Worker、内存超限、同时编辑','UI取消≤200ms；安全退出≤2s或终止；旧状态不覆写；项目仍可保存','时间戳、revision/hash、峰值RSS'),
('036','缓存版本','相同输入、变更材料/算法/options/seed样本','两次计算；分别改变每个依赖再计算','完全相同命中；任一语义依赖变更不误命中；缓存损坏可重算；手工结果不被GC','cache key、命中记录、结果hash'),
('037','确定性回归','FX-03/05/08固定构建/seed','同后端重复10次；三平台运行','同后端规范hash一致；跨平台拓扑一致、坐标/曲长差≤0.001mm；超限不自动更golden','golden diff和运行元数据'),
('038','MVP用户验收','5位基础制作用户、FX-07/05','独立按28完成全链，开发仅观察；另执行V1演示','至少4位无需接管完成；双视图→人工修正→Pattern→缝份→3D→PDF/SVG完整；Beta缝残差<2mm','观察表、失败记录、完整项目与输出'),
('039','商业API与计费','mock服务和测试供应商事件','401/403/429/5xx；webhook重放；旧两个minor客户端','错误语义正确；退避有界；支付重复不重复授权；兼容测试通过；服务失败不阻本地','契约报告、幂等记录'),
('040','平台与降级','冻结OS矩阵、低GPU与CPU模式','每平台安装/打开/编辑/保存/基础输出；context lost；卸载','基础闭环通过；渲染恢复或2D可用；卸载保留项目；每平台独立结论','平台矩阵、日志与安装包hash'),
('041','依赖发行核对','锁文件、安装包、模型/模板清单','扫描SBOM与实际制品；审查LICENSE/NOTICE和来源','无未登记/待审组件；notice与实际版本一致；必要义务有证据；未完成阻发行','SBOM、审查签收和notice'),
('042','国际化与可访问','中文/英文、200%缩放、输入小数','切换语言/缩放、键盘遍历、检查单位和热图','未保存内容保留；不截断关键错误；单位明确；非颜色信息能辨等级；英中文案无缺key','双语界面检查与键盘记录'),
('043','工具状态机','Bezier拖动、文本框焦点、任务面板','拖动Escape/失焦；一百帧拖动；文本Ctrl+Z；卸载面板','取消不提交；一次拖动一条命令；文本撤销不改工程；卸载不泄漏订阅或误停项目任务','命令计数、状态转换和资源记录'),
('044','模板与部位制造','FX-06及兔熊鹿龙Custom模板','导入/升级/非法约束；各模板生成纸样；高级padding','旧项目模板冻结；所有承诺模板有可用资产/参数范围；V2/V3完整且工艺试做记录；失败不得只列名称','模板逐项清单、试做报告'),
('045','DXF与大幅分页','复杂带孔片、Bezier、A0/自定义超大尺寸','导出R2000子集→独立CAD回读；检查分页并集','单位mm、闭合/层/数量/标签正确，弦误差≤0.01mm，比例≤0.1%；无漏片','目标CAD版本、回读数值、页面覆盖'),
('046','交换格式子集','带单位/无单位OBJ、GLB、SVG及不支持实体','导入→确认单位→保存；静态GLB导出回读','单位未知需确认；静态三角网格与白名单路径保留；不支持内容明示；GLB米与内部mm正确换算','实体清单与坐标回读'),
('047','未来SDK边界','Future插件宿主及恶意插件','尝试越权文件/网络/内存耗尽/不兼容major','沙箱生效且项目保留后才允许开放安装；1.0只验证不暴露未审第三方入口','安全审查；Future当前未执行'),
('048','未来范围审查','新增物理/云协作/机器控制需求','建立CR并对照1.0边界、接口、风险和验收','未批准不列1.0已实现；独立增量有REQ/TC/模型验证，不用表面预览替代物理','CR和新增量基线；Future未执行'),
]

TEMPLATES = {
'工作项与PR记录.md': r'''# 工作项与PR记录

状态：待填写（不是已批准任务）

|字段|内容|
|---|---|
|工作项ID/增量|WI-Ix-xxx / Ix|
|REQ/设计章节/TC|待填写|
|问题与完成后行为|待填写具体输入与输出|
|前置依赖与Ready检查|待填写|
|实现文件/commit/PR|尚无|
|接口/schema/算法版本变化|待填写或说明不涉及|
|迁移/恢复/安全/许可影响|逐项分析|
|测试命令/环境/fixture hash|尚未执行|
|实测结果/证据路径|尚无|
|性能变化与已知限制|待填写|
|责任人/估算/审查人|尚未指派|
|独立评审与剩余意见|待评审|
''',
'测试执行记录.md': r'''# 测试执行记录

状态：未执行

|字段|内容|
|---|---|
|Run ID / TC / REQ / 增量|待填写|
|执行人/时间/复核人|待填写|
|OS/CPU/GPU/驱动/RAM/缩放|待填写精确值|
|commit/build/算法/模型/后端|待填写|
|fixture ID/version/hash|待填写|
|前置与操作命令|待填写可复现步骤|
|期望及单位/公差|引用锁定文档版本|
|实测及单位|未测量|
|结论|未执行/通过/失败/阻塞|
|原始日志/输出hash/数值diff/录屏|尚无|
|关联缺陷与复测|待填写|

性能必须记录各次原始值和统计方法；制造验证同时记录数字文件与实体测量，不以截图替代数值。
''',
'增量验收记录.md': r'''# 增量验收记录

状态：待验收

增量/基线/构建：待填写。参加人：产品、技术、测试、工艺（适用）、发布（适用）。

|检查项|预期|实测/证据|结论|
|---|---|---|---|
|范围与REQ覆盖|全部所属Must|尚无|未验收|
|用户闭环演示|22规定出口|尚无|未验收|
|几何/制造指标|18/30锁定值|尚无|未验收|
|回归/安全/恢复|关键全部通过|尚无|未验收|
|性能/兼容|所属矩阵|尚无|未验收|
|缺陷|零S0/S1|尚无|未核对|
|迁移/依赖/文档|全部更新|尚无|未核对|

结论只能在证据齐备后填写：接受 / 有条件接受 / 拒绝。豁免项、理由、责任人、到期日、签收与下一增量反馈必须列明。禁止豁免制造比例错误、数据损坏与关键安全缺陷。
''',
'缺陷与变更记录.md': r'''# 缺陷与变更记录

## 缺陷

BUG-ID、严重度S0～S3、发现版本、REQ/TC、复现输入hash、操作、实际/期望、影响范围、临时绕行、责任人、修复commit、回归证据、独立复核、关闭日期。当前全部待填写。

## 变更

CR-ID、提出人/日期、问题与收益、原基线、新方案、受影响REQ/设计/API/schema/算法/TC/工期/许可/数据、迁移与回退、替代方案、决定人和结论、实施工作项、验证证据。降低阈值必须列明真实实验与用户影响。

状态：提出→影响分析→决定→实施→验证→关闭；未批准CR不能偷偷改变已冻结验收。
''',
'依赖审查记录.md': r'''# 依赖审查记录

状态：pending

名称、精确版本/commit、官方来源、下载hash、使用模块、直接/传递关系、构建/运行用途、链接方式、实际LICENSE路径/SPDX、修改文件、分发资源、NOTICE/源码提供义务、漏洞扫描日期、商业授权凭据引用、法务/技术审查人、决定与日期、SBOM制品引用。所有项目待实际引入后填写。

字体/模型权重/网格/纹理各自建记录，不能继承软件框架许可。无证据时不能将状态改approved。
''',
'算法实验与工艺验证.md': r'''# 算法实验与工艺验证

状态：未执行

实验ID、假设、fixture来源许可/hash、算法版本/seed/PRNG/preset/backend/build、输入拓扑/片数/材料、约束、预算与停止原因。

|指标|基线|实测|差异/说明|
|---|---|---|---|
|EA/EE/角误差/D的均值p95最大|待填|未测|待填|
|片数/缝长残差/毛向偏差|待填|未测|待填|
|耗时/峰值内存|待填|未测|待填|
|几何有效性/制造门禁|待填|未测|待填|

工艺部分：打印机/驱动/比例、标尺工具与测量精度、材料批次/厚度/伸缩条件、操作者、裁剪数量、实际缝长和对位偏差、样衣记录、失败分析、工艺师签收范围。结论须说明假设是否被支持，不允许只贴成功图片。
''',
'发布清单与回滚记录.md': r'''# 发布清单与回滚记录

版本/渠道/平台/架构/commit/build：待填写。状态：未发布。

制品hash与签名、更新manifest、SBOM/NOTICE、测试报告、增量签收、格式迁移备份、已知问题、最低安全版本、上一稳定版、灰度比例、监控窗口、暂停阈值、负责人/支持入口：逐项待填写。

回滚事件须记录触发证据、受影响用户/版本、是否允许项目格式回滚、使用的备份、采取前向修复或包回退、操作时间、验证与对外说明。当前没有生产域名、证书或真实发布证据。
''',
}

ENVELOPE_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'urn:fpcad:ipc-envelope:v1', 'title':'FPCAD IPC Request Envelope v1',
 'type':'object', 'additionalProperties':False,
 'required':['protocolVersion','requestId','method','payload'],
 'properties':{
  'protocolVersion':{'const':1},
  'requestId':{'type':'string','format':'uuid'},
  'method':{'enum':['project.create','project.open','project.save','project.snapshot','command.apply','command.undo','command.redo','reference.calibrate','body.setParameters','pattern.offset','pattern.boolean','seam.link','job.submit','job.cancel','result.accept','result.discard','validation.run','export.create','feature.list']},
  'projectId':{'type':'string','format':'uuid'},
  'expectedRevision':{'type':'integer','minimum':0},
  'payload':{'type':'object'}
 },
 'allOf':[{'if':{'properties':{'method':{'enum':['project.save','command.apply','command.undo','command.redo','reference.calibrate','body.setParameters','seam.link','result.accept']}}},'then':{'required':['projectId','expectedRevision']}}]
}

MANIFEST_SCHEMA = {
 '$schema':'https://json-schema.org/draft/2020-12/schema', '$id':'urn:fpcad:manifest:v1',
 'title':'FPCAD Project Manifest v1', 'type':'object', 'additionalProperties':False,
 'required':['format','formatVersion','schemaVersion','migrationVersion','applicationVersion','unit','createdAt','updatedAt','projectId','contentHash','files'],
 'properties':{
  'format':{'const':'fpcad'},'formatVersion':{'const':1},'schemaVersion':{'type':'integer','minimum':1},
  'migrationVersion':{'type':'integer','minimum':0},'applicationVersion':{'type':'string','minLength':1},
  'unit':{'const':'mm'},'createdAt':{'type':'string','format':'date-time'},'updatedAt':{'type':'string','format':'date-time'},
  'projectId':{'type':'string','format':'uuid'},'contentHash':{'type':'string','pattern':'^[a-f0-9]{64}$'},
  'files':{'type':'array','minItems':1,'items':{'type':'object','additionalProperties':False,'required':['path','size','sha256'],'properties':{
   'path':{'type':'string','minLength':1},'size':{'type':'integer','minimum':0},'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}
  }}}
 }
}

def build():
    ROOT.mkdir(parents=True, exist_ok=True)
    for folder in ('sources','contracts','templates'):
        (ROOT/folder).mkdir(exist_ok=True)
    source = Path(r'C:\Users\koci\Downloads\FurryPatternCAD_完整实现设计文档.md')
    archived = ROOT/'sources'/source.name
    if source.exists():
        shutil.copyfile(source, archived)
    if not archived.exists():
        raise RuntimeError('缺少母文档，不生成无法追溯的资料集')
    source_hash = hashlib.sha256(archived.read_bytes()).hexdigest()
    (ROOT/'sources'/'来源记录.json').write_text(json.dumps({
        'sourcePath':str(source),'archivedFile':archived.name,'sha256':source_hash,
        'sourceVersion':'1.0.0','sourceDate':'2026-09-11','copiedWithoutModification':True,
        'externalReferencesVerified':False
    },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    # 完整方法范围在正文中定义；模式文件是可验证的基础外壳，不冒充全部业务schema。
    for name, schema in [('ipc-envelope.schema.json',ENVELOPE_SCHEMA),('project-manifest.schema.json',MANIFEST_SCHEMA)]:
        (ROOT/'contracts'/name).write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    example = {'protocolVersion':1,'requestId':'00000000-0000-4000-8000-000000000001','method':'command.apply',
      'projectId':'00000000-0000-4000-8000-000000000002','expectedRevision':4,
      'payload':{'commandType':'MoveNodeCommand','arguments':{'pathId':'00000000-0000-4000-8000-000000000003','nodeId':'00000000-0000-4000-8000-000000000004','positionMm':{'x':100,'y':200}}}}
    (ROOT/'contracts'/'ipc-request.example.json').write_text(json.dumps(example,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'contracts'/'README.md').write_text('''# 契约附件边界

两个JSON Schema使用Draft 2020-12。ipc-envelope仅定义请求外壳及部分修改命令的revision必填约束；其余方法的payload、条件校验、响应/事件由06和模块设计规定，I0必须进一步形成方法级schema与生成类型。project-manifest定义包清单字段，不验证路径安全、清单唯一性、内容hash或跨文件引用，这些必须由运行时实现。

时间/UUID的format校验需验证器显式启用。示例使用合成UUID，不含用户数据。基础结构检查不代表实际协议实现已通过测试。

项目内容哈希规范：files按路径UTF-8字节升序；每项键序固定path,size,sha256；无空白、非ASCII直接UTF-8编码，size十进制整数；此files数组字节求SHA-256，不含manifest。路径为正斜杠相对路径，唯一性/大小写冲突按19验证。授权签名JSON规范单独在I9使用经过测试的规范化实现，不能沿用任意JSON.stringify结果。
''',encoding='utf-8')

    req_table = '\n\n|REQ|需求|原文§|首次增量|主要设计|验收测试|状态|\n|---|---|---|---|---|---|---|\n'
    for rid, title, source_sec, inc, design, tc in REQS:
        req_table += f'|REQ-{rid}|{title}|{source_sec}|{inc}|[{design}]({design})|[TC-{tc}](30-测试用例与验收规程.md#tc-{tc})|未实现/未执行|\n'
    title,src,body=DOCS['01-prd.md']; DOCS['01-prd.md']=(title,src,body+'\n\n## 编号需求清单\n'+req_table)
    title,src,body=DOCS['23-需求追踪矩阵.md']; DOCS['23-需求追踪矩阵.md']=(title,src,body+req_table)
    cases=''
    for tid,title,fixture,steps,expected,evidence in TESTS:
        inc=next(r[3] for r in REQS if r[5]==tid)
        priority='P2' if inc=='F1+' else ('P0' if tid in {'001','002','003','004','005','006','010','016','019','023','029','030','031','035','037','038','041','045'} else 'P1')
        cases+=f'\n\n<a id="tc-{tid}"></a>\n### TC-{tid} {title}\n\n- 需求/增量：REQ-{tid} / {inc}；优先级：{priority}；状态：未执行。\n- 输入与前置：{fixture}。\n- 操作：{steps}。\n- 期望：{expected}。\n- 证据：{evidence}。\n'
    title,src,body=DOCS['30-测试用例与验收规程.md']; DOCS['30-测试用例与验收规程.md']=(title,src,body+cases)

    for name,(title,src,body) in sorted(DOCS.items()):
        header=f'# FurryPattern CAD — {title}\n\n> 文档编号：FPCAD-SE-{name[:2]} · 版本：0.1.0 · 日期：2026-09-11\n> 状态：待评审工程基线；设计/目标不代表已实现或测试通过。\n> 需求来源：母文档{src}；新增工程约束按00的标记规则处理。\n\n[返回文档总览](00-文档总览与使用指南.md) · [需求追踪](23-需求追踪矩阵.md) · [决策与待决](26-架构决策与待决事项.md)\n\n'
        if name.startswith('00-'):
            body+='\n\n|文件|内容|\n|---|---|\n'+''.join(f'|[{n}]({n})|{t}|\n' for n,(t,_,_) in sorted(DOCS.items()) if not n.startswith('00-'))
            body+='\n\n附件：[CSV追踪矩阵](traceability.csv)、[测试规程](30-测试用例与验收规程.md)、[契约说明](contracts/README.md)、[来源与哈希](sources/来源记录.json)。\n\n记录模板：'+ '、'.join(f'[{n[:-3]}](templates/{n})' for n in TEMPLATES)+'。\n\n文档工具：[重建脚本](_build_docs.py)、[校验脚本](_validate_docs.py)、[校验报告](validation-report.json)。重建会覆盖本工具生成的文档，正式编辑后应同步生成源或停止重建，不得覆盖人工评审记录。\n'
        (ROOT/name).write_text(header+body+'\n',encoding='utf-8')
    for name,body in TEMPLATES.items():
        (ROOT/'templates'/name).write_text(body.strip()+'\n',encoding='utf-8')
    with (ROOT/'traceability.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['需求ID','需求内容','母文档章节','首次增量','设计文档','验收测试','优先级','实现位置','代码版本','证据','状态'])
        for rid,title,src,inc,design,tc in REQS:
            writer.writerow([f'REQ-{rid}',title,src,inc,design,f'TC-{tc}','Future' if inc=='F1+' else 'Must','未实现','无','未执行','待评审'])
    print(json.dumps({'documents':len(DOCS),'requirements':len(REQS),'tests':len(TESTS),'templates':len(TEMPLATES),'sourceSha256':source_hash},ensure_ascii=False))

if __name__ == '__main__':
    build()
