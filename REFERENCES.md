# 参考文献

本文件与 `README.md` 同级，是被引用的原始文献清单与**断言→来源**映射。
所有 arXiv 编号在收录时用 `arxiv.org/abs/<id>` 逐条打开核对过（标题、作者）。

一条分界线必须先说清：

- **文献给的**：度规形式、能量密度的解析式、QI 的判据结论、各类方案的定性可行性。
- **本仓库算的**：一切具体数字（表格、CSV、图）。文献里没有"10 m 载荷舱、1c、最优包络 3.9 倍"
  这些数，它们是 `scripts/audit.py` 在本仓库的度规族下算出来的，引用时请标为本文计算。

---

## 1. 核心文献（按在项目中的作用排序）

### 1.1 M. Alcubierre, *The warp drive: hyper-fast travel within general relativity*
Class. Quantum Grav. **11** (1994) L73–L77 · arXiv:gr-qc/0009013

- 给出度规 `ds² = -dt² + (dx - v f(r) dt)² + dy² + dz²` 与 tanh 形状函数（eq. 6–8）。
- eq. 10 给外曲率、eq. 12 给体积膨胀 θ、eq. 13 证明舱内走测地线且无时间膨胀。
- **eq. 18 是全仓库的对拍基准**：`T^ab n_a n_b = -(v²/8π)(y²+z²)/(4r²) f'²`。
  本仓库 `warpdrive/alcubierre.py` 把它重推成 `-(v²/32π)(y²+z²)/r² f'²`，
  再用三维网格 ADM 求解器逐点验证（误差 3.3×10⁻⁴）。
- 原文只给能量密度，**没有给总能量的数值**；任何"M_☉ 级"的旧说法都不要记到这篇头上。

### 1.2 M. J. Pfenning, L. H. Ford, *The unphysical nature of "Warp Drive"*
Class. Quantum Grav. **14** (1997) 1743–1751 · arXiv:gr-qc/9702026

- 把量子不等式（QI）应用到曲率泡：负能量的**量级与持续尺度**受 QFT 限制。
- 结论：泡壁厚度被压到**几百个普朗克长度**，由此得到的总积分能量"physically unattainable"。
- 本仓库用它作为 `docs/03-open-problems.md` 的 P1（硬墙），并用 `optimize.qi_audit`
  把这条结论反推成能量数字：壁厚 100 ℓ_P、10 m 载荷、1c ⇒ ≈1.2×10³⁰ M_☉。

### 1.3 C. Van den Broeck, *A "warp drive" with more reasonable total energy requirements*
arXiv:gr-qc/9905084

- 对 Alcubierre 几何做微调（外部体积压缩），把总负质量降到"**几倍太阳质量**"级，
  并伴随同量级正能；作者称该几何满足量子不等式。
- 用途：证明"壁厚/几何设计能把能量降好几个数量级"，是反对"能量必然天文级"这一直觉的
  最强反例之一——本仓库 `optimize.py` 的包络权衡（E ∝ 1/壁厚）与它是同一机制。
- 该文同时指出 Alcubierre 泡的负能量区存在超光速（tachyonic）能量流，引 Clark–Hiscock–Larson。

### 1.4 W. A. Hiscock et al. (Clark, Hiscock & Larson), *Null geodesics in the Alcubierre warp drive spacetime: the view from the bridge*
arXiv:gr-qc/9907019

- 数值积分类光测地线：超光速时泡前方与后方各出现**视界**——后方锥形区无信号能追上飞船，
  前方锥形区飞船无法发出信号。
- 并指出二维修正下发现的真空能发散"很可能在四维同样存在，从而阻止任何飞船超过有效光速"。
- 用途：`docs/03-open-problems.md` 的 P3，且是 P1 之外**独立的**一条封堵。

### 1.5 J. Natário, *Warp drive with zero expansion*
arXiv:gr-qc/0110086（2002 年发表）

- 证明"前方收缩、后方膨胀"并非曲率泡的必要机制，并显式构造**零膨胀**的曲率泡。
- 同时给出一般性论证：由任意无旋矢量场生成的曲率泡，其欧拉观察者的体积膨胀就是 `∇·X`；
  并展示典型泡存在视界与无限蓝移。
