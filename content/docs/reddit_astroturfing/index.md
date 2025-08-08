---
title: "Reddit Astroturfing: A Bayesian Approach"
weight: 1
mermaid: true
math: true
draft: false
date: 2025-03-11
---

## Introduction

We've all come across reddit posts with controversial or opinionated claims and are surprised by the number of supporting comments they receive. At times, this is merely a function of genuine support for contrarian viewpoints. However, if I come across the same small subset of users promoting a particular narrative, I sometimes begin to question if there's a bit of a systematic component to it. There is some chance that a group of users collude to write group-affirming comments, perhaps supported or controlled by a single entity. This is usually suspicious if there's very little activity from such astroturfing users apart from such posts.

In this post, I aim to describe a Bayesian Inference approach which handles the problem of detecting such coordinated commenting behavior on reddit posts. The model is designed to differentiate between genuine user engagement and potential astroturfing activity, while accounting for the natural variation in post popularity and user commenting behavior.

We have to be careful to differentiate this from other non-offending posts which receive a large number of broadly interested community members, which might also coincidentally receive comments from astroturfing users. There needs to be a way to properly measure the certainty with which we can claim that a given set of users is astroturfing. Not just that, it'd be helpful if we could get all subsets of astroturfing users. I have attached a python notebook which showcases a three step approach to this problem using STAN for bayesian modelling.

A common approach used to detect such manipulative activity is to use timestamp data to filter out manipulative activity which took place in a short span of time. This is particularly useful when there's a long persisting interaction with content, such as in Online Shopping reviews, or Yelp reviews. However, this is not effective and misses a lot of activity on social media comment sections which anyways happens in a short span of time.

## Intuition

There are two things we need to take care of:

1. There are certain posts with high participation from the community. On such posts, we might observe a lot of coincidental simultaneous involvement from unrelated users. Our model should be able to learn this probabilistic behaviour of comment-post interaction. This also holds true for posts with low participation, where simultaneous involvement is more suspicious than in the case of high participation posts.
2. There are some commenters who comment on a lot of posts, and some who comment on very few. We need to account for this in our model, so that we can differentiate between a users who are colluding and ones who are indiscriminately commenting on posts.

So all in all, we only want to flag subsets of commenters who seem to be commenting on unpopular posts, which possibly are one of the very few posts that they comment on. We want both of these conditions met to some degree.

## Method

We start with a simple webscraper that collects posts and comments from a given subreddit. We collect all posts made in the past week for illustration.
Here's an illustrious example of posts taken from [ethereum subreddit](https://www.reddit.com/r/ethereum/top/?t=week). For each such post, we collect a list of commenter user ids, for commenters who wrote comments on the post.

<img src="images/im1.png" alt="Ethereum Top Posts" width="600">

1. We mine frequent itemsets from a set of commenter id sets for each post from the set of posts. That is for each post, we collect the commenter user ids into a set. We further mine a set of commentor ids which most frequently simultaneously comment on posts. This is done using a prefix tree algorithm.

2. We construct a bayesian model for the each poster-commenter interaction. If there are `S` posts and `N` commenters, we have `N X S` numbers to model using independent post-wise params and independent commenter-wise params.

3. We run posterior simulations to obtain a sample of posterior parameters, alpha and beta. For each such draw of posterior parameters, we run a random variable draw to populate the original `y` matrix. This set of posterior predictions is processed to find the number of posterior predictions where the comments of interest appear together, giving us a sample of simultaneity frequencies. We then describe the position of the observed simultaneity frequency from the original `y` in the sample of simultaneity frequency draws. If this observed frequency is greater than the 99th percentile among the posterior predictive frequencies, we claim that it is inconsistent with a model of independent decisions, and the commenters might have colluded (astroturfing).

## Reasoning

This hierarchical Bayesian model addresses the challenge of detecting coordinated commenting behavior while accounting for natural variation in both post popularity and user activity levels.

### Key Design Rationale

- Post-Specific Effects (alpha): The model incorporates post-specific logit intercepts to capture the inherent "attractiveness" or engagement level of individual posts. High-participation posts naturally generate more simultaneous comments from unrelated users, making coincidental overlap common and less suspicious. Conversely, low-participation posts have lower baseline engagement, so simultaneous commenting becomes more indicative of potential coordination rather than organic interest.
- User-Specific Effects (beta): Commentor-specific parameters account for individual propensities to comment across the platform. Some users are naturally prolific commenters who engage with many posts indiscriminately, while others are selective participants. By modeling these baseline tendencies, the model can distinguish between users who comment together frequently due to high individual activity rates versus those whose joint participation exceeds what would be expected from their individual behaviors alone.
- Hierarchical Structure: The inclusion of additional commenting data (y_rem) through the hierarchical prior prevents overfitting to the specific posts under investigation. This allows the model to learn realistic baseline commenting probabilities from a broader sample of user behavior, providing better context for evaluating whether observed co-commenting patterns are suspicious or within normal bounds.

