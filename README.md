# warp-drive：曲率引擎的可行性研究

发起人 / Initiator: [zdltvxq](https://github.com/zdltvxq)，2026-11-20。见[项目章程](docs/00-charter.md)。

**English abstract.** This project estimates the negative energy needed by an Alcubierre warp bubble.
It checks a flat-slice 3+1 ADM solver against the energy density in Alcubierre (1994, eq. 18)
and computes how the total Eulerian energy varies with bubble size, wall thickness, and speed.
The audit also estimates the energy of Planck-scale walls, using thicknesses motivated by
Pfenning and Ford rather than solving the quantum inequality.

**Keywords / Topics:** Alcubierre warp drive, warp engine, general relativity, 3+1 ADM formalism,
numerical relativity, exotic matter, negative energy density, quantum inequality,
faster-than-light travel, computational physics, spacetime curvature, feasibility study.

v0.1 已完成平切片求解器的解析验证和第一轮参数扫描。[实施计划](docs/02-plan.md)记录各阶段的验收条件，[开放问题](docs/03-open-problems.md)列出当前模型还没有回答的问题。

---

## 1. 能量估算

载荷舱半径取 10 m，速度取 1c。在扫描的参数中，所需负能量最少的是 tanh 形状：
总欧拉能量约为 −0.556 m（几何单位），即 −6.7×10⁴³ J；其绝对值对应 7.5×10²⁶ kg，约 0.39 个木星质量。此时壁厚尺度 `1/σ` 约为 8 m。

Pfenning 和 Ford（1997）在其假设下得到的壁厚上限只有几百个普朗克长度。保持载荷半径和速度不变，把壁厚设为 100 个普朗克长度，所需负能量的绝对值约为 1.2×10³⁰ 个太阳质量。这里用论文给出的壁厚量级作为输入，能量由本仓库计算。

## 2. 快速开始

```bash
uv venv .venv && uv pip install --python .venv/Scripts/python.exe numpy matplotlib
.venv/Scripts/python.exe -m unittest discover -s tests -v   # 10 项验证
.venv/Scripts/python.exe scripts/audit.py                   # 四张表、巡航示例、两张图和 CSV
```

输出：`data/energy_audit.csv`、`figs/rho_axis.png`、`figs/energy_curves.png`。

## 3. 仓库结构

```
warpdrive/
  units.py      几何单位（G=c=1）：1 m 能量 = 1.2136e44 J，M_sun = 1476.6 m
  shapes.py     形状函数族 f(r)：Alcubierre tanh / 紧支撑 smootherstep / 高斯壳
  flatslice.py  平切片 ADM 求解器：由 shift 和 lapse 计算 K_ij、tr K、θ、ρ_E
  alcubierre.py 闭式解（Alcubierre 1994 eq.18）+ 总能量一维积分 + 网格场构造
  optimize.py   搜索所需负能量最少的形状和包络
scripts/audit.py  审计表与作图
tests/            解析解比较、v² 标度、网格收敛阶、单位换算
docs/             设计、计划、开放问题
docs/00-charter.md 项目章程：发起人、归属、范围、署名规则
REFERENCES.md     文献、结论出处和 BibTeX
LICENSE           MIT
CITATION.cff      供 GitHub「Cite this repository」按钮使用
```

## 4. 物理基线（详见 `docs/01-design.md`）

基线度规采用平切片、单位 lapse（α=1），沿 x 轴直线巡航：

```
ds² = -dt² + (dx - v f(r) dt)² + dy² + dz² ,   r² = (x - x_s)² + y² + z²
K_ij = ½(∂_i β_j + ∂_j β_i)          （γ=δ ⇒ 联络项为零）
ρ_E  = T^{ab} n_a n_b = (K² - K_ij K^ij)/16π
     = -(v²/32π) · (y²+z²)/r² · f'(r)²           ← 与 Alcubierre 1994 eq.18 一致
E    = ∫ρ_E d³x = -(v²/12) ∫ f'(r)² r² dr        ← 角向因子 <(y²+z²)/r²> = 2/3
```

对这类沿 x 轴运动的 Alcubierre 泡，`ρ_E` 在运动轴上为零，在轴外且 `v` 和 `f′` 都不为零处为负。只要存在这样的负能量区，弱能量条件就不成立。

## 5. 验证

能量密度和膨胀率的误差取网格内部的最大绝对偏差，再除以对应解析解的最大绝对值。

| 项目 | 方法 | 结果 |
|---|---|---|
| 逐点能量密度 | 网格 ADM vs 闭式解 eq.18 | 相对误差 3.3×10⁻⁴（241³） |
| 体积膨胀 θ | 网格 −α tr K vs v(x/r)f′ | 相对误差 1.6×10⁻⁴ |
| 总能量 | 三维积分 vs 一维径向积分 | 偏差 < 2% |
| 收敛阶 | 121³ → 241³ | 观测阶 > 3（四阶差分） |
| 标度律 | E(v) / E(R) | E ∝ v²，固定壁厚比时 E ∝ R |

## 6. 参考文献

见[参考文献](REFERENCES.md)。其中的来源表区分原论文的结论与本仓库的计算结果。

## 7. 模型范围

当前求解器要求平切片（γ=δ），这里报告的 Alcubierre 计算取 α=1。非平切片需要在约束方程中加入空间曲率项，列入[实施计划](docs/02-plan.md)的 Phase 1。求解器使用经典广义相对论和几何单位（G=c=1），不计算量子场论修正。

## 8. 版权与引用

© 2026 zdltvxq。代码和文档采用 [MIT 许可证](LICENSE)。

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

GitHub 的「Cite this repository」按钮读取 `CITATION.cff`。引用能量估算时，请注明数值由本仓库计算，并按 [REFERENCES.md](REFERENCES.md) 的来源表引用相关论文。