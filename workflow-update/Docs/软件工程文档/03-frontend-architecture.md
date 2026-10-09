# 前端模块架构

## 组合关系

导航注册表：`apps/desktop/src/modules/workflow-tabs.ts`。页面不得自行维护第二份排序。

| 页面文件 | 组合的功能模块 |
| --- | --- |
| `MarkingsPage.vue` | `ReferencesPanel`、`MaskEditor`、`MarkingLibrary` |
| `ModelManagementPage.vue` | `ModelLibrary`、`ModelTools`、`CustomTemplatePanel`、`MeshEditPanel` |
| `MappingPage.vue` | `MarkingLibrary` 抽屉、`MappingTools` |
| `MappingTools.vue` | `TexturePanel`、`InferenceTools`、`MarkingRecords`、`MarkingEditor` |
| `CuttingPage.vue` | `SurfaceCutPanel`、`CutLinesPanel`、`UnwrapTools`、`PreviewPiecePicker` |
| `PatternPage.vue` | `CutSelection`、`PatternProperties`、`MaterialsPanel`、`SeamsPanel`、`NestingPanel`、`WorkflowPage` |

页面仅组合模块和转发页间事件。业务操作实现由所属模块维护；例如 UV 贴附不会同时留在花纹提取页，模型导入不会留在预览组件和页面中各一份。

## 共享基础模块

- `WorkspaceSplit.vue`：统一分隔条、宽度约束、键盘及比例记忆。
- `ModelViewport.vue` / `SurfacePanel.vue`：一份模型预览、相机、拾取、三维直接交互实现；按当前页启用花纹或裁剪交互。
- `PatternCanvas.vue`：一份二维显示与鼠标事件视图。
- `modules/usePatternEditor.ts`：一份二维状态、节点编辑、曲线、测量、选择、缩放与纸张设置。
- `modules/patternEditorContext.ts`：类型化注入，保证二维画布与属性面板访问相同编辑实例。
- `LabelEditor.vue`、`AllowancePanel.vue`、`AdvancedTools.vue` 等现成功能组件由 `PatternProperties` 组合，打印/ZIP 使用现有 `CutSelection` 及主进程服务。

## 生命周期与隔离

访问过的页面保留挂载并隐藏，输入草稿不会因切页丢失；项目 ID 改变时页面及共享预览重建，避免上一个项目的临时状态泄漏。模型和二维预览在目标容器可用后再迁移。

裁剪草稿的 Teleport 仅在开裁模式创建，避免首次访问模型管理时挂载到尚不存在的裁剪容器。二维 V/P/D、Enter、Delete 快捷键仅在制版的裁片编辑标签生效；项目保存和撤销仍是全局命令。

## 验证入口

`tests/page-layout-e2e.mjs` 验证真实 Electron 页面顺序、功能边界、单实例、相机保留、跨页快捷键、裁剪草稿挂载、拖动/键盘/刷新后的比例以及窄窗口。其他桌面测试使用 `tests/ui-navigation.mjs` 的统一页面入口，保留原有几何、持久化和打印断言。
