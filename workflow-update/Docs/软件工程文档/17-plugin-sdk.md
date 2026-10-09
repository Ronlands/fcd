> 页面说明更新（2026-10-07）：当前主导航为花纹提取 → 模型管理 → 花纹映射 → 开裁 → 制版。3D 只在中间三页显示；制版含二维及制作流程次级功能。本文涉及旧页面的入口或布局按 [46 章](46-五页职责与共享功能模块.md) 更正，历史记录不作为当前页面设计依据。

# FurryPattern CAD — 模块注册与插件扩展契约

> 文档编号：FPCAD-SE-17 · 版本：0.1.0 · 日期：2026-09-11
> 状态：待评审工程基线；设计/目标不代表已实现或测试通过。
> 需求来源：母文档§7、56、57、97；新增工程约束按00的标记规则处理。

[返回文档总览](00-文档总览与使用指南.md) · [需求追踪](23-需求追踪矩阵.md) · [决策与待决](26-架构决策与待决事项.md)

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
