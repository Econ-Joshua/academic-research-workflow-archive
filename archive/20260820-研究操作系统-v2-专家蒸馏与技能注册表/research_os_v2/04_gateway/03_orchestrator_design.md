# Orchestrator设计

Orchestrator是任务调度器，不是研究主权者。

## 最小职责

1. 接收任务
2. 识别研究范式/阶段
3. 选择Skill
4. 检查权限
5. 选择模型
6. 选择Runtime
7. 执行任务
8. 调用验证
9. 触发Human Checkpoint
10. 写入日志

## 不负责

- 自己决定研究问题
- 自己决定核心理论
- 自己修改Human Sovereignty中的commitment

## 最小版本

第一版可以只是Python脚本，通过PowerShell启动；不需要复杂Agent framework。
