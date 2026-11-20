# warp-drive — 曲率引擎（Warp Engine）设计与实施计划

**English abstract.** A computable feasibility audit of an Alcubierre-type warp drive (曲率引擎).
The repo contains a flat-slice 3+1 ADM solver validated point-by-point against Alcubierre's 1994
closed form (eq. 18), a design-space sweep over payload radius × vehicle envelope × cruise speed,
an energy budget in geometric units, and the quantum-inequality wall that decides the whole
program. Every number in the documents is reproducible from `scripts/audit.py`.

**Keywords / Topics:** Alcubierre warp drive, warp engine, general relativity, 3+1 ADM formalism,
numerical relativity, exotic matter, negative energy density, quantum inequality,
faster-than-light travel, computational physics, spacetime curvature, feasibility study.

把「曲率引擎」当成一个工程问题来拆：先把它写成可计算的东西，再让数字告诉我们它卡在哪。

本仓库不承诺造出飞船。它承诺三件事：

1. **可复算**：任何关于能量需求的结论，都能用本仓库的求解器重跑出来（`scripts/audit.py`）。
2. **可证伪**：每个阶段有明确的 go / no-go 判据（`docs/02-plan.md`），不靠"再研究研究"推进。
3. **不糊弄**：物理上做不到的地方直接写在 `docs/03-open-problems.md`，包括目前最强的反方证据。

状态：v0.1 —— 平切片 3+1 求解器 + 设计空间初扫已完成并通过与 Alcubierre 1994 解析式的对拍。

---

## 1. 一句话结论（由本仓库代码算出，不是引用）

对 10 m 半径的载荷舱，速度 1c，在"气泡壁越厚越省能量、但尾迹 r² 权重反噬"的权衡下，
最省的泡的总欧拉能量约

```
E ≈ -0.556 m(几何单位) = -6.7×10^43 J = 7.5×10^26 kg  ≈ 0.39 个木星质量的负能量
对应泡外径 ≈ 42 m，壁厚 ≈ 8 m
```

但同一套代码算出来的另一半结论才是真正的障碍：量子不等式把壁厚压到几百个普朗克长度时
（Pfenning & Ford 1997 的结论），能量变成 **-1.2×10^30 太阳质量 ≈ 10^7 倍可观测宇宙的总质量**。

也就是说：**曲率引擎不是"能量不够"，而是"负能量在空间上被压得极薄"**。
这条判断决定了整个技术路线的排法。

## 2. 快速开始

```bash
uv venv .venv && uv pip install --python .venv/Scripts/python.exe numpy matplotlib
.venv/Scripts/python.exe -m unittest discover -s tests -v   # 10 项验证
.venv/Scripts/python.exe scripts/audit.py                   # 四张表 + 两张图 + CSV
```

输出：`data/energy_audit.csv`、`figs/rho_axis.png`、`figs/energy_curves.png`。

## 3. 仓库结构

```
warpdrive/
  units.py      几何单位（G=c=1）：1 m 能量 = 1.2136e44 J，M_sun = 1476.6 m
  shapes.py     形状函数族 f(r)：Alcubierre tanh / 紧支撑 smootherstep / 高斯壳
  flatslice.py  通用平切片 ADM 求解器：任意 shift/apse 场 → K_ij、tr K、θ、ρ_E
  alcubierre.py 闭式解（Alcubierre 1994 eq.18）+ 总能量一维积分 + 网格场构造
  optimize.py   设计空间搜索：载荷半径 × 车辆包络 × 速度，找最省泡
scripts/audit.py  审计表与作图
tests/            与闭式解对拍、v² 标度、网格收敛阶、单位换算
docs/             设计、计划、开放问题
REFERENCES.md     文献清单 + 断言→来源映射 + BibTeX（与 README 同级）
LICENSE           MIT
CITATION.cff      供 GitHub「Cite this repository」按钮使用
```

## 4. 物理基线（详见 `docs/01-design.md`）

度规族（平切片、apse=1、沿 x 轴直线巡航）：

```
ds² = -dt² + (dx - v f(r) dt)² + dy² + dz² ,   r = |x - x0|
K_ij = ½(∂_i β_j + ∂_j β_i)          （γ=δ ⇒ 联络项为零）
ρ_E  = T^{ab} n_a n_b = (K² - K_ij K^ij)/16π
     = -(v²/32π) · (y²+z²)/r² · f'(r)²           ← 与 Alcubierre 1994 eq.18 一致
E    = ∫ρ_E d³x = -(v²/12) ∫ f'(r)² r² dr        ← 角向因子 <(y²+z²)/r²> = 2/3
```

`negative` 是结构性的：`K² - K_ijK^ij ≤ 0` 恒成立，所以只要 f 有梯度，总有 ρ_E < 0 ——
这就是弱能量条件必被破坏的原因，也是所有"正能量曲率引擎"论文的争议焦点。

## 5. 验证

| 项目 | 方法 | 结果 |
|---|---|---|
| 逐点能量密度 | 网格 ADM vs 闭式解 eq.18 | 相对误差 3.3×10⁻⁴（241³） |
| 体积膨胀 θ | 网格 −α tr K vs v(x/r)f′ | 相对误差 1.6×10⁻⁴ |
| 总能量 | 三维积分 vs 一维径向积分 | 偏差 < 2% |
| 收敛阶 | 121³ → 241³ | 观测阶 > 3（四阶差分） |
| 标度律 | E(v) / E(R) | E ∝ v²，固定壁厚比时 E ∝ R |

## 6. 参考文献

完整清单、**断言→来源映射表**、可直接粘贴的 BibTeX 都在 [REFERENCES.md](REFERENCES.md)。
收录标准：能打开 arXiv abs 页核对到标题与作者，且与仓库里某条断言直接相关。

需要事先说清的一条分界：文献给的是度规形式、解析式与定性结论；
**一切具体数字（表格、CSV、图）都是本仓库算的**，引用时请标为本文计算。

## 7. 边界声明

本仓库的求解器只覆盖 **平切片（γ=δ）+ apse=1** 的度规族，这是 Alcubierre / Natário 主线。
非平切片方案（Bobrick–Martire 型"physical warp drive"）、柱对称 Lentz 孤子需要扩展 3-Ricci 项，
排在 `docs/02-plan.md` 的 Phase 1。所有数字都是 G=c=1 几何单位下的经典广义相对论结果，
不含量子场论修正；QI 相关的数字来自"把壁厚设成给定值"的反推，不是自洽求解。

## 8. 版权与引用

© 2026 zdltvxq。代码与文档均以 **MIT** 许可证发布，全文见 [LICENSE](LICENSE)。

引用本仓库（完整 BibTeX 见 `REFERENCES.md` §3）：

```bibtex
@misc{warpdrive2026repo,
  author = {{zdltvxq}},
  title  = {warp-drive: Warp Engine -- a computable feasibility audit of an Alcubierre drive},
  year   = {2026},
  howpublished = {\url{https://github.com/zdltvxq/warp-drive}},
  note   = {Version 0.1.0}
}
```

GitHub 侧边栏的「Cite this repository」按钮由 `CITATION.cff` 提供，内容与此一致。
引用本仓库中的具体数字时，请注明"由本仓库计算"，并按其来源文献在 `REFERENCES.md`
的映射表中标注——文献没有这些数，别把我们的计算记到他们头上。