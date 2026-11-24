#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_skill.py — 校验技能目录是否合格（零 token 阶段，必须 PASS 才交付）。

用法:
  python validate_skill.py <技能目录>

检查项:
  [ERROR] SKILL.md 存在且含合法 frontmatter(name+description 必填)
  [ERROR] name 为 kebab-case 且与目录名一致
  [ERROR] 密钥/凭据泄漏扫描(SKILL.md + scripts + references)
  [ERROR] Python 脚本语法可编译
  [WARN ] description 过长 / 缺触发条件 / 正文过短 / 残留本机路径 / 未声明脚本用法
退出码: 0=PASS, 1=存在 ERROR。仅使用标准库。
"""
import re
import subprocess
import sys
from pathlib import Path

NAME_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,63}$')
TRIGGER_RE = re.compile(r'(when|invoke|使用|触发|何时|当|遇到|适用)', re.I)
SECRET_PATTERNS = [
    (re.compile(r'sk-[A-Za-z0-9]{16,}'), 'OpenAI 风格密钥'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS AccessKey'),
    (re.compile(r'ghp_[A-Za-z0-9]{20,}'), 'GitHub token'),
    (re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'), 'Slack token'),
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'), '私钥文件'),
    (re.compile(r'(?i)(api[_-]?key|secret|token|passwd|password)\s*[=:]\s*["\'][A-Za-z0-9_\-./+]{16,}["\']'), '凭据赋值'),
]
PLACEHOLDER_OK = re.compile(
    r'(<[^>]+>|\$\{[A-Z_]+\}|your[_-]?|xxx+|placeholder|example|<your[_-]?key>|ENV|getenv)', re.I)
USER_PATH_RE = re.compile(r'[A-Za-z]:\\Users\\[^\\\s]+|/(home|Users)/[a-z][^\s/\]]*', re.I)


class Report:
    def __init__(self):
        self.errors, self.warns = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)


def parse_frontmatter(text):
    if not text.startswith('---'):
        return None, '缺少 frontmatter(文件须以 --- 开头)'
    end = text.find('\n---', 3)
    if end < 0:
        return None, 'frontmatter 未闭合(缺少结束 ---)'
    block = text[3:end]
    meta = {}
    for line in block.splitlines():
        m = re.match(r'^([A-Za-z_-]+)\s*:\s*(.*)$', line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"\'')
    return meta, None


def scan_secrets(paths, rep):
    hits = 0
    for p in paths:
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for rx, label in SECRET_PATTERNS:
                m = rx.search(line)
                if m and not PLACEHOLDER_OK.search(m.group(0)):
                    rep.error('疑似密钥泄漏[%s]: %s 第%d行: %s...' % (
                        label, p.name, line_no, line.strip()[:60]))
                    hits += 1
                    break
    return hits


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    if len(sys.argv) != 2:
        print('用法: python validate_skill.py <技能目录>', file=sys.stderr)
        sys.exit(2)
    skill_dir = Path(sys.argv[1]).resolve()
    rep = Report()

    if not skill_dir.is_dir():
        print('FAIL: 不是有效目录: %s' % skill_dir, file=sys.stderr)
        sys.exit(1)

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.is_file():
        print('FAIL: 缺少 SKILL.md', file=sys.stderr)
        sys.exit(1)
    text = skill_md.read_text(encoding='utf-8', errors='ignore')

    meta, err = parse_frontmatter(text)
    if err:
        rep.error('frontmatter: %s' % err)
        meta = {}
    name = meta.get('name', '')
    desc = meta.get('description', '')
    when = meta.get('whenToUse') or meta.get('when-to-use') or meta.get('when_to_use') or ''

    if not name:
        rep.error('frontmatter 缺少 name')
    elif not NAME_RE.match(name):
        rep.error('name 不符合 kebab-case: %r' % name)
    elif name.lower() != skill_dir.name.lower():
        rep.warn('name(%s) 与目录名(%s)不一致' % (name, skill_dir.name))
    if not desc:
        rep.error('frontmatter 缺少 description')
    else:
        if len(desc) > 300:
            rep.error('description 超过 300 字符(当前 %d)' % len(desc))
        elif len(desc) > 200:
            rep.warn('description 长度 %d, 建议压缩到 200 以内' % len(desc))
        if not TRIGGER_RE.search(desc) and not when:
            rep.warn('description/whenToUse 未体现触发条件, 模型将难以自动调用')

    body_start = text.find('\n---', 3)
    body = text[body_start + 4:] if text.startswith('---') and body_start >= 0 else text
    if len(body.strip()) < 200:
        rep.warn('正文过短(%d 字符), 至少应说明做什么/何时用/怎么用' % len(body.strip()))

    all_files = [skill_md]
    for sub in ('scripts', 'references'):
        d = skill_dir / sub
        if d.is_dir():
            all_files.extend(p for p in d.rglob('*') if p.is_file())
    py_scripts = [p for p in all_files if p.suffix == '.py']
    sh_scripts = [p for p in all_files if p.suffix == '.sh']

    scan_secrets(all_files, rep)

    for p in py_scripts:
        try:
            compile(p.read_text(encoding='utf-8', errors='ignore'), str(p), 'exec')
        except SyntaxError as e:
            rep.error('Python 语法错误: %s 第%d行: %s' % (p.name, e.lineno or 0, e.msg))
    for p in sh_scripts:
        r = subprocess.run(['bash', '-n', str(p)], capture_output=True)
        if r.returncode != 0:
            rep.error('Shell 语法错误: %s: %s' % (p.name, r.stderr.decode('utf-8', 'ignore')[:100]))

    if py_scripts or sh_scripts:
        for p in py_scripts + sh_scripts:
            if p.name not in text:
                rep.warn('正文未提及脚本 %s 的用法' % p.name)
                break

    for p in all_files:
        try:
            t = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        m = USER_PATH_RE.search(t)
        if m and '...' not in m.group(0):  # 含省略号的多为文档示例，跳过
            rep.warn('%s 残留本机用户路径: %s (建议用 <PROJECT_DIR> 等占位符)' % (p.name, m.group(0)[:60]))
            break

    print('检查目录: %s' % skill_dir)
    for w in rep.warns:
        print('  [WARN ] %s' % w)
    for e in rep.errors:
        print('  [ERROR] %s' % e)
    if rep.errors:
        print('结果: FAIL (%d 个错误, %d 个警告)' % (len(rep.errors), len(rep.warns)))
        sys.exit(1)
    print('结果: PASS (%d 个警告)' % len(rep.warns))
    sys.exit(0)


if __name__ == '__main__':
    main()
