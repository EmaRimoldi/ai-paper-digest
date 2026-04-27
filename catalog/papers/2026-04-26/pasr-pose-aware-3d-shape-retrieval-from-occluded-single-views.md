# PASR: Pose-Aware 3D Shape Retrieval from Occluded Single Views

*Jiaxin Shi · 2026-04-24 · safety alignment · Skim*

[paper](http://arxiv.org/abs/2604.22658v1) / [pdf](https://arxiv.org/pdf/2604.22658v1)

## TL;DR

To address this problem, we propose Pose-Aware 3D Shape Retrieval (PASR), a framework that formulates retrieval as a feature-level analysis-by-synthesis problem by distilling knowledge from a 2D foundation model (DINOv3) into a 3D encoder.

## Main Contribution

To address this problem, we propose Pose-Aware 3D Shape Retrieval (PASR), a framework that formulates retrieval as a feature-level analysis-by-synthesis problem by distilling knowledge from a 2D foundation model (DINOv3) into a 3D encoder.

## Main Result

PASR substantially outperforms existing methods on both clean and occluded 3D shape retrieval datasets by a wide margin.

## Method in Brief

Existing approaches largely fall into two categories: those using contrastive learning to map point cloud features into existing vision-language spaces and those that learn a common embedding space for 2D images and 3D shapes.

## Summary by Section

### Abstract

Single-view 3D shape retrieval is a fundamental yet challenging task that is increasingly important with the growth of available 3D data. Existing approaches largely fall into two categories: those using contrastive learning to map point cloud features into existing vision-language spaces and those that learn a common embedding space for 2D images and 3D shapes.

### Introduction and Problem

Single-view 3D shape retrieval is a fundamental yet challenging task that is increasingly important with the growth of available 3D data. To address this problem, we propose Pose-Aware 3D Shape Retrieval (PASR), a framework that formulates retrieval as a feature-level analysis-by-synthesis problem by distilling knowledge from a 2D foundation model (DINOv3) into a 3D encoder.

### Method

Existing approaches largely fall into two categories: those using contrastive learning to map point cloud features into existing vision-language spaces and those that learn a common embedding space for 2D images and 3D shapes. To address this problem, we propose Pose-Aware 3D Shape Retrieval (PASR), a framework that formulates retrieval as a feature-level analysis-by-synthesis problem by distilling knowledge from a 2D foundation model (DINOv3) into a 3D encoder.

### Evaluation and Results

PASR substantially outperforms existing methods on both clean and occluded 3D shape retrieval datasets by a wide margin. PASR achieves competitive clean, occluded, and unseen 3D shape retrieval from single images, while also enabling multitasking with accurate category classification and pose estimation. view is a key enabler for inverse graphics [46]. While these approaches excel on synthetic benchmarks, their generalization to real-world images is limited.

### Limitations

will focus on generalizing this framework to diverse meshes across more categories and exploiting its capabilities for more downstream 3D tasks in the real world.

### Conclusion

will focus on generalizing this framework to diverse meshes across more categories and exploiting its capabilities for more downstream 3D tasks in the real world.

## Caveats

Fast note from local PDF text. Verify claims and limitations directly in the paper.

## Quick Facts

- First author: Jiaxin Shi
- Primary topic: safety alignment
- Secondary topics: theory optimization, foundation models
- Fit: Medium
- Summary source: local PDF text
