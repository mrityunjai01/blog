---
title: "Can Machines Search for Omitted Variables"
weight: 1
mermaid: true
math: true
draft: false
date: 2024-10-13
---

<!-- markdownlint-disable MD025 MD013 -->

There's some consensus that a lot of methods which are used to detect omitted variables don't worka well if the omitted feature is not correlated with the covariates. This causes a problem when trying to detect possible omission of variables. In this post, I will show that even if we know that there is omission, we can't identify omitted variables by only using analytical methods. We need to bring practical information in to ascertain causality, we're otherwise left with a set of possible correlated variables.

I'll first summarize detection methods for omitted variables in a multiple regression setting.
