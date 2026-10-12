# 文档导航

日常操作、安装和构建命令见[项目 README](../README.md)，开发协作规则见 [AGENTS.md](../AGENTS.md)。本目录只保留当前开发有用的说明。

| 文档 | 用途 |
| --- | --- |
| [项目结构](guides/project-structure.md) | 目录职责、代码定位、依赖和本地数据边界 |
| [桌面应用架构](design/architecture.md) | 页面、IPC、计算任务、事务与制造输出的关系 |
| [项目数据与契约](design/data-contracts.md) | 数据关系、持久化、文件交换和依赖完整性 |
| [原图轮廓恢复](design/reference-contour-recovery.md) | 像素约束下的直线、曲线、孔洞与拓扑检查 |
| [材料边界裁切](design/design-boundary-cutting.md) | 颜色边界、用户切线、展开与制造约束 |
| [ARAP 平衡重试](design/arap-balanced-retry.md) | 有界重试、接受条件与失效回退 |

文档与源码不一致时，以当前实现和测试为准，并修正文档。新文档放入 `guides/` 或 `design/`，避免重复根目录 README。旧规划、重复手册和历史验收资料不再保留在工作目录，需要时从 Git 历史追溯。

新的日志、截图、验证和清理报告写入 `test-results/`，不放入文档目录。移动或删除文档后运行 `npm run docs:check` 检查链接。
