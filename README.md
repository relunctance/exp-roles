# Exp Roles
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
[![version](https://img.shields.io/badge/version--green.svg)]()
[![category](https://img.shields.io/badge/category--blue.svg)]()
[![platforms](https://img.shields.io/badge/platforms-hermes-blue.svg)]()

AI Agent 角色定义库 — 与 AI 协同打磨角色，持续进化。

## 目录结构

```
exp-roles/
├── roles/                    # 角色定义目录
│   └── {role-name}/         # 单个角色目录
│       ├── SKILL.md         # 角色详细说明
│       ├── required_skills.txt # 必需的 skills 列表
│       └── config.yaml       # 角色配置
├── schemas/                  # JSON Schema 验证文件
│   └── role.schema.json
├── validators/                # 校验工具
│   └── validate_role.py
└── templates/               # 模板文件
    └── role-template/        # 新建角色的模板
```

## 已有角色

| 角色 | 说明 | 类型 | 层级 |
|------|------|------|------|
| delivery-director | 交付总监 | coordinator | lead |
| architect | 架构师 | executor | specialist |
| fullstack-engineer | 全栈工程师 | executor | specialist |
| git-workflow-expert | Git工作流专家 | executor | specialist |

## 快速开始

### 1. 查看已有角色

```bash
ls roles/
```

### 2. 创建新角色

参考已有角色的结构：

```bash
cp -r templates/role-template roles/my-role
```

### 3. 校验角色

```bash
python validators/validate_role.py roles/my-role
```

## 角色定义规范

详见 [SCHEMA.md](./SCHEMA.md)

## 贡献指南

### 创建新角色

1. Fork 此仓库
2. 在 `roles/` 目录下创建新的角色目录
3. 创建必需的文件：
   - `config.yaml` - 角色配置
   - `required_skills.txt` - 必需的 skills
   - `SKILL.md` - 角色说明
4. 运行校验确保格式正确：

```bash
python validators/validate_role.py roles/my-role
```

5. 提交 Pull Request

### 角色命名规范

- 只能包含小写字母、数字、连字符
- 必须全局唯一
- 建议使用 kebab-case（如 `fullstack-engineer`）

## License

MIT License
