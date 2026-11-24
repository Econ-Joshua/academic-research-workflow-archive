# -*- coding: utf-8 -*-
"""
专利数据 → 企业知识结构指标（Y1/Y2/M1/M2/W）计算器
====================================================

本脚本只负责"标准中间表 → 指标"这一步，接口稳定、与数据库无关。
"新数据库 → 标准中间表"的适配层（下载、清洗、多申请人展开、is_valid 标记等）
必须由使用者按新库自行编写，不在本脚本职责内。

输入：两张标准中间表（pandas DataFrame 或 csv/parquet/pickle 文件）
------------------------------------------------------------------
专利表 patents：
    patent_id    专利号（str）
    group_id     上市公司集团标识，如股票代码（str）
    app_year     申请年（int）
    main_ipc4    主 IPC 四位分类（str）
    is_invention 是否发明专利（bool）
    ※ 多申请人专利须在适配层按申请人集团展开为多条记录（同一 patent_id 出现多次，
      每个集团一条），本脚本不做跨集团去重。

引用表 citations：
    citing_id      引用方专利号，对应 patents.patent_id（str）
    cited_ipc4     被引专利主 IPC4（str，缺失用 NaN）
    cited_in_group 被引专利是否属于同一集团（bool）
    cited_app_year 被引专利申请年（int，缺失用 NaN）
    is_valid       是否有效引用（bool；引用类型取舍规则属适配层职责）

输出：企业-年份面板，主键 (group_id, year)
------------------------------------------------------------------
    group_id            集团标识
    year                年份 t
    FieldNum            Y1a 技术类别数量 |C_it|（仅发明专利主 IPC4 去重计数）
    Width               Y1b 知识宽度 1 − Σ s²（赫芬达尔 1−HHI，发明专利在各类别占比）
    D_FieldNum          ΔFieldNum_t = FieldNum_t − FieldNum_{t−1}
                        （t 与 t−1 年都有专利记录才计算，否则 NaN）
    D_Width             ΔWidth_t = Width_t − Width_{t−1}（同上前提）
    ReuseCount          Y2a 既有领域再生产数量 ln(1 + #{p∈P_t : c(p)∈C_{t−1}})
                        （t 与 t−1 年都有专利记录才计算，否则 NaN）
    ReuseShare          Y2b 上述数量 / |P_t|（|P_t|=0 时 NaN）
    NewSearchCount      M1a 新知识搜索数量 ln(1 + |E_t \\ E^H_t|)，
                        E_t = t 年有效外部引用 cited_ipc4 集合，
                        E^H_t = t−5 至 t−1 年有效外部引用类别并集；
                        集合差为空集时天然为 ln(1+0)=0
    NewSearchShare      M1b |E_t \\ E^H_t| / |E_t|（|E_t|=0 时 NaN）
    SelfCite_win        M2 中间量：t 年发明专利有效引用中，被引属同一集团且
                        cited_app_year ∈ [t−5, t−1] 的次数
    SelfCite_all        稳健口径：被引属同一集团且 cited_app_year < t 的次数（全部历史）
    BackCite            t 年发明专利全部有效后向引用次数
    InternalReuseCount  M2a 内部知识重用数量 ln(1 + SelfCite_win)
    InternalReuseShare  M2b SelfCite_win / BackCite（BackCite=0 时 NaN）
    Open                W 外部知识搜索开放度 1 − Σ q²，
                        q 为 [t−4, t] 五年窗口内有效外部引用在 cited_ipc4 上的分布份额；
                        回归中 W 用 t−1 年值，即取上一年的 Open 入模
                        （窗口内无有效外部引用时 NaN）

约定
------------------------------------------------------------------
- 面板行为 patents 中出现过的 (group_id, app_year) 组合；某年无任何专利记录则无该行。
- 某年无记录时指标为 NaN，不填 0；定义上天然为 0 的除外（如 NewSearchCount）。
- 历史窗口一律 t−5 至 t−1（Open 等价地落在行年份 t 时为 [t−4, t]）；
  M2 稳健口径扩展至 t 年以前全部历史，列名 SelfCite_all 区分。
- 时间对齐：解释变量（M1/M2/W）在 t 年，Y1/Y2 结果变量在 t+1 年；
  本面板中每行指标均以该行年份标注，回归时自行 lag/lead 对齐。

CLI 用法
------------------------------------------------------------------
    python knowledge_indicators.py --patents patents.csv --citations citations.parquet --out panel.csv
输入按扩展名自动识别 csv / parquet / pkl(pickle)；输出支持 csv / parquet。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HISTORY_WINDOW = 5  # 历史窗口长度：t−5 至 t−1

PATENTS_COLS = ["patent_id", "group_id", "app_year", "main_ipc4", "is_invention"]
CITATIONS_COLS = ["citing_id", "cited_ipc4", "cited_in_group", "cited_app_year", "is_valid"]


def _check_schema(df: pd.DataFrame, cols: list[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{name} 缺少必需列: {missing}；需要 {cols}")


def build_panel(patents: pd.DataFrame, citations: pd.DataFrame, years=None) -> pd.DataFrame:
    """由标准中间表计算企业-年份知识结构指标面板。

    参数
    ----
    patents : DataFrame，schema 见模块 docstring。
    citations : DataFrame，schema 见模块 docstring。
    years : 可选，年份可迭代对象；给出时仅输出这些年份的面板行
            （历史窗口仍使用全部输入数据计算，不受 years 截断）。

    返回
    ----
    DataFrame，主键 (group_id, year)，列含义见模块 docstring。
    """
    _check_schema(patents, PATENTS_COLS, "patents")
    _check_schema(citations, CITATIONS_COLS, "citations")

    p = patents[PATENTS_COLS].copy()
    p["app_year"] = p["app_year"].astype(int)
    inv = p[p["is_invention"]].copy()  # Y 类指标只用发明专利

    # ---------- 面板骨架：patents 中出现过的 (group_id, year) ----------
    panel = p[["group_id", "app_year"]].drop_duplicates()
    panel = panel.rename(columns={"app_year": "year"}).sort_values(["group_id", "year"])
    panel = panel.reset_index(drop=True)

    # ---------- Y1: FieldNum / Width（仅发明专利） ----------
    if not inv.empty:
        cnt = (
            inv.groupby(["group_id", "app_year", "main_ipc4"])
            .size()
            .rename("n")
            .reset_index()
        )
        gy = cnt.groupby(["group_id", "app_year"]).agg(
            FieldNum=("main_ipc4", "size"), N=("n", "sum")
        ).reset_index()
        cnt = cnt.merge(gy[["group_id", "app_year", "N"]], on=["group_id", "app_year"])
        cnt["s2"] = (cnt["n"] / cnt["N"]) ** 2
        hhi = cnt.groupby(["group_id", "app_year"])["s2"].sum().rename("hhi").reset_index()
        gy = gy.merge(hhi, on=["group_id", "app_year"])
        gy["Width"] = 1.0 - gy["hhi"]
        panel = panel.merge(
            gy.rename(columns={"app_year": "year"})[["group_id", "year", "FieldNum", "Width"]],
            on=["group_id", "year"],
            how="left",
        )
    else:
        panel["FieldNum"] = np.nan
        panel["Width"] = np.nan

    # ---------- ΔFieldNum / ΔWidth（要求 t 与 t−1 年都有记录） ----------
    grp = panel.groupby("group_id", sort=False)
    prev_year = grp["year"].shift()
    consecutive = (panel["year"] - prev_year) == 1  # 上年有记录
    panel["D_FieldNum"] = grp["FieldNum"].diff().where(consecutive)
    panel["D_Width"] = grp["Width"].diff().where(consecutive)

    # ---------- Y2: ReuseCount / ReuseShare ----------
    if not inv.empty:
        # t−1 年既有类别集合（平移一年作为"当年可复用集合"）
        prev_cats = inv[["group_id", "app_year", "main_ipc4"]].drop_duplicates()
        prev_cats = prev_cats.assign(app_year=prev_cats["app_year"] + 1, _hit=True)
        m = inv.merge(
            prev_cats, on=["group_id", "app_year", "main_ipc4"], how="left"
        )
        m["_hit"] = m["_hit"].fillna(False).astype(bool)
        reuse = m.groupby(["group_id", "app_year"]).agg(
            _reuse_raw=("_hit", "sum"), _P=("patent_id", "size")
        ).reset_index()
        reuse["ReuseCount"] = np.log1p(reuse["_reuse_raw"])
        reuse["ReuseShare"] = np.where(
            reuse["_P"] > 0, reuse["_reuse_raw"] / reuse["_P"], np.nan
        )
        panel = panel.merge(
            reuse.rename(columns={"app_year": "year"})[
                ["group_id", "year", "ReuseCount", "ReuseShare"]
            ],
            on=["group_id", "year"],
            how="left",
        )
        # 上年无记录时 Δ/Reuse 类不计算
        panel.loc[~consecutive, ["ReuseCount", "ReuseShare"]] = np.nan
    else:
        panel["ReuseCount"] = np.nan
        panel["ReuseShare"] = np.nan

    # ---------- 引用表连接专利表（拿到引用方的集团与年份） ----------
    c = citations[CITATIONS_COLS].copy()
    c = c.merge(
        p[["patent_id", "group_id", "app_year", "is_invention"]],
        left_on="citing_id",
        right_on="patent_id",
        how="inner",
    ).drop(columns=["patent_id"])

    valid = c[c["is_valid"]]
    ext = valid[(~valid["cited_in_group"]) & valid["cited_ipc4"].notna()]

    # ---------- M1: NewSearchCount / NewSearchShare ----------
    if not ext.empty:
        # 去重后的 (集团, 年份, 外部类别)
        ecats = ext[["group_id", "app_year", "cited_ipc4"]].drop_duplicates()
        ecats = ecats.sort_values(["group_id", "cited_ipc4", "app_year"])
        # 同一集团同一类别的上一次出现年份；距上次 >5 年（或首次）即为窗口内"新"
        prev_occ = ecats.groupby(["group_id", "cited_ipc4"])["app_year"].shift()
        ecats["_new"] = prev_occ.isna() | ((ecats["app_year"] - prev_occ) > HISTORY_WINDOW)
        m1 = ecats.groupby(["group_id", "app_year"]).agg(
            _E=("cited_ipc4", "size"), _new=("_new", "sum")
        ).reset_index()
        m1["NewSearchCount"] = np.log1p(m1["_new"])
        m1["NewSearchShare"] = np.where(m1["_E"] > 0, m1["_new"] / m1["_E"], np.nan)
        panel = panel.merge(
            m1.rename(columns={"app_year": "year"})[
                ["group_id", "year", "NewSearchCount", "NewSearchShare"]
            ],
            on=["group_id", "year"],
            how="left",
        )
        # 该年有专利记录但无有效外部引用：E 为空集 → 差集为空 → NewSearchCount 天然为 0
        panel["NewSearchCount"] = panel["NewSearchCount"].fillna(0.0)
        # NewSearchShare 保持 NaN（|E|=0）
    else:
        panel["NewSearchCount"] = 0.0
        panel["NewSearchShare"] = np.nan

    # ---------- M2: SelfCite / BackCite / InternalReuse（仅发明专利的引用） ----------
    vinv = valid[valid["is_invention"]]
    if not vinv.empty:
        t = vinv["app_year"]
        cy = vinv["cited_app_year"]
        in_group = vinv["cited_in_group"]
        vinv = vinv.assign(
            _self_win=in_group & cy.notna()
            & (cy >= t - HISTORY_WINDOW) & (cy <= t - 1),
            _self_all=in_group & cy.notna() & (cy < t),
        )
        m2 = vinv.groupby(["group_id", "app_year"]).agg(
            SelfCite_win=("_self_win", "sum"),
            SelfCite_all=("_self_all", "sum"),
            BackCite=("citing_id", "size"),
        ).reset_index()
        m2["InternalReuseCount"] = np.log1p(m2["SelfCite_win"])
        m2["InternalReuseShare"] = np.where(
            m2["BackCite"] > 0, m2["SelfCite_win"] / m2["BackCite"], np.nan
        )
        panel = panel.merge(
            m2.rename(columns={"app_year": "year"})[
                ["group_id", "year", "SelfCite_win", "SelfCite_all",
                 "BackCite", "InternalReuseCount", "InternalReuseShare"]
            ],
            on=["group_id", "year"],
            how="left",
        )
        # 有记录但该年发明专利无有效引用：次数天然为 0，比例为 NaN
        for col in ["SelfCite_win", "SelfCite_all", "BackCite", "InternalReuseCount"]:
            panel[col] = panel[col].fillna(0)
    else:
        panel["SelfCite_win"] = 0
        panel["SelfCite_all"] = 0
        panel["BackCite"] = 0
        panel["InternalReuseCount"] = 0.0
        panel["InternalReuseShare"] = np.nan

    # ---------- W: Open（五年窗口内有效外部引用类别分布的 1−HHI） ----------
    # 行年份 t 对应窗口 [t−4, t]，即论文记号中 Open_{i,t−1} 用 [t−5, t−1]。
    if not ext.empty:
        ec = (
            ext.groupby(["group_id", "app_year", "cited_ipc4"])
            .size()
            .rename("n")
            .reset_index()
        )
        open_parts = []
        for g, sub in ec.groupby("group_id"):
            full_years = range(int(sub["app_year"].min()), int(sub["app_year"].max()) + 1)
            mat = sub.pivot_table(
                index="app_year", columns="cited_ipc4", values="n",
                fill_value=0, aggfunc="sum",
            ).reindex(full_years, fill_value=0)
            roll = mat.rolling(HISTORY_WINDOW, min_periods=1).sum()
            tot = roll.sum(axis=1)
            hhi = roll.div(tot.replace(0, np.nan), axis=0).pow(2).sum(axis=1)
            open_s = 1.0 - hhi
            open_s[tot == 0] = np.nan  # 窗口内无有效外部引用 → NaN
            open_parts.append(
                pd.DataFrame({"group_id": g, "year": open_s.index, "Open": open_s.values})
            )
        open_df = pd.concat(open_parts, ignore_index=True)
        panel = panel.merge(open_df, on=["group_id", "year"], how="left")
    else:
        panel["Open"] = np.nan

    if years is not None:
        panel = panel[panel["year"].isin(set(years))].reset_index(drop=True)

    return panel


def _read_table(path: str) -> pd.DataFrame:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, dtype={"patent_id": str, "group_id": str, "citing_id": str})
    if suffix in (".parquet", ".pq"):
        return pd.read_parquet(path)
    if suffix in (".pkl", ".pickle"):
        return pd.read_pickle(path)
    raise ValueError(f"无法识别的文件扩展名: {suffix}（支持 csv/parquet/pkl）")


def _write_table(df: pd.DataFrame, path: str) -> None:
    suffix = Path(path).suffix.lower()
    if suffix in (".parquet", ".pq"):
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="专利数据 → 企业知识结构指标（Y1/Y2/M1/M2/W）")
    ap.add_argument("--patents", required=True, help="专利表路径（csv/parquet/pkl）")
    ap.add_argument("--citations", required=True, help="引用表路径（csv/parquet/pkl）")
    ap.add_argument("--out", required=True, help="输出面板路径（csv/parquet）")
    ap.add_argument("--years", default=None,
                    help="可选，仅输出指定年份，如 2015-2022 或 2018,2019,2020")
    args = ap.parse_args()

    years = None
    if args.years:
        s = args.years.strip()
        if "-" in s and "," not in s:
            a, b = s.split("-", 1)
            years = list(range(int(a), int(b) + 1))
        else:
            years = [int(x) for x in s.split(",")]

    panel = build_panel(_read_table(args.patents), _read_table(args.citations), years=years)
    _write_table(panel, args.out)
    print(f"已输出面板 {len(panel)} 行 × {panel.shape[1]} 列 → {args.out}")
