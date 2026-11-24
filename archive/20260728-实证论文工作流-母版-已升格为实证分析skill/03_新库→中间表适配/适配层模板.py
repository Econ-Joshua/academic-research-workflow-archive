# -*- coding: utf-8 -*-
"""
适配层模板：新专利数据库 → 标准中间表（patents.csv + citations.csv）

⚠️ 本文件是【一次性适配层】骨架：每换一个专利数据库，复制本模板改写。
   数据源地址一律留空自填，不要在模板里写死路径（工作流规则）。

输出 schema（与 02_中间表→指标计算/knowledge_indicators.py 严格对齐）：
  patents  : patent_id, group_id, app_year(int), main_ipc4(str), is_invention(bool)
  citations: citing_id, cited_ipc4(str,可NaN), cited_in_group(bool),
             cited_app_year(int,可NaN), is_valid(bool)

使用前必读：01_指标定义+构造约定+质量清单/references/indicator-definitions.md
  —— 产出中间表后，先按其中"数据质量清单"做收录诊断，再进入 02 计算指标。

用法：
  python 适配层模板.py --raw-dir "【自填：原始数据目录】" --out-dir ./
"""
import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

# ============ 【自填区 1】原始数据字段映射 ============
# 把右侧标准列名映射到原始库的实际列名（按新库文档填写，None 表示该列不存在）
COLMAP = {
    "patent_id": None,      # 专利号/申请号
    "applicant": None,      # 申请人名称（可能一格多人，需拆分）
    "group_id": None,       # 关联上市公司代码（无标准化ID时以关联股票代码为准）
    "app_year": None,       # 申请年（或申请日，需取年份）
    "ipc": None,            # IPC 分类号（取主分类前 4 位）
    "patent_type": None,    # 专利类型（用于识别发明专利）
    # —— 引用相关（若引用关系在另一张表，见 build_citations 注释）——
    "citing_id": None,      # 引用方专利号
    "cited_id": None,       # 被引专利号
    "cite_type": None,      # 引用类型（如 X/Y/A/L，有效性规则见下）
}
# 有效引用类型（按新库的引用类型体系填写；上一套库的经验：X/Y/A/L 等多类型并存）
VALID_CITE_TYPES = []       # 【自填】如 ["X", "Y", "A", "L"]
INVENTION_KEYWORDS = ["发明"]  # 【自填】patent_type 中识别发明专利的依据（注意排除"实用新型"）


# ============ 【自填区 2】读取原始数据 ============
def load_raw(raw_dir: Path) -> pd.DataFrame:
    """按新库的实际组织方式读取并合并（分年份文件/单大表/数据库连接均可）。"""
    files = sorted(raw_dir.glob("*.csv"))   # 【按实际改】可能是 csv/dta/parquet/分年份目录
    if not files:
        raise FileNotFoundError(f"{raw_dir} 下未找到数据文件，请检查 --raw-dir")
    return pd.concat([pd.read_csv(f, encoding="utf-8-sig", low_memory=False)
                      for f in files], ignore_index=True)


