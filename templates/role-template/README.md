# 角色模板

使用此目录作为创建新角色的起点。

## 必需文件

- `config.yaml` - 角色配置
- `required_skills.txt` - 必需的 skills
- `SKILL.md` - 角色说明

## config.yaml 示例

```yaml
name: my-role
display_name: 我的角色
description: 角色描述

attributes:
  type: executor
  tier: specialist

skills:
  required:
    - skill-1
    - skill-2
  optional:
    - skill-3

applicable_phases:
  - execute
  - verify

capabilities:
  - 能力描述1
  - 能力描述2
```

## required_skills.txt 示例

```
skill-1
skill-2
```

## SKILL.md 示例

```markdown
# 我的角色

## 角色职责

描述角色的主要职责。

## 核心职责

1. 职责1
2. 职责2

## 适用场景

描述角色适用的场景。

## 工作方式

描述角色如何工作。

## 协作方式

描述角色与其他角色的协作方式。
```
