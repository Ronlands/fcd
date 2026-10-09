# FurryPattern CAD

当前维护源码、构建和发布均位于 `workflow-update`。根目录 `npm` 命令转发到当前项目。

- 双击 `启动新版FurryCAD.cmd`：运行 `workflow-update/release/latest.json` 指定的最新发布程序，使用现有本地工作库。
- 开发运行：`npm start`；开发构建：`npm run build`。
- 完整说明：[当前 README](workflow-update/README.md)。
- 本轮修复与验收：[双视图、花纹贴附与裁切修复验收](workflow-update/Docs/软件工程文档/67-双视图贴附裁切修复验收.md)。

`workflow-update/.local/workspace` 和根目录已有 `.local/workspace` 属于用户数据；`.tools` 是当前 Rust 工具链和离线依赖，均不属于旧软件或测试数据。