# ============ 专利表：多申请人展开 + 字段标准化 ============
def build_patents(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.rename(columns={v: k for k, v in COLMAP.items()
                             if v and k in ("patent_id", "applicant", "group_id",
                                            "app_year", "ipc", "patent_type")})
    # 1) 申请年：若原始是日期，改取年份
    if df["app_year"].dtype == object:
        df["app_year"] = pd.to_datetime(df["app_year"], errors="coerce").dt.year
    df["app_year"] = df["app_year"].astype("Int64")

    # 2) 主 IPC 四位：取主分类号前 4 位（如 G06F17/30 → G06F）
    df["main_ipc4"] = (df["ipc"].astype(str).str.strip()
                       .str.split().str[0].str[:4].str.upper())

    # 3) 发明专利标记
    df["is_invention"] = (df["patent_type"].astype(str)
                          .apply(lambda s: any(k in s for k in INVENTION_KEYWORDS)
                                 and "实用新型" not in s))

    # 4) 多申请人展开：同一专利每个申请人集团各自分别计（构造约定，勿删）
    #    【按实际改】申请人分隔符可能是 ;、；、| 等
    df["applicant"] = df["applicant"].astype(str).str.split(r"[;；|]")
    df = df.explode("applicant")
    df["applicant"] = df["applicant"].str.strip()

    # 5) group_id：若原始库只有申请人名称没有股票代码，需在此与
    #    "申请人-上市公司关联表"合并（【自填】关联表来源）；已有代码则直接标准化
    df["group_id"] = df["group_id"].astype(str).str.strip()
    # df = df.merge(关联表, on="applicant", how="left")  # 【按需启用】

    out = df[["patent_id", "group_id", "app_year", "main_ipc4", "is_invention"]]
    return out.dropna(subset=["patent_id", "group_id", "app_year"])


# ============ 引用表：有效性 + 集团内外 + 被引 IPC4/年份 ============
def _parse_cited_year(cited_id: pd.Series) -> pd.Series:
    """从被引专利申请号解析年份（上一套库的规则，按新库格式核对）：
    >=12 位数字取前 4 位；8 位取前 2 位（>=85→19xx，否则 20xx）。"""
    s = cited_id.astype(str).str.replace(r"\D", "", regex=True)
    y = pd.Series(np.nan, index=cited_id.index)
    m12, m8 = s.str.len() >= 12, s.str.len() == 8
    y[m12] = pd.to_numeric(s[m12].str[:4], errors="coerce")
    yy = pd.to_numeric(s[m8].str[:2], errors="coerce")
    y[m8] = np.where(yy >= 85, 1900 + yy, 2000 + yy)
    return pd.to_numeric(y, errors="coerce").astype("Int64")


def build_citations(raw: pd.DataFrame, patents: pd.DataFrame) -> pd.DataFrame:
    # 【按实际改】若引用关系在独立文件中，改为单独读取，勿依赖 raw
    df = raw.rename(columns={v: k for k, v in COLMAP.items()
                             if v and k in ("citing_id", "cited_id", "cite_type")})
    # 1) 有效引用：按新库引用类型体系筛选（构造约定：适配层负责打 is_valid）
    df["is_valid"] = df["cite_type"].isin(VALID_CITE_TYPES) if VALID_CITE_TYPES else True

    # 2) 被引专利是否属于同一集团：被引号 ∈ 本集团专利号集合
    own = patents[["patent_id", "group_id"]].drop_duplicates()
    df = df.merge(own.rename(columns={"patent_id": "cited_id",
                                      "group_id": "cited_group_id"}),
                  on="cited_id", how="left")
    citing_group = df[["citing_id"]].merge(
        own.rename(columns={"patent_id": "citing_id"}), on="citing_id", how="left")
    df["cited_in_group"] = (df["cited_group_id"].notna()
                            & (df["cited_group_id"] == citing_group["group_id"]))

    # 3) 被引 IPC4 / 申请年：优先从 patents 表连接；查不到时从被引申请号解析年份
    df = df.merge(patents[["patent_id", "main_ipc4", "app_year"]]
                  .rename(columns={"patent_id": "cited_id",
                                   "main_ipc4": "cited_ipc4",
                                   "app_year": "cited_app_year"}),
                  on="cited_id", how="left")
    miss = df["cited_app_year"].isna()
    df.loc[miss, "cited_app_year"] = _parse_cited_year(df.loc[miss, "cited_id"])

    return df[["citing_id", "cited_ipc4", "cited_in_group",
               "cited_app_year", "is_valid"]]


# ============ 质量诊断（对应 01 的数据质量清单，必须先跑再进 02） ============
def diagnose(patents: pd.DataFrame, citations: pd.DataFrame):
    cov = (patents[patents["is_invention"]]
           .groupby("app_year")["patent_id"].nunique())
    print("① 分年份发明专利收录量（核对尾部年份是否截断）：\n", cov.to_string())
    link = citations["cited_ipc4"].notna().mean()
    print(f"\n② 引用表连接率（被引能查到IPC4的比例）：{link:.1%}"
          "  —— 过低说明引用库与专利库匹配差")
    n_dup = patents.duplicated(["patent_id", "group_id"]).sum()
    print(f"\n③ 集团标识检查：patents 重复 (patent_id,group_id) {n_dup} 行（应为 0）")
    multi = patents.groupby("patent_id")["group_id"].nunique()
    print(f"\n④ 多申请人展开抽查：{int((multi > 1).sum())} 件专利归属多个集团，"
          f"单专利最大集团数 {int(multi.max())}（异常大需检查拆分逻辑）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True, help="【自填】原始数据目录")
    ap.add_argument("--out-dir", default=".", help="输出目录")
    a = ap.parse_args()
    out = Path(a.out_dir)

    raw = load_raw(Path(a.raw_dir))
    patents = build_patents(raw)
    citations = build_citations(raw, patents)
    diagnose(patents, citations)

    patents.to_csv(out / "patents.csv", index=False, encoding="utf-8-sig")
    citations.to_csv(out / "citations.csv", index=False, encoding="utf-8-sig")
    print(f"\n已输出: {out/'patents.csv'} ({len(patents)} 行), "
          f"{out/'citations.csv'} ({len(citations)} 行)")
    print("下一步：确认诊断结果后，运行 02_中间表→指标计算/knowledge_indicators.py")
