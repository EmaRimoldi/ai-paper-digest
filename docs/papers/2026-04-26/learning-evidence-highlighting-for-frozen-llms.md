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
image: ../../../public/assets/paper_cards/learning-evidence-highlighting-for-frozen-llms.svg
---

# Learning Evidence Highlighting for Frozen LLMs

![Paper card](../../../public/assets/paper_cards/learning-evidence-highlighting-for-frozen-llms.svg)

## TL;DR

Large Language Models (LLMs) can reason well, yet often miss decisive evidence when it is buried in long, noisy contexts.

## What it contributes

- We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.
- HiLight avoids compressing or rewriting the input, which can discard or distort evidence, by training a lightweight Emphasis Actor to insert minimal highlight…
- A frozen Solver then performs downstream reasoning on the emphasized input.

## Key results

- We introduce HiLight, an Evidence Emphasis framework that decouples evidence selection from reasoning for frozen LLM solvers.
- HiLight avoids compressing or rewriting the input, which can discard or distort evidence, by training a lightweight Emphasis Actor to insert minimal highlight…
- A frozen Solver then performs downstream reasoning on the emphasized input.

## Method in brief

Large Language Models (LLMs) can reason well, yet often miss decisive evidence when it is buried in long, noisy contexts.

## Caveats

Summary based on abstract/metadata only.

## Links

- Paper: http://arxiv.org/abs/2604.22565v1
- PDF: https://arxiv.org/pdf/2604.22565v1
- Code/project: 
