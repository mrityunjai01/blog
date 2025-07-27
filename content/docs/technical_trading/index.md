---
title: "Snooping in Technical Trading"
weight: 1
mermaid: true
math: true
draft: false
date: 2024-10-13
---

<!-- markdownlint-disable MD025 MD013 -->

# Introduction

Technical Trading is defined by the exclusive use of data from past prices and volumes to make trading decisions. It has been widely contested that technical trading doesn't outperform major benchmarks owing to the weak form of the Efficient Market Hypothesis (EMH). However, there are many who believe that technical trading can be profitable, especially when combined with other methods such as fundamental analysis or machine learning. This is especially true when some strategies outperform benchmarks in back-test, leading researchers to claim that those strategies are profitable.

In this post, I will show that there are certain conditions on the time series price signal which can be exploited to make profitable trades. I will also show how it is possible to detect data snooping when selecting a performant strategy. I will also show that the profitability of technical trading is not necessarily due to the exploitation of market inefficiencies, but rather due to the exploitation of the time series properties of the price signal itself. This means that I to restrict the universe of my analysis to technical trading strategies which only use past prices as inputs to trading decisions. This excludes most strategies which use fundamental data or even data from other assets, as is the case in Statistical Arbitrage strategies.
