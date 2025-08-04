---
title: "Zero-shot Retrieval With Priors"
weight: 1
mermaid: true
math: true
draft: false
date: 2025-07-13
---

# Introduction

Retrieval refers to searching for a response to a query from a large corpus of documents. In the context of information retrieval, it is often necessary to retrieve relevant documents or passages from a large collection based on a given query. This process is typically performed using various retrieval models that rank documents based on their relevance to the query.

Zero-shot retrieval refers to retrieval without any prior training. This might seem a daunting task at the outset, but it has been observed that simple sparse models like BM25 which use lexical similarity have been shown to have promising generalization capability. One way to measure this capability is to evaluate it on benchmarks such as BEIR.

The BEIR benchmark, introduced by [Thakur et al](#beir-leaderboard) is designed to evaluate information retrieval systems across diverse combinations of tasks and domains. It was designed to focus on the “zero-shot” retrieval setting, i.e., evaluation on tasks and domains without any training data or supervision signals.

# References

<a id = "beir-leaderboard">[1]</a> Resources for Brewing BEIR: Reproducible Reference Models and an Official Leaderboard. Ehsan Kamalloo, Nandan Thakur, Carlos Lassance, Xueguang Ma, Jheng-Hong Yang, & Jimmy Lin. (2023)
