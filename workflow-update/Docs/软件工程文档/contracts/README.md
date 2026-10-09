# 契约附件边界

两个JSON Schema使用Draft 2020-12。ipc-envelope仅定义请求外壳及部分修改命令的revision必填约束；其余方法的payload、条件校验、响应/事件由06和模块设计规定，I0必须进一步形成方法级schema与生成类型。project-manifest定义包清单字段，不验证路径安全、清单唯一性、内容hash或跨文件引用，这些必须由运行时实现。

时间/UUID的format校验需验证器显式启用。示例使用合成UUID，不含用户数据。基础结构检查不代表实际协议实现已通过测试。

项目内容哈希规范：files按路径UTF-8字节升序；每项键序固定path,size,sha256；无空白、非ASCII直接UTF-8编码，size十进制整数；此files数组字节求SHA-256，不含manifest。路径为正斜杠相对路径，唯一性/大小写冲突按19验证。授权签名JSON规范单独在I9使用经过测试的规范化实现，不能沿用任意JSON.stringify结果。
