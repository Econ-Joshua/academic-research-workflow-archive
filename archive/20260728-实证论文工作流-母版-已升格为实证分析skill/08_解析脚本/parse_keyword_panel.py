# -*- coding: utf-8 -*-
"""
上市公司年报 MD&A 文本三层关键词交乘识别（通用版）

方法论（固化）：
  技术词 × 场景词 × 实施动词 三层交乘：
    - 句子切分（[。！？；\\n]+）；
    - 在 WINDOW 邻近句窗口内要求技术词与场景词共现；
    - 窗口内命中实施动词的触发句权重 w_verb，无动词权重 w_noverb；
    - 排除规则引擎：每条正则命中触发句即剔除该句；
    - 纯英文/数字词自动加 (?<![A-Za-z0-9])...(?![A-Za-z0-9]) 词边界。
  词表与排除规则为课题专属数据资产，全部通过参数传入，脚本不含任何领域词。

用法示例（数据源地址一律留空，使用时自行填写）：
  python parse_keyword_panel.py \
      --texts-dir "【自填：年报/MD&A 文本根目录】 " \
      --wordlist "【自填：词表.csv】" \
      --exclude-rules "【自填：排除规则.csv，可选】" \
      --year 2022 --start 0 --end 5120 \
      --out 输出/shard_2022_0_5120.csv

文本目录默认结构（仅为一种常见布局，换数据源时须核对并用 --pattern 覆盖）：
  {texts-dir}/{year}/文本/{股票代码}_{year}-12-31.txt
可用 --pattern 覆盖文件匹配模板（{year} 会被替换）。
"""
import argparse
from pathlib import Path

import pandas as pd
import re

SENT_SPLIT = re.compile(r"[。！？；\n]+")
CE_CHAR = re.compile(r"[一-鿿A-Za-z]")

CATEGORIES = ["技术词", "场景词", "实施动词"]


def load_words(wordlist_path):
    """读取三类词表 CSV（至少含列：类别、关键词；允许多余列）。"""
    wl = pd.read_csv(wordlist_path, encoding="utf-8-sig")
    for col in ("类别", "关键词"):
        if col not in wl.columns:
            raise ValueError(f"词表缺少必需列: {col}（现有列: {list(wl.columns)}）")
    cats = {}
    for c in CATEGORIES:
        words = wl.loc[wl["类别"] == c, "关键词"].dropna().astype(str).str.strip()
        cats[c] = [w for w in words if w]
    missing = [c for c, ws in cats.items() if not ws]
    if missing:
        raise ValueError(f"词表中以下类别为空: {missing}（类别取值须为 {CATEGORIES}）")
    return cats


def load_kill_res(exclude_path):
    """读取排除规则 CSV（两列：name、regex；每行一条正则，命中即剔除触发句）。"""
    if not exclude_path:
        return []
    er = pd.read_csv(exclude_path, encoding="utf-8-sig")
    for col in ("name", "regex"):
        if col not in er.columns:
            raise ValueError(f"排除规则文件缺少必需列: {col}（现有列: {list(er.columns)}）")
    res = []
    for _, row in er.iterrows():
        pat = str(row["regex"]).strip()
        if pat and pat.lower() != "nan":
            res.append(re.compile(pat))
    return res


def build_regex(words):
    """长词优先；纯英文/数字词加拉丁词边界，避免 AIPC 误中 AI 等。"""
    parts = []
    for w in sorted(set(words), key=len, reverse=True):
        esc = re.escape(w)
        if re.fullmatch(r"[A-Za-z0-9]+", w):
            parts.append(r"(?<![A-Za-z0-9])" + esc + r"(?![A-Za-z0-9])")
        else:
            parts.append(esc)
    return re.compile("|".join(parts)) if parts else None


