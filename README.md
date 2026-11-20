# warp-drive — 曲率引擎（Warp Engine）设计与实施计划

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
.venv/Scripts/python.exe scripts/audit.py                   # 三张表 + 两张图 + CSV
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

## 6. 引用

- M. Alcubierre, *The warp drive: hyper-fast travel within general relativity*, Class. Quantum Grav. 11 (1994) L73, arXiv:gr-qc/0009013
- M. J. Pfenning, L. H. Ford, *The unphysical nature of "Warp Drive"*, Class. Quantum Grav. 14 (1997) 1743, arXiv:gr-qc/9702026
- C. Van Den Broeck, *A "warp drive" with more reasonable total energy requirements*, arXiv:gr-qc/9905084
- J. Natário, *Warp drive with zero expansion*, arXiv:gr-qc/0110086
- E. W. Lentz, *Breaking the Warp Barrier: Hyper-Fast Solitons in Einstein-Maxwell-Plasma Theory*, arXiv:2006.07125
- J. Santiago, S. Schuster, M. Visser, *Generic warp drives violate the null energy condition*, arXiv:2105.03079

## 7. 边界声明

本仓库的求解器只覆盖 **平切片（γ=δ）+ apse=1** 的度规族，这是 Alcubierre / Natário 主线。
非平切片方案（Bobrick–Martire 型"physical warp drive"）、柱对称 Lentz 孤子需要扩展 3-Ricci 项，
排在 `docs/02-plan.md` 的 Phase 1。所有数字都是 G=c=1 几何单位下的经典广义相对论结果，
不含量子场论修正；QI 相关的数字来自"把壁厚设成给定值"的反推，不是自洽求解。