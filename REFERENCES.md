# 参考文献

下文按研究主题列出论文，并在第 2 节注明哪些结果由本仓库复算。10 m 载荷舱的能量估算和包络扫描来自 `scripts/audit.py`，不是论文中的数值。

## 1. 文献注释

### 1.1 M. Alcubierre, *The warp drive: hyper-fast travel within general relativity*
Class. Quantum Grav. **11** (1994) L73–L77 · arXiv:gr-qc/0009013

- 给出度规 `ds² = -dt² + (dx - v f(r) dt)² + dy² + dz²` 与 tanh 形状函数（eq. 6–8）。
- eq. 10 给外曲率、eq. 12 给体积膨胀 θ、eq. 13 证明舱内走测地线且无时间膨胀。
- 用式 18 的能量密度检验三维网格求解器。`warpdrive/alcubierre.py` 采用等价写法 `-(v²/32π)(y²+z²)/r² f'²`，网格验证的归一化最大误差约为 3.3×10⁻⁴。
- 原文给出能量密度，未报告总能量数值。

### 1.2 M. J. Pfenning, L. H. Ford, *The unphysical nature of "Warp Drive"*
Class. Quantum Grav. **14** (1997) 1743–1751 · arXiv:gr-qc/9702026

- 作者把量子不等式（QI）用于 Alcubierre 泡，在其假设下得到约几百个普朗克长度的壁厚上限，并认为相应的总能量无法达到。
- `optimize.qi_audit` 采用指定壁厚进行估算：取壁厚 100 ℓ_P、载荷半径 10 m、速度 1c，负能量绝对值对应约 1.2×10³⁰ M_☉。

### 1.3 C. Van den Broeck, *A "warp drive" with more reasonable total energy requirements*
arXiv:gr-qc/9905084

- 修改 Alcubierre 几何，使内部容积相对于外部尺度增大。作者报告的负能量绝对值相当于几倍太阳质量，另有同量级正能量，并认为该几何满足所用的量子不等式。
- 本仓库的平切片包络扫描不包含这一几何；计划在 Phase 1 单独复现。
- 该文同时指出 Alcubierre 泡的负能量区存在超光速（tachyonic）能量流，引 Clark–Hiscock–Larson。

### 1.4 C. Clark, W. A. Hiscock, S. L. Larson, *Null geodesics in the Alcubierre warp drive spacetime: the view from the bridge*
arXiv:gr-qc/9907019

- 作者数值积分类光测地线，发现超光速泡的前后方各有视界：船内信号到不了前方锥形区，后方锥形区的信号也追不上飞船。
- 并指出二维修正下发现的真空能发散"很可能在四维同样存在，从而阻止任何飞船超过有效光速"。
- 对应 `docs/03-open-problems.md` 的 P3（视界）。

### 1.5 J. Natário, *Warp drive with zero expansion*
arXiv:gr-qc/0110086（2002 年发表）

- 构造零膨胀曲率泡，说明曲率泡不要求前方收缩、后方膨胀。
- 体积膨胀率由 shift 的散度决定；在本仓库的符号约定下为 `θ = -α tr K = -∇·β`。论文还讨论了视界和无限蓝移。零膨胀解列入 Phase 1 的复现计划。

### 1.6 E. W. Lentz, *Breaking the Warp Barrier: Hyper-Fast Solitons in Einstein–Maxwell–Plasma Theory*
arXiv:2006.07125

- 作者提出一类欧拉能量密度为正的超光速孤子，并讨论导电等离子体和经典电磁场能否提供所需源。
- Phase 1 复现其能量估算，Phase 2 检查其他观察者测得的能量密度。参见 1.8。

### 1.7 A. Bobrick, G. Martire, *Introducing Physical Warp Drives*
Class. Quantum Grav. **38** (2021) 105009 · arXiv:2102.06824

- 提出一般曲率泡模型，给出亚光速、正能量的球对称例子，以及作者认为满足量子不等式的超光速解。论文还估算了降低 Alcubierre 泡负能量需求的方案，报告降幅约两个数量级，并讨论了可调的舱内容积和时间速率。
- 在作者的模型中，泡是惯性运动的能量壳层；改变运动状态仍需要推进。
- 用途：Phase 1 的非平切片复现目标之一。

### 1.8 J. Santiago, S. Schuster, M. Visser, *Generic warp drives violate the null energy condition*
arXiv:2105.03079（PRD 接收版）

- WEC 要求所有类时观察者测得非负能量密度，仅检查欧拉观察者还不够。在论文的框架下，符合其假设的泡违反 WEC、SEC 和 DEC；NEC 的结论还需要附加假设。作者也指出，即使改用修正引力，相关几何仍违反类光或类时收敛条件。
- 对应 `docs/03-open-problems.md` 的 P2（正能量主张）。

---

## 2. 结论出处与复现状态