- 用途：本仓库 `flatslice.py` 的 `θ = -α tr K = -∇·β` 与它一致；拓展阶段（Phase 1）
  要把零膨胀族作为第二批被复现的解。

### 1.6 E. W. Lentz, *Breaking the Warp Barrier: Hyper-Fast Solitons in Einstein–Maxwell–Plasma Theory*
arXiv:2006.07125

- 构造一类由**纯正能量密度**驱动的超光速孤子，并说明可由导电等离子体 + 经典电磁场提供。
- 用途：正能主张的代表作之一；Phase 1 要复现它的孤子能量，Phase 2 要用全观察者判据
  检验它（见 1.8 的反驳）。

### 1.7 A. Bobrick, G. Martire, *Introducing Physical Warp Drives*
Class. Quantum Grav. **38** (2021) 105009 · arXiv:2102.06824

- 给出包住所有既有定义的通用曲率泡模型；构造第一批**亚光速、正能量、球对称**的泡；
  给出满足量子不等式的超光速解；把 Alcubierre 的负能量需求**降低两个数量级**；
  并提出"空间容量与时间速率可控"的泡。
- 关键论点：**任何曲率泡都是惯性运动的能量壳层，因此仍然需要推进（propulsion）**——
  这条常被流行解读忽略。
- 用途：Phase 1 的非平切片复现目标之一。

### 1.8 J. Santiago, S. Schuster, M. Visser, *Generic warp drives violate the null energy condition*
arXiv:2105.03079（PRD 接收版）

- 对 1.6 / 1.7 一类"正能量曲率泡"主张的系统反驳：WEC 要求**所有类时观察者**看到正密度，
  而那些工作只验证了共动欧拉观察者。结论是在其框架内所有物理上合理的泡必然违反 WEC/SEC/DEC，
  在合理附加假设下违反 NEC；即便在修改引力中，几何的零/类时收敛条件仍被违反。
- 用途：`docs/03-open-problems.md` 的 P2。**这条是反方最强证据，必须与 1.6/1.7 并列出现**，
  否则本仓库的设计文档不可信。

---

## 2. 断言 → 来源映射

| 断言 | 来源 | 谁负责算 |
|---|---|---|
| `ρ_E = -(v²/32π)(y²+z²)/r² f'²` | Alcubierre 1994 eq.18 [1.1] | 重推 + 网格对拍（本仓库） |
| 舱内为测地线、无时间膨胀 | Alcubierre 1994 eq.13 [1.1] | 未重复验证（解析结论） |
| `K² - K_ijK^ij ≤ 0` ⇒ 必有负能量 | 恒等式 [1.1] | 本仓库恒等式 + 数值检查 |
| 壁厚被 QI 压到数百 ℓ_P，总能量不可及 | Pfenning–Ford [1.2] | 用 `qi_audit` 反推数字（本仓库） |
| 体积压缩可把总负质量降到几倍 M_☉ | Van den Broeck [1.3] | 未复现（Phase 1） |
| 泡前后视界、真空能发散可能阻断 >c | Clark–Hiscock–Larson [1.4] | 未复现（Phase 1，测地线） |
| 零膨胀泡同样存在视界与蓝移 | Natário [1.5] | 未复现（Phase 1） |
| 正能量超光速孤子存在 | Lentz [1.6] | 未复现（Phase 1） |
| 亚光速正能泡 + QI 相容 + 负能量降两个量级 | Bobrick–Martire [1.7] | 未复现（Phase 1） |
| 正能量主张只对共动观察者成立，全观察者必违 | Santiago–Schuster–Visser [1.8] | Phase 2（全观察者扫描） |
| E ∝ v²；固定壁厚比时 E ∝ R | 本仓库 | `tests/test_validation.py` |
| 最优包络 ≈ 3.9×载荷半径；1c/10 m 需 7.5×10²⁶ kg | 本仓库 | `scripts/audit.py` → `data/energy_audit.csv` |
| QI 壁厚下需求 ≈1.2×10³⁰ M_☉ | 本仓库 | `optimize.qi_audit` |

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

收录标准：能打开 arXiv abs 页核对到标题+作者，且与本仓库的某条断言直接相关；否则不进本文件。