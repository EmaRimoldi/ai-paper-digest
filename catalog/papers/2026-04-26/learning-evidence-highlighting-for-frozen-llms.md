# Learning Evidence Highlighting for Frozen LLMs

*Shaoang Li · 2026-04-24 · foundation models · Must read*

[paper](http://arxiv.org/abs/2604.22565v1) / [pdf](https://arxiv.org/pdf/2604.22565v1)

## TL;DR

This motivates an explicit decoupling: rather than forcing a single solver to simultaneously sift through noise and reason, we introduce a lightweight module whose sole job is to surface evidence, allowing a powerful frozen solver to devote its capacity to reasoning.

## Main Contribution

This motivates an explicit decoupling: rather than forcing a single solver to simultaneously sift through noise and reason, we introduce a lightweight module whose sole job is to surface evidence, allowing a powerful frozen solver to devote its capacity to reasoning.

## Main Result

Across sequential recommendation and long-context question answering, HiLight consistently improves performance over strong prompt-based and automated prompt-optimization baselines.

## Method in Brief

We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.

## Summary by Section

### Abstract

Large Language Models (LLMs) can reason well, yet often miss decisive evidence when it is buried in long, noisy contexts. We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.

### Introduction and Problem

A useful perspective is that long-context failures often arise from coupling two distinct subproblems into a single forward pass: evidence selection, identifying a small set of task-relevant spans amid distractors, and reasoning, performing multi-step inference over the selected evidence.

### Method

We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers. We cast highlighting as a weakly supervised decisionmaking problem and optimize the Actor with reinforcement learning using only the Solver’s task reward, requiring no evidence labels and no access to or modification of the Solver.

### Evaluation and Results

This section evaluates HiLight on long-context tasks spanning different evidence sparsity and distractor regimes. Our goals are to (i) quantify end-to-end gains over strong prompt-optimization baselines, (ii) test whether non-destructive emphasis is essential (vs. pruning), and (iii) assess robustness to budgets, marker formats, and Solver choice.

### Limitations

Empirical studies have documented this failure mode, including the “Lost in the Middle” effect, where models attend less reliably to information that is neither near the beginning nor the end of a long input Liu et al. (2024). A useful perspective is that long-context failures often arise from coupling two distinct subproblems into a single forward pass: evidence selection, identifying a small set of task-relevant spans amid distractors, and reasoning, performing multi-step inference over the selected evidence.

### Conclusion

We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers. HiLight avoids compressing or rewriting the input, which can discard or distort evidence, by training a lightweight Emphasis Actor to insert minimal highlight tags around pivotal spans in the unaltered context.

## Caveats

Empirical studies have documented this failure mode, including the “Lost in the Middle” effect, where models attend less reliably to information that is neither near the beginning nor the end of a long input Liu et al. (2024).

## Quick Facts

- First author: Shaoang Li
- Primary topic: foundation models
- Secondary topics: theory optimization, reinforcement learning
- Fit: Medium
- Summary source: local PDF text
