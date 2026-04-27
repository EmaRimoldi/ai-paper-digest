---
title: 'SpikingBrain2.0: Brain-Inspired Foundation Models for Efficient Long-Context
  and Cross-Platform Inference'
authors:
- Yuqi Pan
- Jinghao Zhuang
- Yupeng Feng
- Fangzhi Zhong
- Siyu Ding
- Xuerui Qiu
- Shaowei Gu
- Bohan Sun
- Zhiyong Qin
- Yibo Zhong
- Lingtao Ouyang
- Kun Yang
- Zehao Liu
- Yuhong Chou
- Shurong Wang
- Anjie Hu
- Han Xu
- Bo Xu
- Guoqi Li
date: '2026-04-26'
primary_topic: foundation_models
secondary_topics:
- neuroai
priority: Must read
fit_score: Medium
links:
  paper: http://arxiv.org/abs/2604.22575v1
  pdf: https://arxiv.org/pdf/2604.22575v1
  code: ''
  project: ''
image: ../../../assets/paper_cards/spikingbrain2-0-brain-inspired-foundation-models-for-efficient-long-context-and.svg
---

# SpikingBrain2.0: Brain-Inspired Foundation Models for Efficient Long-Context and Cross-Platform Inference

![Paper card](../../../assets/paper_cards/spikingbrain2-0-brain-inspired-foundation-models-for-efficient-long-context-and.svg)

## TL;DR

We introduce SpikingBrain2.0 (SpB2.0), a 5B model that advances both architecture and training efficiency of its predecessor.

## What it contributes

- We introduce SpikingBrain2.0 (SpB2.0), a 5B model that advances both architecture and training efficiency of its predecessor.
- SpB2.0 further supports dual quantization paths: INT8-Spiking coding enables sparse event-driven computation, while FP8 coding accelerates inference on modern GPUs. (2) Enhanced Training Strategy: We develop an optimized Transformer-to-Hyb…
- It looks relevant to foundation models and is a plausible candidate for a first-pass read.

## Key results

- SpB2.0 achieves a 10.13x TTFT speedup at 4M context and supports over 10M tokens on 8 A100 GPUs under vLLM, where full-attention models exceed memory limits.

## Method in brief

SpB2.0 further supports dual quantization paths: INT8-Spiking coding enables sparse event-driven computation, while FP8 coding accelerates inference on modern GPUs. (2) Enhanced Training Strategy: We develop an optimized Transformer-to-Hyb…

## Caveats

A key challenge is to design foundation models that maintain performance and long-context efficiency with minimal training overhead.

## Links

- Paper: http://arxiv.org/abs/2604.22575v1
- PDF: https://arxiv.org/pdf/2604.22575v1
- Code/project: 
