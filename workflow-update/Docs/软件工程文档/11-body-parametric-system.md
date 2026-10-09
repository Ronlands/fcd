> 页面说明更新（2026-10-07）：当前主导航为花纹提取 → 模型管理 → 花纹映射 → 开裁 → 制版。3D 只在中间三页显示；制版含二维及制作流程次级功能。本文涉及旧页面的入口或布局按 [46 章](46-五页职责与共享功能模块.md) 更正，历史记录不作为当前页面设计依据。

# FurryPattern CAD — 参数化身体、材料与模板设计

> 文档编号：FPCAD-SE-11 · 版本：0.1.0 · 日期：2026-09-11
> 状态：待评审工程基线；设计/目标不代表已实现或测试通过。
> 需求来源：母文档§11～14、38、39、71～73、87、101～103；新增工程约束按00的标记规则处理。

[返回文档总览](00-文档总览与使用指南.md) · [需求追踪](23-需求追踪矩阵.md) · [决策与待决](26-架构决策与待决事项.md)

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
