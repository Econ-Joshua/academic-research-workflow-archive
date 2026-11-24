#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_skill.py — 技能脚手架生成器（零 token 阶段）。

用法:
  python make_skill.py --name <kebab-case名> --description "<一句话+触发条件>" \
      [--when-to-use "<触发场景>"] [--body-file body.md] \
      [--script a.py --script b.sh] [--reference guide.md] \
      [--out <skills目录>] [--force]

生成:
  <out>/<name>/SKILL.md          (YAML frontmatter + 正文)
  <out>/<name>/scripts/*.py|sh   (可选)
  <out>/<name>/references/*.md   (可选)
仅使用标准库。
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

NAME_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,63}$')
TEMPLATE = """# {name}

> TODO: 一句话说明该技能解决什么问题。

## 何时使用
> TODO: 写清楚触发场景（用户说什么话、遇到什么情况时使用本技能）。

## 使用方法
> TODO: 步骤或命令。脚本调用统一写成:
> python "${{KIMI_SKILL_DIR}}/scripts/<脚本名>.py" --help

## 边界与反例
> TODO: 什么情况不该用本技能。
"""


def yaml_quote(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', "'") + '"'


def script_table(scripts):
    rows = ['| 脚本 | 运行方式 |', '|---|---|']
    for s in scripts:
        name = Path(s).name
        rows.append('| `%s` | `python "${KIMI_SKILL_DIR}/scripts/%s" --help` |' % (name, name))
    return '\n'.join(rows)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description='生成技能目录骨架(SKILL.md + scripts/ + references/)')
    ap.add_argument('--name', required=True, help='技能名, kebab-case, 如 pdf-extract-tables')
    ap.add_argument('--description', required=True, help='一句话功能+何时触发(必含触发条件)')
    ap.add_argument('--when-to-use', default=None, help='触发场景描述(Kimi frontmatter 字段)')
    ap.add_argument('--body-file', default=None, help='正文 markdown 文件(缺省用内置模板)')
    ap.add_argument('--script', action='append', default=[], help='要纳入 scripts/ 的脚本文件,可重复')
    ap.add_argument('--reference', action='append', default=[], help='要纳入 references/ 的文档,可重复')
    ap.add_argument('--out', default='skills', help='目标 skills 目录(默认 ./skills)')
    ap.add_argument('--force', action='store_true', help='覆盖已存在的同名技能目录')
    args = ap.parse_args()

    name = args.name.strip()
    if not NAME_RE.match(name):
        print('错误: 技能名必须为小写字母/数字/连字符, 2-64 字符, 收到: %r' % name, file=sys.stderr)
        sys.exit(2)
    desc = ' '.join(args.description.split())
    if len(desc) > 300:
        print('错误: description 超过 300 字符(当前 %d), 请精简' % len(desc), file=sys.stderr)
        sys.exit(2)
    if len(desc) > 200:
        print('警告: description 长度 %d, 建议压缩到 200 以内' % len(desc), file=sys.stderr)

    skill_dir = Path(args.out) / name
    if skill_dir.exists():
        if not args.force:
            print('错误: 已存在 %s, 加 --force 覆盖' % skill_dir, file=sys.stderr)
            sys.exit(2)
        shutil.rmtree(skill_dir)
    (skill_dir / 'scripts').mkdir(parents=True, exist_ok=True)
    (skill_dir / 'references').mkdir(parents=True, exist_ok=True)

    fm = ['---', 'name: %s' % name, 'description: %s' % yaml_quote(desc)]
    if args.when_to_use:
        fm.append('whenToUse: %s' % yaml_quote(' '.join(args.when_to_use.split())))
    fm.append('---')
    frontmatter = '\n'.join(fm)

    if args.body_file:
        body = Path(args.body_file).read_text(encoding='utf-8')
    else:
        body = TEMPLATE.format(name=name)

    copied_scripts = []
    for s in args.script:
        src = Path(s)
        if not src.is_file():
            print('错误: 脚本不存在: %s' % s, file=sys.stderr)
            sys.exit(2)
        shutil.copy2(src, skill_dir / 'scripts' / src.name)
        copied_scripts.append(src.name)
    copied_refs = []
    for r in args.reference:
        src = Path(r)
        if not src.is_file():
            print('错误: 参考文档不存在: %s' % r, file=sys.stderr)
            sys.exit(2)
        shutil.copy2(src, skill_dir / 'references' / src.name)
        copied_refs.append(src.name)

    parts = [frontmatter, '', body.rstrip(), '']
    if copied_scripts:
        missing = [s for s in copied_scripts if s not in body]
        if missing:
            parts.append('\n## 脚本\n\n' + script_table(copied_scripts) + '\n')
    if copied_refs:
        parts.append('\n## 参考资料\n\n' + '\n'.join(
            '- `references/%s`' % r for r in copied_refs) + '\n')

    (skill_dir / 'SKILL.md').write_text('\n'.join(parts), encoding='utf-8')

    # 清理空目录
    for sub in ('scripts', 'references'):
        d = skill_dir / sub
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()

    print('已生成技能: %s' % skill_dir)
    print('SKILL.md: %d 字符, scripts: %d 个, references: %d 个' % (
        len(body), len(copied_scripts), len(copied_refs)))
    print('安装提示: 复制到 ~/.kimi-code/skills/(用户级) 或项目内 .kimi-code/skills/(项目级); '
          '通用目录 ~/.agents/skills/ 可跨工具共享。')


if __name__ == '__main__':
    main()
