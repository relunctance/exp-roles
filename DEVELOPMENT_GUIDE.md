# Roles 打磨指南

> 如何创建、验证和迭代 AI Agent 角色

---

## 概述

本指南帮助你理解如何为 Expert Teams 打磨高质量的角色。

**角色（Role）** 是具有特定职责和技能要求的 AI Agent 定义。角色定义放在 `exp-roles/roles/` 目录下。

---

## 目录结构

```
exp-roles/
├── roles/                      # 角色定义目录
│   └── {role-name}/           # 单个角色目录
│       ├── SKILL.md           # 角色详细说明
│       ├── required_skills.txt # 必需的 skills 列表
│       └── config.yaml         # 角色配置
├── schemas/                   # JSON Schema 验证文件
├── validators/                # 校验工具
└── templates/                # 角色模板
```

---

## 创建新角色

### 1. 使用模板

```bash
# 复制模板
cp -r templates/role-template roles/my-new-role/
```

### 2. 修改配置文件

编辑 `roles/my-new-role/config.yaml`：

```yaml
name: "my-new-role"           # 唯一标识符（小写字母、数字、连字符）
display_name: "我的新角色"
description: "角色描述"

attributes:
  type: executor              # executor | reviewer | coordinator | observer
  tier: specialist            # specialist | generalist | lead

skills:
  required:
    - skill-name-1
  optional:
    - skill-name-2

applicable_phases:
  - plan
  - execute
  - verify

capabilities:
  - 能力描述1
  - 能力描述2
```

### 3. 编写 SKILL.md

在 `roles/my-new-role/SKILL.md` 中详细描述：
- 角色的主要职责
- 适用场景
- 工作方式
- 与其他角色的协作
- 约束和限制

### 4. 列出必需的 skills

在 `roles/my-new-role/required_skills.txt` 中列出必需的 skills：

```
superpowers:writing-plans
superpowers:test-driven-development
```

---

## 角色属性说明

| 属性 | 可选值 | 说明 |
|------|--------|------|
| **type** | executor | 执行者，负责具体任务 |
| | reviewer | 评审者，负责质量把关 |
| | coordinator | 协调者，负责多角色协作 |
| | observer | 观察者，监控和汇报 |
| **tier** | specialist | 专家，在特定领域深入 |
| | generalist | 通才，多领域都能胜任 |
| | lead | 领导，负责指导和决策 |

---

## 打磨角色的最佳实践

### 1. 从单一职责开始

好的角色应该**只做一件事**，并且做好。

❌ 避免：创建一个能做所有事情的"万能角色"
✅ 推荐：创建多个专业角色，通过协作完成任务

### 2. 明确输入和输出

每个角色应该有明确的：
- **输入**：它接收什么信息/任务
- **输出**：它产生什么结果
- **边界**：它不负责什么

### 3. 描述协作方式

在 SKILL.md 中明确：
- 这个角色向谁汇报
- 这个角色从谁那里获取信息
- 这个角色与谁协作

```markdown
## 协作方式

- 向 delivery-director 汇报进度
- 从 architect 获取架构决策
- 与 engineer 协作实现功能
```

### 4. 避免模糊描述

❌ 避免：
```markdown
角色应该"尽最大努力"完成工作
```

✅ 推荐：
```markdown
角色应该在 5 分钟内完成简单任务，
复杂任务需要向 delivery-director 申请更多时间
```

### 5. 定义清晰的约束

```markdown
## 约束

- 不修改共享配置（如 database.yaml）
- 不删除他人创建的代码
- 遇到不确定情况先询问再行动
```

---

## 验证角色

### 自动校验

```bash
# 校验所有角色
python validators/validate_role.py

# 校验特定角色
python validators/validate_role.py roles/my-new-role
```

### 手动检查清单

- [ ] `config.yaml` 格式正确，通过 JSON Schema 校验
- [ ] `required_skills.txt` 中列出的 skills 都存在
- [ ] `SKILL.md` 包含所有必要章节
- [ ] 角色的职责描述清晰，不会产生歧义
- [ ] 角色的边界明确，不会与其他角色冲突

---

## 常见问题

### Q: 角色之间职责重叠怎么办？

**A:** 职责重叠说明需要重新划分边界。检查是否有：
1. 两个角色做了同样的事情
2. 一个角色做了本应属于另一个角色的事

解决方案：
- 明确每个角色的**唯一职责**
- 使用 `blocked_by` 防止并行冲突
- 通过 delivery-director 协调

### Q: 角色太泛化怎么办？

**A:** 如果一个角色能做太多事情，考虑拆分成多个专业角色：

```
# 太泛化
"engineer": 能做前端、后端、运维、测试

# 拆分后
"frontend-engineer": 只做前端
"backend-engineer": 只做后端
"devops-engineer": 只做运维
"qa-engineer": 只做测试
```

### Q: 如何决定角色需要哪些 skills？

**A:** 根据角色的**工作方式**和**职责**：

1. 如果角色需要写实现计划 → `writing-plans`
2. 如果角色需要 TDD → `test-driven-development`
3. 如果角色需要调试 → `systematic-debugging`
4. 如果角色需要设计 → `brainstorming`

---

## 迭代流程

### 1. 创建角色（v0.1）
```bash
cp -r templates/role-template roles/new-role/
```

### 2. 定义基本结构
- 填写 `config.yaml`
- 写 `SKILL.md` 的框架

### 3. 在团队中测试
- 用 `spawn_team.py` 启动包含新角色的团队
- 观察角色行为是否符合预期

### 4. 收集反馈
- 角色是否完成预期任务？
- 角色是否与其他角色正确协作？
- 是否有遗漏的职责？

### 5. 迭代改进
根据反馈调整 `SKILL.md` 和 `config.yaml`

---

## 参考

- [SCHEMA.md](./SCHEMA.md) - 角色定义规范
- [Expert Teams](https://github.com/relunctance/expert-teams)
- [Superpowers](https://github.com/obra/superpowers) - 开发方法论 skills
