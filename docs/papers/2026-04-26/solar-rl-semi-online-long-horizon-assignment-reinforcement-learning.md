# SOLAR-RL: Semi-Online Long-horizon Assignment Reinforcement Learning

*Jichao Wang · 2026-04-24 · foundation models · Must read*

[paper](http://arxiv.org/abs/2604.22558v1) / [pdf](https://arxiv.org/pdf/2604.22558v1)

## TL;DR

Our main contributions are summarized as follows: • We propose SOLAR-RL, a framework that bridges the gap between offline training stability and online exploration by simulating dynamic feedback mechanisms within static datasets. • We introduce a trajectory-aware reward shaping mechanism that addresses the credit assignment problem by performing retroactive credit assignment via failure-point detection and target-aligned reward shaping, distilling trajectory-level execution quality into dense step-level rewards. • We achieve competitive performance with online/SFT baselines without interaction, specifically demonstrating superior robustness and generalization in complex, long-horizon tasks compared to strong baselines.

## Main Contribution

Our main contributions are summarized as follows: • We propose SOLAR-RL, a framework that bridges the gap between offline training stability and online exploration by simulating dynamic feedback mechanisms within static datasets. • We introduce a trajectory-aware reward shaping mechanism that addresses the credit assignment problem by performing retroactive credit assignment via failure-point detection and target-aligned reward shaping, distilling trajectory-level execution quality into dense step-level rewards. • We achieve competitive performance with online/SFT baselines without interaction, specifically demonstrating superior robustness and generalization in complex, long-horizon tasks compared to strong baselines.

## Main Result

In this section, we rigorously evaluate SOLAR-RL across three diverse benchmarks.

## Method in Brief

In this section, we introduce SOLAR-RL, a Semionline Reinforcement Learning framework designed to address the credit assignment problem in long-horizon GUI navigation.

## Summary by Section

### Abstract

As Multimodal Large Language Models (MLLMs) mature, GUI agents are evolving from static interactions to complex navigation. While Reinforcement Learning (RL) has emerged as a promising paradigm for training MLLM agents on dynamic GUI tasks, its effective application faces a dilemma.

### Introduction and Problem

Critically, both paradigms grapple with the Credit Assignment Problem (CAP) (Lu et al., 2025b). This challenge motivates the need for a paradigm that retains the stability of offline learning while incorporating trajectory-level signals typically available only in online interaction.

### Method

In this section, we introduce SOLAR-RL, a Semionline Reinforcement Learning framework designed to address the credit assignment problem in long-horizon GUI navigation. Then, we detail our two core components: (1) Offline Trajectory Reconstruction, which simulates online interaction dynamics using static data to expand the exploration space; and (2) Trajectory-Aware Reward Shaping, which retroactively propagates outcome variations to accurately attribute credit in sparse-reward environments.

### Evaluation and Results

In this section, we rigorously evaluate SOLAR-RL across three diverse benchmarks. We aim to answer two key questions: (1) Does SOLAR-RL achieve competitive performance against state-of-the-art GUI agents, particularly under strict offline constraints? (2) Does the proposed semi-online mechanism effectively mitigate the training instability and policy collapse often observed in standard RL baselines?

### Limitations

Specifically, we reconstruct diverse rollout candidates from static data, detect the first failure point using per-step validity signals, and retroactively assign dense step-level rewards with target-aligned shaping to reflect trajectory-level execution quality—effectively simulating online feedback without interaction costs. It utilizes trajectory reconstruction and retroactive credit assignment via failure-point detection, combined with target-aligned reward shaping, to simulate pseudoonline feedback, ensuring stable long-horizon optimization. applicability across diverse operating systems (Qin et al., 2025).

### Conclusion

While Reinforcement Learning (RL) has emerged as a promising paradigm for training MLLM agents on dynamic GUI tasks, its effective application faces a dilemma. Standard Offline RL often relies on static step-level data, neglecting global trajectory semantics such as task completion and execution quality.

## Caveats

Specifically, we reconstruct diverse rollout candidates from static data, detect the first failure point using per-step validity signals, and retroactively assign dense step-level rewards with target-aligned shaping to reflect trajectory-level execution quality—effectively simulating online feedback without interaction costs.

## Quick Facts

- First author: Jichao Wang
- Primary topic: foundation models
- Secondary topics: agents, reinforcement learning
- Fit: Medium
- Summary source: local PDF text
