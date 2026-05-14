#!/usr/bin/env python3
"""
角色定义校验脚本

校验角色定义文件是否符合 schema 规范。
"""

import json
import sys
from pathlib import Path

import jsonschema
import yaml


def load_schema(schema_path: Path) -> dict:
    """加载 JSON Schema"""
    with open(schema_path) as f:
        return json.load(f)


def load_role(role_path: Path) -> dict:
    """加载 YAML 格式的角色配置"""
    config_file = role_path / "config.yaml"
    if not config_file.exists():
        return None
    with open(config_file) as f:
        return yaml.safe_load(f)


def validate_role(role_path: Path, schema_path: Path) -> tuple[bool, list[str]]:
    """
    校验角色定义

    Returns:
        (是否通过, 错误信息列表)
    """
    errors = []

    # 加载 schema
    try:
        schema = load_schema(schema_path)
    except Exception as e:
        return False, [f"无法加载 schema: {e}"]

    # 加载角色配置
    role = load_role(role_path)
    if role is None:
        return False, [f"角色目录中缺少 config.yaml: {role_path}"]

    # 校验
    try:
        jsonschema.validate(role, schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        message = e.message
        errors.append(f"[{path}] {message}")
    except jsonschema.SchemaError as e:
        return False, [f"Schema 错误: {e}"]

    # 额外校验：检查必需的文件是否存在
    required_files = ["config.yaml", "required_skills.txt", "SKILL.md"]
    for filename in required_files:
        file_path = role_path / filename
        if not file_path.exists():
            errors.append(f"[files] 缺少必需的文件: {filename}")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_role.py <role-path> [schema-file]")
        print("示例: python validate_role.py roles/delivery-director")
        sys.exit(1)

    role_path = Path(sys.argv[1])

    # 默认 schema 路径
    if len(sys.argv) >= 3:
        schema_path = Path(sys.argv[2])
    else:
        # 相对于脚本位置查找 schema
        script_dir = Path(__file__).parent.parent
        schema_path = script_dir / "schemas" / "role.schema.json"

    if not role_path.exists():
        print(f"❌ 角色目录不存在: {role_path}")
        sys.exit(1)

    if not schema_path.exists():
        print(f"❌ Schema 文件不存在: {schema_path}")
        sys.exit(1)

    print(f"📋 校验角色: {role_path}")
    print(f"📋 使用 Schema: {schema_path}")
    print()

    valid, errors = validate_role(role_path, schema_path)

    if valid:
        print("✅ 校验通过！")
        sys.exit(0)
    else:
        print("❌ 校验失败：")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
