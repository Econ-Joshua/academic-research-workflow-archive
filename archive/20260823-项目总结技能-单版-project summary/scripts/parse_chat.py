#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_chat.py — 解析对话导出文件（JSON / JSONL / Markdown / TXT），提取可复用信号。

用法:
  python parse_chat.py <文件1> [文件2 ...] [-o digest_chat.json]

提取内容:
  - 代码块（去重 + 出现频次 + 是否可独立运行 + 疑似密钥标记）
  - 高频 shell 命令
  - 报错→修复 配对（近似配对）
  - 重复出现的用户意图（可复用需求的信号）
仅使用标准库。
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

CODE_FENCE = re.compile(r'```([\w+#.-]*)[ \t]*\r?\n(.*?)```', re.S)
ROLE_LINE = re.compile(          # "用户：" / "**User**:" 这类带冒号的角色行
    r'^\s*(?:#{1,4}\s*)?(?:\*\*)?\s*'
    r'(User|Human|用户|我|Assistant|AI|Bot|助手|System|系统|Tool|工具)'
    r'(?:\*\*)?\s*[:：]\s*(.*)$'
)
ROLE_HEADER = re.compile(        # 整行只有角色词，如 "## User" / "**Assistant**"
    r'^\s*(?:#{1,4}\s*)?\*{0,2}\s*'
    r'(User|Human|用户|Assistant|AI|Bot|助手|System|系统|Tool|工具)'
    r'\s*\*{0,2}\s*$'
)
ROLE_MAP = {
    'user': 'user', 'human': 'user', '用户': 'user', '我': 'user',
    'assistant': 'assistant', 'ai': 'assistant', 'bot': 'assistant', '助手': 'assistant',
    'system': 'system', '系统': 'system', 'tool': 'tool', '工具': 'tool',
}
CMD_RE = re.compile(
    r'^\s*(?:[$>]\s*)?(git|npm|npx|yarn|pnpm|pip3?|python3?|py|node|uv|uvicorn|conda|'
    r'docker|docker-compose|kubectl|make|cargo|go|mvn|gradle|curl|wget|ssh|scp|rsync|'
    r'tar|unzip|chmod|ffmpeg|adb|powershell|pwsh|bash|zsh|brew|apt|apt-get|choco)\b.*$'
)
ERR_RE = re.compile(
    r'(Traceback|Error|ERROR|Exception|FATAL|failed|Failed|FAILED|exit code [1-9]|'
    r'command not found|not recognized|Permission denied|ECONNREFUSED|EACCES|'
    r'报错|失败|无法|找不到|无法找到)'
)
RUNNABLE_RE = re.compile(
    r'(^\s*#!|argparse|sys\.argv|def main\(|async def main\(|if __name__|'
    r'add_argument|click\.command|function main|typer\.run)'
)
SECRET_RE = re.compile(
    r'(?i)(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|'
    r'(api[_-]?key|secret|token|password)\s*[=:]\s*["\'][A-Za-z0-9_\-]{12,})'
)


def norm_role(r):
    return ROLE_MAP.get(str(r).strip().lower(), ROLE_MAP.get(str(r).strip(), 'other'))


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict):
                t = c.get('text') or c.get('content') or ''
                if isinstance(t, str):
                    parts.append(t)
        return '\n'.join(parts)
    if isinstance(content, dict):
        return content.get('text') or content.get('content') or ''
    return ''


