> 页面说明更新（2026-10-07）：当前主导航为花纹提取 → 模型管理 → 花纹映射 → 开裁 → 制版。3D 只在中间三页显示；制版含二维及制作流程次级功能。本文涉及旧页面的入口或布局按 [46 章](46-五页职责与共享功能模块.md) 更正，历史记录不作为当前页面设计依据。

# FurryPattern CAD — IPC、任务与接口契约

> 文档编号：FPCAD-SE-06 · 版本：0.1.0 · 日期：2026-09-11
> 状态：待评审工程基线；设计/目标不代表已实现或测试通过。
> 需求来源：母文档§7、44、59、60、81、113；新增工程约束按00的标记规则处理。

[返回文档总览](00-文档总览与使用指南.md) · [需求追踪](23-需求追踪矩阵.md) · [决策与待决](26-架构决策与待决事项.md)

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