## Program

Here's the stan program we use for modelling comment behaviour.

```stan
data {
int<lower=1> N;
 int<lower=1> S;
 int<lower=1> R;
 array[S, N] int<lower=0,upper=1> y;
array[S] int<lower=0> y_rem;
}

parameters {
vector[N] alpha; // item-specific logit intercepts
vector[S] beta; // subset-specific effects
real mu_alpha; // hyperprior mean for item effects
real<lower=0> sigma_alpha; // hyperprior sd for item effects
real mu_beta;
real<lower=0> sigma_beta;
real alpha_0;
real mu_alpha_0;
real<lower=0> sigma_alpha_0;

}

model {
// Hyperpriors
mu_alpha ~ normal(0, 1);
sigma_alpha ~ exponential(1);
mu_beta ~ normal(0, 1);
sigma_beta ~ exponential(1);
mu_alpha_0 ~ normal(0, 1);
sigma_alpha_0 ~ exponential(1);

// Hierarchical priors
alpha_0 ~ normal(mu_alpha_0, sigma_alpha_0);
alpha ~ normal(alpha_0, sigma_alpha);
beta ~ normal(mu_beta, sigma_beta);

// Likelihood
for (s in 1:S) {
for (n in 1:N) {
y[s,n] ~ bernoulli_logit(alpha[n] + beta[s]);
}
y_rem[s] ~ binomial(R, inv_logit(alpha_0 + beta[s]));
}
}

```

This Stan program implements a hierarchical Bayesian model to analyze commenting patterns between users and posts, incorporating both observed and unobserved commenting behavior.

### Model Structure

The model assumes that the probability of commentor `s` commenting on post `n` follows a Bernoulli distribution with logit-linear predictors combining post-specific and commentor-specific effects.

### Data Variables

1. **N** (`int<lower=1>`): Number of posts in the observed dataset
2. **S** (`int<lower=1>`): Number of commentors being studied
3. **R** (`int<lower=1>`): Number of additional posts not in the main dataset (used for hierarchical modeling)
4. **y** (`array[S, N] int<lower=0,upper=1>`): Binary comment matrix where `y[s,n] = 1` if commentor `s` commented on post `n`, 0 otherwise
5. **y_rem** (`array[S] int<lower=0>`): Count of comments each commentor `s` made on the `R` additional posts

### Parameters

6. **alpha** (`vector[N]`): Post-specific logit intercepts representing each post's baseline propensity to receive comments
7. **beta** (`vector[S]`): Commentor-specific logit effects representing each commentor's baseline propensity to comment
8. **mu_alpha** (`real`): Population mean for post effects (unused in current specification)
9. **sigma_alpha** (`real<lower=0>`): Population standard deviation for post effects
10. **mu_beta** (`real`): Population mean for commentor effects
11. **sigma_beta** (`real<lower=0>`): Population standard deviation for commentor effects
12. **alpha_0** (`real`): Baseline post effect for the additional `R` posts
13. **mu_alpha_0** (`real`): Prior mean for baseline post effect
14. **sigma_alpha_0** (`real<lower=0>`): Prior standard deviation for baseline post effect

### Prior Distributions

15. **mu_alpha** ~ Normal(0, 1)
16. **sigma_alpha** ~ Exponential(1)
17. **mu_beta** ~ Normal(0, 1)
18. **sigma_beta** ~ Exponential(1)
19. **mu_alpha_0** ~ Normal(0, 1)
20. **sigma_alpha_0** ~ Exponential(1)
21. **alpha_0** ~ Normal(mu_alpha_0, sigma_alpha_0)
22. **alpha[n]** ~ Normal(alpha_0, sigma_alpha) for n = 1, ..., N
23. **beta[s]** ~ Normal(mu_beta, sigma_beta) for s = 1, ..., S

### Likelihood Distributions

24. **y[s,n]** ~ Bernoulli_logit(alpha[n] + beta[s]) for s = 1, ..., S and n = 1, ..., N
25. **y_rem[s]** ~ Binomial(R, inv_logit(alpha_0 + beta[s])) for s = 1, ..., S

The hierarchical structure allows information from the additional posts (`y_rem`) to inform the prior distribution for the observed post effects (`alpha`) through the shared baseline `alpha_0`.
