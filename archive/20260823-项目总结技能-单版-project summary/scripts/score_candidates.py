#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""score_candidates.py — 对 digest 做规则评分，输出候选 shortlist（模型只读这个文件）。

用法:
  python score_candidates.py <digest1.json> [digest2.json ...] [-o shortlist.json] [--top 12]

输入: scan_project.py / parse_chat.py 产出的 digest JSON（可混合传多个）。
输出: 按分值排序的候选清单，含预览（已截断）、评分理由、类型提示。
仅使用标准库。
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

RISKY_RE = re.compile(r'rm\s+-rf|DROP\s+TABLE|format\s+[A-Za-z]:|del\s+/[sq]', re.I)
PLACEHOLDER_OK = re.compile(r'<[^>]+>|\$\{[A-Z_]+\}|your[_-]?key|xxx+|placeholder|example', re.I)


def score_code_block(i, c):
    reasons = []
    score = 0
    occ, chars = c.get('occurrences', 1), c.get('chars', 0)
    lang = str(c.get('lang', '')).lower()
    if c.get('runnable'):
        score += 5
        reasons.append('可独立运行(argparse/main/shebang)')
    else:
        score -= 2
        reasons.append('疑似代码片段(非完整程序)')
    if occ >= 2:
        score += min(occ, 5) * 3
        reasons.append('出现 %d 次(重复=高复用信号)' % occ)
    if 300 <= chars <= 8000:
        score += 2
        reasons.append('体量适中(%d 字符)' % chars)
    elif chars < 100:
        score -= 4
        reasons.append('过短(%d 字符)' % chars)
    elif chars > 20000:
        score -= 2
        reasons.append('过长(%d 字符)' % chars)
    if lang in ('python', 'py', 'sh', 'bash', 'shell', 'powershell', 'ps1'):
        score += 1
        reasons.append('脚本语言(%s)' % lang)
    if c.get('secrets'):
        penalty = -3 if PLACEHOLDER_OK.search(c.get('preview', '')) else -8
        score += penalty
        reasons.append('含疑似密钥,需脱敏' if penalty == -3 else '含疑似真实密钥,强烈建议脱敏')
    if RISKY_RE.search(c.get('preview', '')):
        score -= 3
        reasons.append('含高危命令模式')
    return score, reasons


def score_command(cmd, count):
    reasons = []
    score = min(count, 10) * 2
    reasons.append('使用 %d 次' % count)
    if not re.search(r'[/\\](home|Users)/|C:\\|https?://(?!github|pypi|npmjs)', cmd):
        score += 2
        reasons.append('不含本机路径/私有地址,通用性好')
    else:
        score -= 2
        reasons.append('含本机路径或私有地址,需泛化')
    if RISKY_RE.search(cmd):
        score -= 4
        reasons.append('含高危命令模式')
    return score, reasons


def load_digests(paths):
    digests = []
    for p in paths:
        try:
            data = json.loads(Path(p).read_text(encoding='utf-8'))
            digests.append(data)
        except (OSError, json.JSONDecodeError) as e:
            print('警告: 跳过 %s: %s' % (p, e), file=sys.stderr)
    return digests


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description='对 digest 做规则评分,输出候选 shortlist')
    ap.add_argument('digests', nargs='+', help='digest JSON 文件(scan_project/parse_chat 产出)')
    ap.add_argument('-o', '--out', default=None, help='输出 JSON 文件路径(默认打印到 stdout)')
    ap.add_argument('--top', type=int, default=12, help='保留前 N 个候选(默认 12)')
    args = ap.parse_args()

    digests = load_digests(args.digests)
    if not digests:
        print('错误: 无有效 digest 输入', file=sys.stderr)
        sys.exit(2)

    candidates = []
    context = {'languages': [], 'frameworks': [], 'project_commands': []}

    for d in digests:
        schema = d.get('schema', '')
        if schema.startswith('parse_chat'):
            for i, c in enumerate(d.get('code_blocks', [])):
                s, why = score_code_block(i, c)
                if s <= 0:
                    continue
                candidates.append({
                    'type': 'code_block',
                    'type_hint': 'script_tool' if c.get('runnable') else 'snippet',
                    'score': s,
                    'reasons': why,
                    'stats': {'occurrences': c.get('occurrences'), 'chars': c.get('chars'),
                              'lang': c.get('lang'), 'runnable': c.get('runnable'),
                              'secrets': c.get('secrets')},
                    'preview': c.get('preview', ''),
                })
            for c in d.get('commands', []):
                s, why = score_command(c['cmd'], c.get('count', 1))
                if s <= 0:
                    continue
                candidates.append({
                    'type': 'command',
                    'type_hint': 'command_snippet',
                    'score': s,
                    'reasons': why,
                    'stats': {'count': c.get('count')},
                    'preview': c['cmd'],
                })
            for ef in d.get('error_fix', []):
                if not ef.get('fix'):
                    continue
                candidates.append({
                    'type': 'error_fix',
                    'type_hint': 'pitfall_fix',
                    'score': 4,
                    'reasons': ['踩坑修复对:重新发现成本高'],
                    'stats': {},
                    'preview': ('症状: %s\n修复: %s' % (ef['error'], ef['fix']))[:400],
                })
            for it in d.get('repeated_intents', []):
                candidates.append({
                    'type': 'intent',
                    'type_hint': 'workflow',
                    'score': 3 + it.get('count', 2),
                    'reasons': ['同类请求出现 %d 次,值得沉淀为流程' % it.get('count', 2)],
                    'stats': {'count': it.get('count')},
                    'preview': it.get('text', ''),
                })
        elif schema.startswith('scan_project'):
            context['languages'].extend([l for l, _ in d.get('languages', [])[:6]])
            context['frameworks'].extend(d.get('frameworks', [])[:10])
            context['project_commands'].extend(
                [c.get('name', '') for c in d.get('commands', [])[:15]])

    candidates.sort(key=lambda x: -x['score'])
    top = candidates[:args.top]
    for c in top:
        c['preview'] = c['preview'][:400]
    context['languages'] = sorted(set(context['languages']))[:8]
    context['frameworks'] = sorted(set(context['frameworks']))[:12]

    shortlist = {
        'schema': 'shortlist/1',
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'sources': args.digests,
        'candidate_total': len(candidates),
        'kept': len(top),
        'context': context,
        'rubric': {
            'code_block': '可独立运行+5 | 重复出现 每次最多+3(封顶5次) | 体量适中+2 | 脚本语言+1 | 密钥-3~-8 | 过短-4 | 高危-3',
            'command': '频次x2(封顶10) | 通用性好+2 | 本机路径-2 | 高危-4',
            'error_fix': '固定+4(有明确修复才收录)',
            'intent': '重复>=2次 +3+次数',
        },
        'next_step': '模型逐个候选过"四问标准"(见 references/mining-guide.md),>=3个是则进入撰写阶段',
        'candidates': top,
    }
    text = json.dumps(shortlist, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print('已写入 %s (候选 %d 个, 保留 %d 个)' % (args.out, len(candidates), len(top)))
    else:
        print(text)


if __name__ == '__main__':
    main()
