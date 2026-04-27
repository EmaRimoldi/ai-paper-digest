---
title: 'ArmSSL: Adversarial Robust Black-Box Watermarking for Self-Supervised Learning
  Pre-trained Encoders'
authors:
- Yongqi Jiang
date: '2026-04-26'
primary_topic: safety_alignment
secondary_topics:
- evaluation
priority: Must read
fit_score: Medium
links:
  paper: http://arxiv.org/abs/2604.22550v1
  pdf: https://arxiv.org/pdf/2604.22550v1
  code: ''
  project: ''
image: ../../../assets/paper_cards/armssl-adversarial-robust-black-box-watermarking-for-self-supervised-learning-pr.svg
---

# ArmSSL: Adversarial Robust Black-Box Watermarking for Self-Supervised Learning Pre-trained Encoders

![Paper card](../../../assets/paper_cards/armssl-adversarial-robust-black-box-watermarking-for-self-supervised-learning-pr.svg)

## TL;DR

We propose ArmSSL, an SSL watermarking framework that assures black-box verifiability and adversarial robustness while preserving utility.

## What it contributes

- We propose ArmSSL, an SSL watermarking framework that assures black-box verifiability and adversarial robustness while preserving utility.
- Forutility, a reference-guided watermark tuning strategy is designed to allow the watermark to be learned as a small side task without affecting the main task by aligning the watermarked encoder’s outputs with those of the original clean e…
- It looks relevant to safety alignment and is a plausible candidate for a first-pass read.

## Key results

- SSL has achieved remarkable success in fields such as computer vision (CV) [2], natural language processing (NLP) [3], and autonomous driving [4].
- The former pulls watermark representations toward anchors located at the representation centers of all rest non-source classes, entangling watermark and clean representa…
- A key innovation of MoCo v2 is its use of a momentum encoder to maintain a dynamic queue of negative examples, which allows it to achieve higher representation accuracy…

## Method in brief

Forutility, a reference-guided watermark tuning strategy is designed to allow the watermark to be learned as a small side task without affecting the main task by aligning the watermarked encoder’s outputs with those of the original clean e…

## Caveats

However, no existing SSL watermarking for IP protection can concurrently satisfy the following two practical requirements: (1) provide ownership verification capability under black-box suspect model access once the stol…

## Links

- Paper: http://arxiv.org/abs/2604.22550v1
- PDF: https://arxiv.org/pdf/2604.22550v1
- Code/project: 