| 结论 | 来源 | 复现状态 |
|---|---|---|
| `ρ_E = -(v²/32π)(y²+z²)/r² f'²` | Alcubierre 1994 eq.18 [1.1] | 已与网格结果比较 |
| 舱内为测地线、无时间膨胀 | Alcubierre 1994 eq.13 [1.1] | 未重复验证（解析结论） |
| 运动中的 Alcubierre 泡存在负能量区 | Alcubierre 1994 eq.18 [1.1] | 网格结果确认存在负能量区 |
| 在论文假设下，壁厚上限为数百 ℓ_P | Pfenning–Ford [1.2] | `qi_audit` 使用指定壁厚，未复算上限 |
| 体积压缩可把总负质量降到几倍 M_☉ | Van den Broeck [1.3] | 未复现（Phase 1） |
| 泡前后视界、真空能发散可能阻断 >c | Clark–Hiscock–Larson [1.4] | 未复现（Phase 1，测地线） |
| 零膨胀泡同样存在视界与蓝移 | Natário [1.5] | 未复现（Phase 1） |
| 超光速孤子的欧拉能量密度为正（作者主张） | Lentz [1.6] | 未复现（Phase 1） |
| 亚光速正能泡 + QI 相容 + 负能量降两个量级 | Bobrick–Martire [1.7] | 未复现（Phase 1） |
| 欧拉能量密度非负不足以满足 WEC | Santiago–Schuster–Visser [1.8] | Phase 2 将检查其他类时方向 |
| E ∝ v²；固定壁厚比时 E ∝ R | 本仓库 | `tests/test_validation.py` |
| 本次扫描的最优包络比约为 3.9；载荷半径 10 m、速度 1c 时，能量绝对值对应 7.5×10²⁶ kg | 本仓库 | `scripts/audit.py` 生成 `data/energy_audit.csv` |
| 壁厚取 100 ℓ_P 时，能量绝对值对应约 1.2×10³⁰ M_☉ | 本仓库 | `optimize.qi_audit` |

---

## 3. BibTeX

```bibtex
@article{alcubierre1994warp,
  author  = {Alcubierre, Miguel},
  title   = {The warp drive: hyper-fast travel within general relativity},
  journal = {Classical and Quantum Gravity},
  volume  = {11},
  pages   = {L73--L77},
  year    = {1994},
  eprint  = {gr-qc/0009013},
  archivePrefix = {arXiv}
}

@article{pfenning1997unphysical,
  author  = {Pfenning, Michael J. and Ford, L. H.},
  title   = {The unphysical nature of ``Warp Drive''},
  journal = {Classical and Quantum Gravity},
  volume  = {14},
  pages   = {1743--1751},
  year    = {1997},
  eprint  = {gr-qc/9702026},
  archivePrefix = {arXiv}
}

@misc{vandenbroeck1999warp,
  author = {Van Den Broeck, Chris},
  title  = {A ``warp drive'' with more reasonable total energy requirements},
  year   = {1999},
  eprint = {gr-qc/9905084},
  archivePrefix = {arXiv}
}

@misc{clark1999null,
  author = {Clark, Carl and Hiscock, William A. and Larson, Shane L.},
  title  = {Null geodesics in the Alcubierre warp drive spacetime: the view from the bridge},
  year   = {1999},
  eprint = {gr-qc/9907019},
  archivePrefix = {arXiv}
}

@misc{natario2002zero,
  author = {Nat{\'a}rio, Jos{\'e}},
  title  = {Warp drive with zero expansion},
  year   = {2002},
  eprint = {gr-qc/0110086},
  archivePrefix = {arXiv}
}

@misc{lentz2020breaking,
  author = {Lentz, Erik W.},
  title  = {Breaking the Warp Barrier: Hyper-Fast Solitons in {Einstein--Maxwell--Plasma} Theory},
  year   = {2020},
  eprint = {2006.07125},
  archivePrefix = {arXiv}
}

@article{bobrick2021introducing,
  author  = {Bobrick, Alexey and Martire, Gianni},
  title   = {Introducing physical warp drives},
  journal = {Classical and Quantum Gravity},
  volume  = {38},
  pages   = {105009},
  year    = {2021},
  eprint  = {2102.06824},
  archivePrefix = {arXiv}
}

@misc{santiago2022generic,
  author = {Santiago, Jessica and Schuster, Sebastian and Visser, Matt},
  title  = {Generic warp drives violate the null energy condition},
  year   = {2022},
  eprint = {2105.03079},
  archivePrefix = {arXiv}
}

@misc{warpdrive2026repo,
  author = {{zdltvxq}},
  title  = {warp-drive: Warp Engine -- a computable feasibility audit of an Alcubierre drive},
  year   = {2026},
  howpublished = {\url{https://github.com/zdltvxq/warp-drive}},
  note   = {Version 0.1.0}
}
```

## 4. 尚未纳入（Phase 1 待读）

- 数值相对论中曲率泡的演化与不稳定性（泡在加速/减速时的行为）
- 修改引力下的曲率泡（作为"新物理清单"的候选，见 `docs/02-plan.md` Phase 4-B）
- 类比引力实验（BEC / 非线性光学 / 超材料）里可对应的 `K_ij` 与 `θ` 场

收录与仓库研究问题直接相关的论文，并按 arXiv 摘要页核对标题和作者。