def read_text(path):
    for enc in ("utf-8", "gb18030"):
        try:
            return path.read_text(encoding=enc, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def count_hits(regex, s):
    return len(regex.findall(s)) if regex else 0


def parse_file(text, tech_re, scen_re, verb_re, kill_res, window, w_verb, w_noverb):
    chars_total = len(text)
    chars_ce = len(CE_CHAR.findall(text))
    out = {"chars_total": chars_total, "chars_ce": chars_ce, "n_sent": 0,
           "valid_ctx": 0, "tech_hits_w": 0.0, "scen_hits_w": 0.0,
           "verb_hits_w": 0.0, "freq_sum": 0.0,
           "raw_tech": count_hits(tech_re, text),
           "raw_scen": count_hits(scen_re, text),
           "raw_verb": count_hits(verb_re, text)}
    if not tech_re.search(text):
        return out
    sents = [s for s in SENT_SPLIT.split(text) if s.strip()]
    n = len(sents)
    out["n_sent"] = n
    scen_cnt = [count_hits(scen_re, s) for s in sents]
    verb_cnt = [count_hits(verb_re, s) for s in sents]
    for i, s in enumerate(sents):
        tech_n = count_hits(tech_re, s)
        if not tech_n:
            continue
        if any(r.search(s) for r in kill_res):
            continue
        lo, hi = max(0, i - window), min(n, i + window + 1)
        scen_win = sum(scen_cnt[lo:hi])
        if scen_win == 0:
            continue
        verb_win = sum(verb_cnt[lo:hi])
        w = w_verb if verb_win > 0 else w_noverb
        out["valid_ctx"] += 1
        out["tech_hits_w"] += w * tech_n
        out["scen_hits_w"] += w * scen_win
        out["verb_hits_w"] += w * verb_win
        out["freq_sum"] += w * (tech_n + scen_win + verb_win)
    return out


def main():
    ap = argparse.ArgumentParser(description="MD&A 三层关键词交乘词频面板构建")
    ap.add_argument("--texts-dir", required=True,
                    help="年报文本根目录，默认结构 {texts-dir}/{year}/文本/*_{year}-12-31.txt")
    ap.add_argument("--wordlist", required=True,
                    help="三类词表 CSV（列：类别、关键词；类别 ∈ 技术词/场景词/实施动词）")
    ap.add_argument("--exclude-rules", default=None,
                    help="可选：排除规则 CSV（列：name、regex；每行一条正则，命中即剔除触发句）")
    ap.add_argument("--pattern", default="*_{year}-12-31.txt",
                    help="年份目录下的文件匹配模板，{year} 会被替换")
    ap.add_argument("--texts-subdir", default="文本",
                    help="年份目录下的文本子目录名，默认 文本；设为空串表示直接在年份目录下")
    ap.add_argument("--window", type=int, default=2, help="邻近句共现窗口，默认 2")
    ap.add_argument("--w-verb", type=float, default=1.0, help="命中实施动词权重，默认 1.0")
    ap.add_argument("--w-noverb", type=float, default=0.5, help="无实施动词权重，默认 0.5")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cats = load_words(args.wordlist)
    kill_res = load_kill_res(args.exclude_rules)
    tech_re = build_regex(cats["技术词"])
    scen_re = build_regex(cats["场景词"])
    verb_re = build_regex(cats["实施动词"])
    print(f"词表: 技术词 {len(cats['技术词'])} | 场景词 {len(cats['场景词'])} | "
          f"实施动词 {len(cats['实施动词'])} | 排除规则 {len(kill_res)} 条", flush=True)

    base = Path(args.texts_dir) / str(args.year)
    tdir = base / args.texts_subdir if args.texts_subdir else base
    files = sorted(tdir.glob(args.pattern.format(year=args.year)))
    files = files[:args.limit] if args.limit else files[args.start:args.end]
    print(f"{args.year}: 本任务处理 {len(files)} 份", flush=True)

    rows = []
    for k, f in enumerate(files):
        r = parse_file(read_text(f), tech_re, scen_re, verb_re, kill_res,
                       args.window, args.w_verb, args.w_noverb)
        r["code"], r["t"] = f.name.split("_")[0], args.year
        rows.append(r)
        if (k + 1) % 1000 == 0:
            print(f"  进度 {k + 1}/{len(files)}", flush=True)

    df = pd.DataFrame(rows)
    # 中文列名输出面板
    colmap = {
        "code": "股票代码", "t": "年份",
        "freq_sum": "加权词频",
        "raw_tech": "技术词原始命中数", "raw_scen": "场景词命中数",
        "raw_verb": "实施动词原始命中数",
        "valid_ctx": "触发句数",
        "tech_hits_w": "加权技术词命中数", "scen_hits_w": "加权场景词命中数",
        "verb_hits_w": "加权实施动词命中数",
        "chars_total": "文本字符数", "chars_ce": "中英字符数",
        "n_sent": "句子数",
    }
    df = df.rename(columns=colmap)
    front = ["股票代码", "年份", "加权词频", "技术词原始命中数", "场景词命中数",
             "触发句数", "文本字符数"]
    df = df[front + [c for c in df.columns if c not in front]]

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outp, index=False, encoding="utf-8-sig")
    nz = (df["加权词频"] > 0).mean() if len(df) else 0.0
    print(f"  完成: {len(df)} 行 | 加权词频>0 占比 {nz:.1%} | {outp}", flush=True)


if __name__ == "__main__":
    main()
