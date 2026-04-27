# ATRS: Adaptive Trajectory Re-splitting via a Shared Neural Policy for Parallel Optimization

*Jiajun Yu · 2026-04-24 · agents · Must read*

[paper](http://arxiv.org/abs/2604.22715v1) / [pdf](https://arxiv.org/pdf/2604.22715v1)

## TL;DR

The main contributions of this work are: • Adaptive Trajectory Re-splitting Framework: We formulate the adaptive structural adjustment for parallel trajectory optimization as a Multi-Agent RL problem for the first time.

## Main Contribution

The main contributions of this work are: • Adaptive Trajectory Re-splitting Framework: We formulate the adaptive structural adjustment for parallel trajectory optimization as a Multi-Agent RL problem for the first time.

## Main Result

To mitigate this, recent solvers exploit specific problem structures to achieve linear time complexity O(N).

## Method in Brief

In this section, we present the proposed adaptive trajectory re-splitting framework, ATRS.

## Summary by Section

### Abstract

Parallel trajectory optimization via the Alternating Direction Method of Multipliers (ADMM) has emerged as a scalable approach to long-horizon motion planning. However, existing frameworks typically decompose the problem into parallel subproblems based on a predefined fixed structure.

### Introduction and Problem

As applications expand to large-scale environments and swarm-level tasks [1], [2], optimizing long-horizon trajectories in real time becomes a critical computational challenge. Trajectory optimization is commonly formulated as an Optimal Control Problem (OCP).

### Method

In this section, we present the proposed adaptive trajectory re-splitting framework, ATRS. The underlying trajectory optimization is first formulated as a consensus parallel optimization problem via CADMM (Sec.

### Evaluation and Results

To mitigate this, recent solvers exploit specific problem structures to achieve linear time complexity O(N). Existing L2O methods have achieved notable progress in parameter tuning and solver warm-starting for problems with fixed dimensions. Benchmarks and real-world experiments validate that the lightweight policy enables faster convergence and real-time onboard deployment without sim-to-real degradation.

### Limitations

In this paper, we presented ATRS, which is based on parallel ADMM and embeds a shared DRL policy to re-split stagnating trajectory segments online. The re-splitting problem is formulated as a MASP-MDP in which all segments act as homogeneous agents sharing a unified policy network.

### Conclusion

In this paper, we presented ATRS, which is based on parallel ADMM and embeds a shared DRL policy to re-split stagnating trajectory segments online.

## Caveats

Fast note from local PDF text. Verify claims and limitations directly in the paper.

## Quick Facts

- First author: Jiajun Yu
- Primary topic: agents
- Secondary topics: theory optimization, reinforcement learning
- Fit: Medium
- Summary source: local PDF text
