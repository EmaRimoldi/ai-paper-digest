# ArmSSL: Adversarial Robust Black-Box Watermarking for Self-Supervised Learning Pre-trained Encoders

*Yongqi Jiang · 2026-04-24 · safety alignment · Must read*

[paper](http://arxiv.org/abs/2604.22550v1) / [pdf](https://arxiv.org/pdf/2604.22550v1)

## TL;DR

We propose ArmSSL, an SSL watermarking framework that assures black-box verifiability and adversarial robustness while preserving utility.

## Main Contribution

We propose ArmSSL, an SSL watermarking framework that assures black-box verifiability and adversarial robustness while preserving utility.

## Main Result

SSL has achieved remarkable success in fields such as computer vision (CV) [2], natural language processing (NLP) [3], and autonomous driving [4].

## Method in Brief

The emerging SSL ownership verification, mainly focusing on encoder watermarking, is underexplored to date, with only limited works [6], [8]–[10].

## Summary by Section

### Abstract

Self-supervised learning (SSL) encoders are invaluable intellectual property (IP). However, no existing SSL watermarking for IP protection can concurrently satisfy the following two practical requirements: (1) provide ownership verification capability under black-box suspect model access once the stolen encoders are used in downstream tasks; (2) be robust under adversarial watermark detection or removal, because the watermark samples form a distinguishable out-of-distribution (OOD) cluster.

### Introduction and Problem

Self-supervised learning (SSL) encoders are invaluable intellectual property (IP). However, no existing SSL watermarking for IP protection can concurrently satisfy the following two practical requirements: (1) provide ownership verification capability under black-box suspect model access once the stolen encoders are used in downstream tasks; (2) be robust under adversarial watermark detection or removal, because the watermark samples form a distinguishable out-of-distribution (OOD) cluster.

### Method

The emerging SSL ownership verification, mainly focusing on encoder watermarking, is underexplored to date, with only limited works [6], [8]–[10]. For example, Wu et al. [10] proposed a backdoorbased watermarking method that maximizes the representation discrepancy between watermarked and clean encoders on trigger-carrying inputs to induce downstream classifiers to misclassify them into the same class consistently.

### Evaluation and Results

SSL has achieved remarkable success in fields such as computer vision (CV) [2], natural language processing (NLP) [3], and autonomous driving [4]. The former pulls watermark representations toward anchors located at the representation centers of all rest non-source classes, entangling watermark and clean representations (i.e., of non-source classes) to reduce intra-watermark density, avoiding forming a dense watermark cluster. A key innovation of MoCo v2 is its use of a momentum encoder to maintain a dynamic queue of negative examples, which allows it to achieve higher representation accuracy and better convergence stability than SimCLR even with a smaller batch size and fewer epochs.

### Limitations

However, no existing SSL watermarking for IP protection can concurrently satisfy the following two practical requirements: (1) provide ownership verification capability under black-box suspect model access once the stolen encoders are used in downstream tasks; (2) be robust under adversarial watermark detection or removal, because the watermark samples form a distinguishable out-of-distribution (OOD) cluster. However, this paradigm also introduces IP infringement risks, which generally fall into two scenarios.

### Conclusion

Overall, existing SSL watermarking schemes are restricted to a single verification context (e.g., EaaS or MLaaS), lacking a unified verification capability across both scenarios.

## Caveats

However, no existing SSL watermarking for IP protection can concurrently satisfy the following two practical requirements: (1) provide ownership verification capability under black-box suspect model access once the stolen encoders are used in downstream tasks; (2) be robust under adversarial watermark detection or removal, because the watermark samples form a distinguishable out-of-distribution (OOD) cluster.

## Quick Facts

- First author: Yongqi Jiang
- Primary topic: safety alignment
- Secondary topics: evaluation
- Fit: Medium
- Summary source: local PDF text
