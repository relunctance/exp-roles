#!/usr/bin/env python3
"""
角色定义校验脚本

校验角色定义文件是否符合 schema 规范，包括：
- JSON Schema 格式校验
- 必需文件完整性校验
- config.yaml name 与目录名一致性校验
- config.yaml skills 与 required_skills.txt 交叉校验
- required_skills.txt 格式校验（支持 source 注释）
- SKILL.md 结构校验
- skill source/url 合法性校验
"""

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml


# 合法的 source 类型
VALID_SOURCES = {"superpowers", "git"}

# 需要 url 的 source 类型
SOURCES_REQUIRING_URL = {"git"}


def load_schema(schema_path: Path) -> dict:
    """加载 JSON Schema"""
    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def load_role(role_path: Path) -> dict:
    """加载 YAML 格式的角色配置"""
    config_file = role_path / "config.yaml"
    if not config_file.exists():
        return None
    with open(config_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_required_skills(role_path: Path) -> list[dict] | None:
    """
    加载 required_skills.txt 中的 skill 列表

    支持格式:
      skill-name  # source: superpowers
      skill-name  # source: git url: https://github.com/xxx/skill

    返回 list[dict]，每个 dict 包含 name, source, url(optional)。
    如果文件不存在返回 None。
    """
    skills_file = role_path / "required_skills.txt"
    if not skills_file.exists():
        return None

    skills = []
    with open(skills_file, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 解析 skill name 和 source 注释
            skill = {"name": line, "line_num": line_num}

            # 匹配 # source: xxx [url: yyy] 注释
            comment_match = re.search(r"#\s*source:\s*(\S+)(?:\s+url:\s*(\S+))?\s*$", line)
            if comment_match:
                # skill name 是注释前面的部分
                skill["name"] = line[:comment_match.start()].strip()
                skill["source"] = comment_match.group(1)
                if comment_match.group(2):
                    skill["url"] = comment_match.group(2)

            skills.append(skill)

    return skills if skills else None


def parse_skills_from_yaml(role: dict) -> list[dict]:
    """
    从 config.yaml 中提取 skills 列表

    返回 list[dict]，每个 dict 包含 name, source, url(optional)。
    """
    if not role or not role.get("skills"):
        return []

    skills = []
    for category in ("required", "optional"):
        items = role["skills"].get(category, [])
        for item in items:
            if isinstance(item, str):
                # 兼容旧的纯字符串格式
                skills.append({"name": item})
            elif isinstance(item, dict):
                skill = {"name": item.get("name", "")}
                if "source" in item:
                    skill["source"] = item["source"]
                if "url" in item:
                    skill["url"] = item["url"]
                skills.append(skill)
    return skills


def validate_skills_txt_format(role_path: Path) -> list[str]:
    """
    校验 required_skills.txt 的格式

    检查项：
    - 文件是否为空（无有效 skill）
    - 是否有重复项
    - skill name 格式是否合法
    - source 注释格式是否合法（如果存在）
    - git source 是否包含 url
    """
    errors = []
    skills_file = role_path / "required_skills.txt"
    if not skills_file.exists():
        return errors

    skill_name_pattern = re.compile(r"^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$")

    with open(skills_file, encoding="utf-8") as f:
        lines = f.readlines()

    valid_skills = []
    seen_names = set()

    for i, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # 跳过空行和纯注释行
        if not line or line.startswith("#"):
            continue

        # 分离 skill name 和 source 注释
        comment_match = re.search(r"#\s*source:\s*(\S+)(?:\s+url:\s*(\S+))?\s*$", line)
        if comment_match:
            skill_name = line[:comment_match.start()].strip()
            source = comment_match.group(1)
            url = comment_match.group(2)
        else:
            skill_name = line
            source = None
            url = None

        # 检查 skill name 格式
        if not skill_name:
            errors.append(
                f"[required_skills.txt] 第 {i} 行: skill name 为空"
            )
            continue

        if not skill_name_pattern.match(skill_name):
            errors.append(
                f"[required_skills.txt] 第 {i} 行格式不合法: '{skill_name}'，"
                f"只能包含小写字母、数字、连字符、点和下划线"
            )

        # 检查 source 合法性
        if source and source not in VALID_SOURCES:
            errors.append(
                f"[required_skills.txt] 第 {i} 行 source 不合法: '{source}'，"
                f"只能是 {sorted(VALID_SOURCES)}"
            )

        # 检查 git source 是否有 url
        if source == "git" and not url:
            errors.append(
                f"[required_skills.txt] 第 {i} 行: source 为 git 但缺少 url"
            )

        # 检查重复
        if skill_name in seen_names:
            errors.append(
                f"[required_skills.txt] 第 {i} 行重复: '{skill_name}'"
            )
        seen_names.add(skill_name)
        valid_skills.append(skill_name)

    # 检查是否有至少一个有效 skill
    if not valid_skills:
        errors.append(
            "[required_skills.txt] 文件为空，至少需要一个有效的 skill"
        )

    return errors


def validate_name_consistency(role_path: Path, role: dict) -> list[str]:
    """
    校验 config.yaml 中的 name 字段是否与目录名一致
    """
    errors = []
    if not role or "name" not in role:
        return errors

    dir_name = role_path.name
    if role["name"] != dir_name:
        errors.append(
            f"[name] config.yaml name '{role['name']}' "
            f"与目录名 '{dir_name}' 不一致"
        )
    return errors


def validate_skills_consistency(role_path: Path, role: dict) -> list[str]:
    """
    校验 config.yaml skills 与 required_skills.txt 内容一致性

    对比 skills.required 的 skill name 列表与 required_skills.txt 中的 name。
    同时校验 source 和 url 的一致性。
    """
    errors = []
    if not role or not role.get("skills", {}).get("required"):
        return errors

    # 从 YAML 提取 required skills
    yaml_skills = role["skills"]["required"]
    yaml_names = set()
    yaml_map = {}

    for item in yaml_skills:
        if isinstance(item, str):
            name = item
            source = None
            url = None
        elif isinstance(item, dict):
            name = item.get("name", "")
            source = item.get("source")
            url = item.get("url")
        else:
            continue

        yaml_names.add(name)
        yaml_map[name] = {"source": source, "url": url}

    # 从 txt 提取 required skills
    txt_skills = load_required_skills(role_path)
    if txt_skills is None:
        return errors

    txt_names = set()
    txt_map = {}

    for skill in txt_skills:
        name = skill["name"]
        txt_names.add(name)
        txt_map[name] = {
            "source": skill.get("source"),
            "url": skill.get("url"),
        }

    # 检查 name 一致性
    if yaml_names != txt_names:
        missing_in_txt = yaml_names - txt_names
        extra_in_txt = txt_names - yaml_names
        if missing_in_txt:
            errors.append(
                f"[skills] config.yaml 中有但 required_skills.txt 缺少: "
                f"{sorted(missing_in_txt)}"
            )
        if extra_in_txt:
            errors.append(
                f"[skills] required_skills.txt 中有但 config.yaml 缺少: "
                f"{sorted(extra_in_txt)}"
            )

    # 检查 source 一致性（仅对两边都有的 skill）
    common_names = yaml_names & txt_names
    for name in common_names:
        yaml_source = yaml_map[name]["source"]
        txt_source = txt_map[name]["source"]
        if yaml_source != txt_source:
            errors.append(
                f"[skills] skill '{name}' source 不一致: "
                f"config.yaml='{yaml_source}', required_skills.txt='{txt_source}'"
            )

    return errors


def validate_skill_md_structure(role_path: Path, role: dict) -> list[str]:
    """
    校验 SKILL.md 的基本结构

    检查项：
    - 文件大小（至少 100 字节，避免空壳文件）
    - 包含必需章节标题
    """
    errors = []
    skill_file = role_path / "SKILL.md"
    if not skill_file.exists():
        return errors

    # 检查文件大小
    size = skill_file.stat().st_size
    if size < 100:
        errors.append(
            f"[SKILL.md] 文件过小 ({size} 字节)，至少应包含 100 字节的内容"
        )
        return errors

    # 检查必需章节
    required_sections = ["角色职责", "适用场景", "工作方式", "协作方式", "约束和限制"]
    content = skill_file.read_text(encoding="utf-8")

    for section in required_sections:
        pattern = re.compile(rf"^#{{2,3}}\s+.*{re.escape(section)}", re.MULTILINE)
        if not pattern.search(content):
            errors.append(
                f"[SKILL.md] 缺少必需章节: '{section}'"
            )

    return errors


def validate_skill_sources(role: dict) -> list[str]:
    """
    校验 config.yaml 中所有 skill 的 source 和 url 合法性

    检查项：
    - source 值是否合法
    - source 为 git 时是否提供 url
    """
    errors = []
    if not role or not role.get("skills"):
        return errors

    for category in ("required", "optional"):
        items = role["skills"].get(category, [])
        for i, item in enumerate(items):
            if isinstance(item, str):
                # 旧格式：缺少 source 字段
                errors.append(
                    f"[skills.{category}] 第 {i + 1} 项 '{item}' 使用了旧格式，"
                    f"需要改为对象格式并指定 source"
                )
                continue

            if not isinstance(item, dict):
                errors.append(
                    f"[skills.{category}] 第 {i + 1} 项格式错误，应为对象"
                )
                continue

            name = item.get("name", "")
            source = item.get("source")

            # 检查 source 是否存在
            if not source:
                errors.append(
                    f"[skills.{category}] skill '{name}' 缺少 source 字段"
                )
                continue

            # 检查 source 值合法性
            if source not in VALID_SOURCES:
                errors.append(
                    f"[skills.{category}] skill '{name}' source 不合法: '{source}'，"
                    f"只能是 {sorted(VALID_SOURCES)}"
                )
                continue

            # 检查 git source 是否有 url
            if source == "git" and not item.get("url"):
                errors.append(
                    f"[skills.{category}] skill '{name}' source 为 git 但缺少 url"
                )

            # 检查非 git source 不应有 url
            if source != "git" and item.get("url"):
                errors.append(
                    f"[skills.{category}] skill '{name}' source 为 '{source}' "
                    f"不应包含 url"
                )

    return errors


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

    # JSON Schema 校验
    try:
        jsonschema.validate(role, schema)
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        message = e.message
        errors.append(f"[{path}] {message}")
    except jsonschema.SchemaError as e:
        return False, [f"Schema 错误: {e}"]

    # 必需文件完整性校验
    required_files = ["config.yaml", "required_skills.txt", "SKILL.md"]
    for filename in required_files:
        file_path = role_path / filename
        if not file_path.exists():
            errors.append(f"[files] 缺少必需的文件: {filename}")

    # name 与目录名一致性校验
    errors.extend(validate_name_consistency(role_path, role))

    # skill source/url 合法性校验
    errors.extend(validate_skill_sources(role))

    # skills.required 与 required_skills.txt 一致性校验
    errors.extend(validate_skills_consistency(role_path, role))

    # required_skills.txt 格式校验
    errors.extend(validate_skills_txt_format(role_path))

    # SKILL.md 结构校验
    errors.extend(validate_skill_md_structure(role_path, role))

    return len(errors) == 0, errors


def validate_all_roles(project_root: Path, schema_path: Path | None = None) -> tuple[int, int]:
    """
    校验所有角色

    Returns:
        (通过数量, 失败数量)
    """
    if schema_path is None:
        schema_path = project_root / "schemas" / "role.schema.json"

    roles_dir = project_root / "roles"
    if not roles_dir.exists():
        print(f"❌ 角色目录不存在: {roles_dir}")
        return 0, 0

    role_dirs = sorted(
        d for d in roles_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    if not role_dirs:
        print("⚠️ 未找到任何角色目录")
        return 0, 0

    passed = 0
    failed = 0

    for role_dir in role_dirs:
        valid, errors = validate_role(role_dir, schema_path)
        if valid:
            print(f"  ✅ {role_dir.name}")
            passed += 1
        else:
            print(f"  ❌ {role_dir.name}")
            for error in errors:
                print(f"     - {error}")
            failed += 1

    return passed, failed


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_role.py <role-path> [schema-file]")
        print("      python validate_role.py --all [project-root]")
        print("示例: python validate_role.py roles/delivery-director")
        print("      python validate_role.py --all")
        sys.exit(1)

    # 全量校验模式
    if sys.argv[1] == "--all":
        if len(sys.argv) >= 3:
            project_root = Path(sys.argv[2])
        else:
            project_root = Path(__file__).parent.parent

        schema_path = project_root / "schemas" / "role.schema.json"
        if not schema_path.exists():
            print(f"❌ Schema 文件不存在: {schema_path}")
            sys.exit(1)

        print(f"📋 全量校验角色: {project_root / 'roles'}")
        print(f"📋 使用 Schema: {schema_path}")
        print()

        passed, failed = validate_all_roles(project_root, schema_path)

        print()
        print(f"结果: {passed} 通过, {failed} 失败")
        sys.exit(0 if failed == 0 else 1)

    # 单角色校验模式
    role_path = Path(sys.argv[1])

    if len(sys.argv) >= 3:
        schema_path = Path(sys.argv[2])
    else:
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
