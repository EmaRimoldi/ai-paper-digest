---
title: Learning Evidence Highlighting for Frozen LLMs
authors:
- Shaoang Li
- Yanhang Shi
- Yufei Li
- Mingfu Liang
- Xiaohan Wei
- Yunchen Pu
- Fei Tian
- Chonglin Sun
- Frank Shyu
- Luke Simon
- Sandeep Pandey
- Xi Liu
- Jian Li
date: '2026-04-26'
primary_topic: foundation_models
secondary_topics:
- theory_optimization
- reinforcement_learning
priority: Must read
fit_score: Medium
links:
  paper: http://arxiv.org/abs/2604.22565v1
  pdf: https://arxiv.org/pdf/2604.22565v1
  code: ''
  project: ''
image: ../../../assets/paper_cards/learning-evidence-highlighting-for-frozen-llms.svg
---

# Learning Evidence Highlighting for Frozen LLMs

![Paper card](../../../assets/paper_cards/learning-evidence-highlighting-for-frozen-llms.svg)

## TL;DR

We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.

## What it contributes

- We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.
- We cast highlighting as a weakly supervised decision-making problem and optimize the Actor with reinforcement learning using only the Solver's task reward, requiring no evidence labels and no access to or modification of the Solver.
- It looks relevant to foundation models and is a plausible candidate for a first-pass read.

## Key results

- Across sequential recommendation and long-context question answering, HiLight consistently improves performance over strong prompt-based and automated prompt-optimizatio…

## Method in brief

We cast highlighting as a weakly supervised decision-making problem and optimize the Actor with reinforcement learning using only the Solver's task reward, requiring no evidence labels and no access to or modification of the Solver.

## Caveats

Fast note from local PDF text. Verify claims and limitations directly in the paper.

## Links

- Paper: http://arxiv.org/abs/2604.22565v1
- PDF: https://arxiv.org/pdf/2604.22565v1
- Code/project: 
