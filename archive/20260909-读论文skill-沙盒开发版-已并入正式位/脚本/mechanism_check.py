#!/usr/bin/env python3
"""读论文 skill · 机制链完整性自检（确定性逻辑，0 token）

对一篇论文页的【理解】段 B 段（机制架构），校验七环是否存在。
规则（与 知识库/机制链模板.md 对齐）：
  - 七环名称：初始条件/触发/机制1/机制2/组织中介/结果/边界条件
  - 允许环缺失，但必须明确标注"论文未说明"或 "—"，不得无标注省略
  - 输出：每环 found/missing；全部 missing 过多则告警
用法：
  python mechanism_check.py <note-论文.md>            # 校验单篇
  python mechanism_check.py <目录> --dir              # 校验目录下所有 note-*.md
返回码：0=通过，1=单篇存在缺失但已标注，2=存在未标注省略", 3=找不到B段
"""
import re
import sys
from pathlib import Path

CHAIN_LABELS = [
    ("初始条件", "Initial"),
    ("触发", "Triggering"),
    ("机制1", "M1"),
    ("机制2", "M2"),
    ("组织/过程中介", "Mediator"),
    ("结果", "Outcome"),
    ("边界条件", "Boundary"),
]

# 被认可的"缺失"标注
MISSING_MARKERS = ("论文未说明", "论文未提供", "未说明", "—", "—(无)", "[?]")


def split_chain_block(text: str):
    """从【理解】段提取 B 段。返回 B 段文本；找不到返回 None。"""
    m = re.search(r"\*\*?B\.\s*机制架构.*?(?=\n\*\*?C\.|\Z)", text, re.S)
    return m.group(0) if m else None


def check_link(block: str):
    """校验箭头链是否闭合：每对相邻环之间应有 → 。"""
    arrows = block.count("→")
    has_link = arrows >= 6
    return has_link, arrows


def check_one(text: str):
    block = split_chain_block(text)
    if not block:
        return None
    results = {}
    for label, _ in CHAIN_LABELS:
        # 该环正文：定位到环名后到下一个箭头分隔的段落头
        mc = re.search(re.escape(label), block)
        if not mc:
            results[label] = "missing_label"  # 环名都没出现 = 未标注省略
            continue
        # 取该环后续的一段文本（至下一环名或换行再换行）
        head = mc.end()
        tail = re.search(r"[（(].*?[)）]|[\n]{2,}", block[head:])
        snippet = block[head: head + (tail.start() if tail else 120)].strip()
        if any(mk in snippet for mk in MISSING_MARKERS):
            results[label] = "missing_marked"
        else:
            results[label] = "found"
    linked, arrows = check_link(block)
    return results, linked, arrows


def report(text: str, path_label: str):
    out = check_one(text)
    if out is None:
        print(f"[{path_label}] !! 未找到 B.机制架构 段")
        return 3
    results, linked, arrows = out
    status = 0
    for label, st in results.items():
        if st == "missing_label":
            status = max(status, 2)
            print(f"  - {label}: 【未标注省略】违规")
        elif st == "missing_marked":
            print(f"  - {label}: 缺失但已标注(PASS)")
        else:
            print(f"  - {label}: 已给出")
    if not linked:
        status = max(status, 2)
        print(f"  !! 箭头链未闭合，仅 {arrows} 个 '→'（需≥6）。")
    else:
        print(f"  - 箭头链闭合(PASS)，{arrows} 个 '→'。")
    if status == 0:
        print(f"[{path_label}] 通过")
    elif status == 1:
        print(f"[{path_label}] 通过(全缺失均已标注)")
    return status


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    target = Path(args[0])
    if "--dir" in args and target.is_dir():
        files = sorted(target.glob("note-*.md"))
        worst = 0
        for f in files:
            worst = max(worst, report(f.read_text(encoding="utf-8"), f.name))
        print(f"\n共 {len(files)} 篇，取最差状态 {worst}")
        return worst
    if not target.exists():
        print(f"找不到文件: {target}")
        return 3
    return report(target.read_text(encoding="utf-8"), target.name)


if __name__ == "__main__":
    sys.exit(main())