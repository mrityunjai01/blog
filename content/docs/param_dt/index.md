---
title: "Continuously Parametrizing Decision Trees"
weight: 1
mermaid: true
math: true
draft: false
date: 2025-03-11
---

There have been a lot of efforts into parametrizing decision trees in a continuous fashion, that is, making the tree's prediction continuous with respect to its parameters. This is important because it is a first step towards differentiability of trees, which could result in an SGD optimization for fitting trees. However, most such efforts have failed because of some very fundamental problems in the definition of the decision trees' architecture. This makes a parametrization very difficult unless we drop architectural constraints.

One such approach (unpublished, due to Prof Garg), holds some potential.
