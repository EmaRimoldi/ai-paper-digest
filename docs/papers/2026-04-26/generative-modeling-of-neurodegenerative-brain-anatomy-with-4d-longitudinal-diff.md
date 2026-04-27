# Generative Modeling of Neurodegenerative Brain Anatomy with 4D Longitudinal Diffusion Model

*Nivetha Jayakumar · 2026-04-24 · neuroai · Skim*

[paper](http://arxiv.org/abs/2604.22700v1) / [pdf](https://arxiv.org/pdf/2604.22700v1)

## TL;DR

To address this problem, we propose a novel 4D (3DxT) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, conditioned on available clinical variables such as health status, age, sex, and other relevant factors.

## Main Contribution

To address this problem, we propose a novel 4D (3DxT) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, conditioned on available clinical variables such as health status, age, sex, and other relevant factors.

## Main Result

Experimental results demonstrate that our method excels at generating longitudinal sequences with preserved anatomical structure and shape, outperforming state-of-theart diffusion models that operate in the pixel space, as well as recursive models that synthesize missing time points using multi-frame guidance.

## Method in Brief

We validate our model through both synthetic sequence generation and downstream longitudinal disease classification, as well as brain segmentation.

## Summary by Section

### Abstract

Understanding and predicting the progression of neurodegenerative diseases remains a major challenge in medical AI, with significant implications for early diagnosis, disease monitoring, and treatment planning. However, most available longitudinal neuroimaging datasets are temporally sparse with a few follow-up scans per subject.

### Introduction and Problem

Understanding and predicting the progression of neurodegenerative diseases remains a major challenge in medical AI, with significant implications for early diagnosis, disease monitoring, and treatment planning. To address this problem, we propose a novel 4D (3DxT) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, conditioned on available clinical variables such as health status, age, sex, and other relevant factors.

### Method

To address this problem, we propose a novel 4D (3D×T) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, con- ∗These authors contribute equally to this work. [cs.CV] 24 Apr 2026 ditioned on available clinical variables such as health status, age, sex, and other relevant factors. Moreover, while most current approaches focus on manipulating image intensity or texture, our method explicitly learns the data distribution of topology-preserving spatiotemporal deformations to effectively capture the geometric changes of brain structures over time.

### Evaluation and Results

Experiments on two large-scale longitudinal neuroimage datasets demonstrate that our method outperforms state-of-the-art baselines in generating anatomically accurate, temporally consistent, and clinically meaningful brain trajectories. Experimental results demonstrate that our method excels at generating longitudinal sequences with preserved anatomical structure and shape, outperforming state-of-theart diffusion models that operate in the pixel space, as well as recursive models that synthesize missing time points using multi-frame guidance.

### Limitations

However, most available longitudinal neuroimaging datasets are temporally sparse with a few follow-up scans per subject. However, longitudinal neuroimaging data are often temporally sparse, incomplete, or entirely unavailable due to challenges such as high imaging costs, patient dropout, and the difficulty of conducting repeated scans over extended study periods [37, 39].

### Conclusion

To address this problem, we propose a novel 4D (3D×T) diffusion-based generative framework that effectively models and synthesizes longitudinal brain anatomy over time, con- ∗These authors contribute equally to this work. [cs.CV] 24 Apr 2026 ditioned on available clinical variables such as health status, age, sex, and other relevant factors. In this paper, we propose a novel 4D longitudinal diffusion model in the time-sequential deformation space of brain images.

## Caveats

However, most available longitudinal neuroimaging datasets are temporally sparse with a few follow-up scans per subject.

## Quick Facts

- First author: Nivetha Jayakumar
- Primary topic: neuroai
- Secondary topics: none
- Fit: Low
- Summary source: local PDF text