def find_json_messages(obj, out):
    if isinstance(obj, dict):
        role = obj.get('role') or obj.get('from') or obj.get('author') or obj.get('speaker')
        content = obj.get('content')
        if content is None:
            content = obj.get('parts') or obj.get('text') or obj.get('message')
        if role is not None and content is not None:
            t = text_of(content)
            if t.strip():
                out.append((norm_role(role), t))
        for v in obj.values():
            if isinstance(v, (dict, list)):
                find_json_messages(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_json_messages(v, out)


def load_messages(path):
    p = Path(path)
    raw = p.read_text(encoding='utf-8', errors='ignore')
    msgs = []
    if p.suffix.lower() == '.json':
        try:
            find_json_messages(json.loads(raw), msgs)
            if msgs:
                return msgs
        except json.JSONDecodeError:
            pass
    if p.suffix.lower() in ('.jsonl', '.json') or not msgs:
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                find_json_messages(json.loads(line), msgs)
            except json.JSONDecodeError:
                continue
        if msgs:
            return msgs
    # Markdown / TXT：按角色标题行切分
    role, buf = 'other', []

    def flush():
        if buf:
            body = '\n'.join(buf)
            if body.strip():
                msgs.append((role, body))
            buf.clear()

    for line in raw.splitlines():
        m = ROLE_LINE.match(line)
        h = None if m else ROLE_HEADER.match(line)
        if m or h:
            flush()  # 先用旧角色落盘缓冲内容
            role = norm_role((m or h).group(1))
            if m:
                rest = m.group(2).strip().strip('*').strip()  # 处理 "**User: 内容**" 的尾星号
                if rest:
                    msgs.append((role, rest))
        else:
            buf.append(line)
    flush()
    return msgs


def analyze(messages):
    stats = Counter(r for r, _ in messages)
    code_blocks = OrderedDict()   # hash -> dict
    commands = Counter()
    user_intents = Counter()
    intent_text = {}
    err_events = []               # (idx, kind, text)

    cond_lines = []               # 压缩后的行流：代码块折叠为单行 token，用于报错配对
    for role, text in messages:
        blocks_in_msg = []
        for m in CODE_FENCE.finditer(text):
            lang = (m.group(1) or '').lower()
            body = m.group(2)
            h = hashlib.md5('\n'.join(l.rstrip() for l in body.splitlines()
                                      if l.strip()).encode('utf-8')).hexdigest()
            item = code_blocks.get(h)
            if item is None:
                code_blocks[h] = {
                    'lang': lang or '(未标注)',
                    'occurrences': 1,
                    'chars': len(body),
                    'runnable': bool(RUNNABLE_RE.search(body)),
                    'secrets': bool(SECRET_RE.search(body)),
                    'preview': body[:300],
                    'first_role': role,
                }
            else:
                item['occurrences'] += 1
            blocks_in_msg.append((h, lang, body))
        # 折叠文本：把代码块替换为占位 token，避免代码内容被当作普通行分析
        folded = CODE_FENCE.sub('⟦CODE_BLOCK⟧', text)
        for line in folded.splitlines():
            cond_lines.append((role, line, blocks_in_msg))
        if role == 'user':
            t = text.strip()
            if len(t) >= 6:
                key = re.sub(r'\s+', '', t.lower())[:60]
                user_intents[key] += 1
                intent_text.setdefault(key, t[:80])

    err_fix = []
    for i, (role, line, msg_blocks) in enumerate(cond_lines):
        bare = re.sub(r'^\s*(?:\d+[.).、]|[•*\-·>+]+)\s+', '', line)  # 去掉编号/项目符号前缀
        if CMD_RE.match(bare):
            cmd = bare.strip()[:120]
            commands[cmd] += 1
        if ERR_RE.search(line) and len(err_fix) < 60:
            fix = ''
            for j in range(i + 1, min(i + 13, len(cond_lines))):
                r2, l2, mb2 = cond_lines[j]
                if '⟦CODE_BLOCK⟧' in l2 and mb2:
                    fix = '代码块: ' + (mb2[0][2][:140] if mb2[0][2] else '')
                    break
                if CMD_RE.match(re.sub(r'^\s*(?:\d+[.).、]|[•*\-·>+]+)\s+', '', l2)):
                    fix = l2.strip()[:140]
                    break
            err_fix.append({'error': line.strip()[:160], 'fix': fix})

    cb_list = sorted(code_blocks.values(), key=lambda x: -x['occurrences'])[:25]
    for c in cb_list:
        c['preview'] = c['preview'][:300]
    dedup = len(code_blocks)
    intents = [{'text': intent_text[k], 'count': v}
               for k, v in user_intents.most_common(20) if v >= 1][:20]
    return {
        'schema': 'parse_chat/1',
        'stats': {
            'messages_by_role': dict(stats),
            'total_messages': len(messages),
            'code_blocks_total': sum(c['occurrences'] for c in code_blocks.values()),
            'code_blocks_dedup': dedup,
        },
        'code_blocks': cb_list,
        'commands': [{'cmd': c, 'count': n} for c, n in commands.most_common(30)],
        'error_fix': err_fix[:15],
        'user_intents': intents,
        'repeated_intents': [i for i in intents if i['count'] >= 2][:10],
    }


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description='解析对话导出文件，提取可复用信号')
    ap.add_argument('files', nargs='+', help='对话导出文件（json/jsonl/md/txt，可多个）')
    ap.add_argument('-o', '--out', default=None, help='输出 JSON 文件路径（默认打印到 stdout）')
    args = ap.parse_args()

    all_msgs = []
    files_used = []
    for f in args.files:
        try:
            msgs = load_messages(f)
            all_msgs.extend(msgs)
            files_used.append({'file': f, 'messages': len(msgs)})
        except OSError as e:
            print('警告: 无法读取 %s: %s' % (f, e), file=sys.stderr)
    if not all_msgs:
        print('错误: 未解析到任何消息，请检查文件格式', file=sys.stderr)
        sys.exit(2)

    digest = analyze(all_msgs)
    digest['files'] = files_used
    text = json.dumps(digest, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print('已写入 %s (%d 条消息, %d 个去重代码块)' % (
            args.out, len(all_msgs), digest['stats']['code_blocks_dedup']))
    else:
        print(text)


if __name__ == '__main__':
    main()
