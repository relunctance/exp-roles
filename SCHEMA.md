# Exp Roles 角色定义规范

## 概述

Exp Roles 是一个用于定义 AI Agent 角色的规范。每个角色有明确的职责、技能要求和适用场景。任何人都可以基于此规范创建自己的角色。

## 核心概念

### 角色（Role）

角色是具有特定职责和技能要求的 AI Agent 定义。

### 角色属性

角色属性定义了角色的基本特征和行为方式。

## 目录结构

```
exp-roles/
├── roles/                      # 角色定义目录
│   └── {role-name}/           # 单个角色目录
│       ├── SKILL.md           # 角色详细说明
│       ├── required_skills.txt # 必需的 skills 列表
│       └── config.yaml         # 角色配置
├── schemas/                   # JSON Schema 验证文件
│   └── role.schema.json
├── validators/                # 校验工具
│   └── validate_role.py
└── templates/                # 模板文件
    └── role-template/         # 新建角色的模板
```

## 角色文件格式

### config.yaml

```yaml
# 角色基本信息
name: "角色唯一标识符"        # 小写字母、数字、连字符
display_name: "人类可读名称"
description: "角色描述"

# 角色属性
attributes:
  type: executor              # executor | reviewer | coordinator | observer
  tier: specialist            # specialist | generalist | lead

# 技能要求
skills:
  required:
    - skill-name-1
    - skill-name-2
  optional:
    - skill-name-3

# 适用的流程阶段
applicable_phases:
  - plan
  - execute
  - verify

# 角色能力
capabilities:
  - 能力描述1
  - 能力描述2
```

### required_skills.txt

```
# 必需的 skills 列表
# 每行一个 skill 名称
skill-name-1
skill-name-2
```

### SKILL.md

```markdown
# 角色名称

## 角色职责

描述角色的主要职责。

## 适用场景

描述角色适用的场景。

## 工作方式

描述角色如何工作。

## 与其他角色的协作

描述角色与其他角色的协作方式。

## 约束和限制

描述角色的约束和限制。
```

## 字段说明

### config.yaml 字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| name | string | 是 | 唯一标识符，只能包含小写字母、数字、连字符 |
| display_name | string | 是 | 人类可读的显示名称 |
| description | string | 否 | 角色的详细描述 |
| attributes | object | 否 | 角色属性配置 |
| skills | object | 否 | 技能要求配置 |
| applicable_phases | array | 否 | 适用的流程阶段列表 |
| capabilities | array | 否 | 角色能力列表 |

### attributes 字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| type | string | 否 | 角色类型：executor(执行者) / reviewer(评审者) / coordinator(协调者) / observer(观察者) |
| tier | string | 否 | 角色层级：specialist(专家) / generalist(通才) / lead(领导) |

### skills 字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| required | array | 是 | 必须安装的 skills 列表 |
| optional | array | 否 | 可选的 skills 列表 |

### applicable_phases 可选值

| 值 | 说明 |
|----|------|
| plan | 规划阶段 |
| design | 设计阶段 |
| execute | 执行阶段 |
| review | 评审阶段 |
| verify | 验证阶段 |
| release | 发布阶段 |

## 角色类型说明

### executor（执行者）

负责具体执行任务的角色，如工程师、设计师等。

### reviewer（评审者）

负责评审和审核工作的角色，如架构评审员、代码评审员等。

### coordinator（协调者）

负责协调和调度的角色，如项目经理、交付总监等。

### observer（观察者）

负责监控和观察的角色，如 QA 工程师、审计员等。

## 角色层级说明

### specialist（专家）

专注于特定领域的角色，如前端专家、后端专家等。

### generalist（通才）

能够处理多种任务的全才角色。

### lead（领导）

负责领导和管理其他角色的角色。

## 示例

### delivery-director（交付总监）

```yaml
# config.yaml
name: delivery-director
display_name: 交付总监
description: 负责团队交付协调和进度管理

attributes:
  type: coordinator
  tier: lead

skills:
  required:
    - writing-plans
  optional:
    - systematic-debugging

applicable_phases:
  - plan
  - release
  - verify

capabilities:
  - 协调多角色协作
  - 管理交付进度
  - 审批关键节点
```

### architect（架构师）

```yaml
# config.yaml
name: architect
display_name: 架构师
description: 负责系统架构和技术决策

attributes:
  type: executor
  tier: specialist

skills:
  required:
    - writing-plans
    - brainstorming
  optional:
    - systematic-debugging

applicable_phases:
  - plan
  - design

capabilities:
  - 设计系统架构
  - 做技术决策
  - 评审代码架构
```

## 贡献指南

### 创建新角色

1. 在 `roles/` 目录下创建新的角色目录
2. 创建必需的文件：
   - `config.yaml` - 角色配置
   - `required_skills.txt` - 必需的 skills
   - `SKILL.md` - 角色说明
3. 运行校验确保格式正确：

```bash
python validators/validate_role.py roles/my-role
```

4. 提交 Pull Request

### 角色命名规范

- 只能包含小写字母、数字、连字符
- 必须全局唯一
- 建议使用 kebab-case（如 `fullstack-engineer`）

## 校验

使用 `validators/validate_role.py` 校验角色文件：

```bash
python validators/validate_role.py roles/delivery-director
```

## License

MIT License
