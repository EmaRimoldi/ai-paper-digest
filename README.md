# AI Paper Radar

![AI Paper Radar](public/assets/hero.svg)

I built this as my personal research radar: a way to stay updated on AI papers without getting buried under the daily arXiv avalanche.

The goal is simple: track the papers that look genuinely worth reading, organize them by topic, and keep very short notes on what each paper contributes. It is not a replacement for careful reading; it is my first-pass filter for turning research noise into signal.

I outsource the noise, not the thinking.

<!-- AUTO-GENERATED:RUN_METADATA -->

Last updated: `2026-04-26`
Papers tracked: `80`

## Today’s Top 10

<!-- AUTO-GENERATED:DAILY_TOP10 -->

1. [Agentic World Modeling: Foundations, Capabilities, Laws, and Beyond](catalog/papers/2026-04-26/agentic-world-modeling-foundations-capabilities-laws-and-beyond.md) — agents. We introduce a "levels x laws" taxonomy organized along two axes.
2. [ArmSSL: Adversarial Robust Black-Box Watermarking for Self-Supervised Learning Pre-trained Encoders](catalog/papers/2026-04-26/armssl-adversarial-robust-black-box-watermarking-for-self-supervised-learning-pr.md) — safety alignment. We propose ArmSSL, an SSL watermarking framework that assures black-box verifiability and adversarial robustness while preserving utility.
3. [ATRS: Adaptive Trajectory Re-splitting via a Shared Neural Policy for Parallel Optimization](catalog/papers/2026-04-26/atrs-adaptive-trajectory-re-splitting-via-a-shared-neural-policy-for-parallel-op.md) — agents. The main contributions of this work are: • Adaptive Trajectory Re-splitting Framework: We formulate the adaptive structural adjustment for parallel trajectory optimization as a Multi-Agent RL problem for the first time.
4. [SOLAR-RL: Semi-Online Long-horizon Assignment Reinforcement Learning](catalog/papers/2026-04-26/solar-rl-semi-online-long-horizon-assignment-reinforcement-learning.md) — foundation models. Our main contributions are summarized as follows: • We propose SOLAR-RL, a framework that bridges the gap between offline training stability and online exploration by simulating dynamic feedback mechanisms within static datasets. • We introduce a trajectory-aware reward shaping mechanism that addresses the credit assignment problem by performing retroactive credit assignment via failure-point detection and target-aligned reward shaping, distilling trajectory-level execution quality into dense step-level rewards. • We achieve competitive performance with online/SFT baselines without interaction, specifically demonstrating superior robustness and generalization in complex, long-horizon tasks compared to strong baselines.
5. [Learning Evidence Highlighting for Frozen LLMs](catalog/papers/2026-04-26/learning-evidence-highlighting-for-frozen-llms.md) — foundation models. This motivates an explicit decoupling: rather than forcing a single solver to simultaneously sift through noise and reason, we introduce a lightweight module whose sole job is to surface evidence, allowing a powerful frozen solver to devote its capacity to reasoning.
6. [SpikingBrain2.0: Brain-Inspired Foundation Models for Efficient Long-Context and Cross-Platform Inference](catalog/papers/2026-04-26/spikingbrain2-0-brain-inspired-foundation-models-for-efficient-long-context-and.md) — foundation models. Recent breakthroughs in large-scale foundation models have been driven not only by the scaling of data and parameters but also by the rapid expansion of context windows (Anthropic, 2026; Team et al., 2024; Liu et al., 2025a; Team et al., 2025a; Blakeman et al., 2025; Team et al., 2026).
7. [Adversarial Co-Evolution of Malware and Detection Models: A Bilevel Optimization Perspective](catalog/papers/2026-04-26/adversarial-co-evolution-of-malware-and-detection-models-a-bilevel-optimization.md) — safety alignment. The remainder of this paper is organized as follows.
8. [PASR: Pose-Aware 3D Shape Retrieval from Occluded Single Views](catalog/papers/2026-04-26/pasr-pose-aware-3d-shape-retrieval-from-occluded-single-views.md) — safety alignment. To address this problem, we propose Pose-Aware 3D Shape Retrieval (PASR), a framework that formulates retrieval as a feature-level analysis-by-synthesis problem by distilling knowledge from a 2D foundation model (DINOv3) into a 3D encoder.
9. [Structure-Guided Diffusion Model for EEG-Based Visual Cognition Reconstruction](catalog/papers/2026-04-26/structure-guided-diffusion-model-for-eeg-based-visual-cognition-reconstruction.md) — neuroai. Overall, this work introduces a new structured decoding paradigm for EEG-based visual cognition reconstruction and provides fresh insights into the cognitive guidance mechanisms of multimodal generative models.
10. [Generative Modeling of Neurodegenerative Brain Anatomy with 4D Longitudinal Diffusion Model](catalog/papers/2026-04-26/generative-modeling-of-neurodegenerative-brain-anatomy-with-4d-longitudinal-diff.md) — neuroai. To address this problem, we propose a novel 4D (3DxT) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, conditioned on available clinical variables such as health status, age, sex, and other relevant factors.

## Topic Map

![Topic map](public/assets/topic_map.svg)

<!-- AUTO-GENERATED:TOPIC_INDEX -->

- [Foundation Models](catalog/topics/foundation_models/README.md) — 48 tracked papers
- [Agents & Tool Use](catalog/topics/agents/README.md) — 3 tracked papers
- [Evaluation & Benchmarks](catalog/topics/evaluation/README.md) — 13 tracked papers
- [Safety, Alignment & Robustness](catalog/topics/safety_alignment/README.md) — 10 tracked papers
- [Theory, Optimization & Statistical Learning](catalog/topics/theory_optimization/README.md) — 3 tracked papers
- [Reinforcement Learning](catalog/topics/reinforcement_learning/README.md) — 0 tracked papers
- [NeuroAI & Computational Neuroscience](catalog/topics/neuroai/README.md) — 2 tracked papers
- [Automated Research](catalog/topics/automated_research/README.md) — 0 tracked papers
- [Interpretability](catalog/topics/interpretability/README.md) — 1 tracked papers
- [Benchmark Design](catalog/topics/benchmarks/README.md) — 0 tracked papers

## How this works

Every day, a small pipeline checks paper sources, research feeds, and public research signals. It deduplicates papers, scores them by relevance and interestingness, saves selected metadata and PDFs locally, and publishes short public notes for the best items.

## Caveat

These are quick notes, not peer review. If something looks important, read the paper.

## Copyright

This repository publishes links, original summaries, and original generated visuals. PDFs, private reading artifacts, and figure reuse without clear permission stay out of the public catalog by default.

