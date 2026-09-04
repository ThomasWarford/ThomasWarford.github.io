---
layout: post
title:  "What is Hamiltonian Monte Carlo?"
date:   2022-08-09
description: "An intuitive introduction to Hamiltonian Monte Carlo: why simple MCMC struggles in high dimensions, and how treating parameters as particles rolling in a potential fixes it."
image: assets/images/hmc-intro/chains.png
math: true
---

<div class="editors-note">
    <strong>Editor's Note:</strong> This post was originally written for the PRACE Summer of HPC blog in August 2022, during my placement at the Hartree Centre. The original blog post can be found [here](https://web.archive.org/web/20260903190835/https://summerofhpc.prace-ri.eu/what-is-hamiltonian-monte-carlo/). The work ultimately resulted in [this conference paper](https://doi.org/10.1007/978-3-031-36030-5_48).
</div>

| ![HMC generating samples from a donut-shaped distribution]({{site.baseurl}}/assets/images/hmc-intro/donut.gif) |
|:--:| 
| *Elegant animation of HMC generating samples from a donut-shaped distribution, from [Tom Begley's blog post](https://tcbegley.com/blog/mcmc-part-2). Thanks for granting me permission to use it!* |

Generating random variables from an arbitrary distribution is a surprisingly difficult task, and Hamiltonian Monte Carlo (HMC) solves this challenge in an elegant way. Let's consider a multivariate target distribution $$\pi(\vec{q})$$, with parameters $$\vec{q}$$.

Most Markov Chain Monte Carlo (MCMC) methods work by generating the proposals for the next sample ($$\vec{q}_{n+1}$$) from the current sample ($$\vec{q}_n$$). For instance, an MCMC method could take a random Gaussian step in parameter space to get the next proposal. The proposal is then accepted or rejected with probability determined by the probability density at the current and the proposed positions. The rejection of samples at a lower density causes the walk to "stay on track", and for computational resources to be focused on the typical set, where the density of the target distribution is significant.

This simple MCMC method struggles with high-dimensional distributions, as the volume surrounding the typical set is much larger than the volume of the typical set, meaning most propositions are in areas of low density and are therefore rejected. This isn't very efficient. We can reduce the step-size to increase the acceptance rate, but this causes samples to be highly correlated.

This is where HMC steps in. Each point in the parameter space $$\vec{q}$$ is assigned a potential energy $$u(\vec{q})=-\ln{\pi(\vec{q})}$$. To concretize this, imagine a 2D Gaussian distribution $$\pi(q_1, q_2) = \exp(-q_1^2-q_2^2)$$. This has a bowl shaped parabolic potential energy function.

To go from one sample to the next, we give the "particle" a random momentum $$\vec{p}$$ and simulate the evolution of the system for a certain number of time-steps. To concretize this, imagine a hockey puck being given a random momentum in a large, parabolic bowl. In an ideal world, this method of generating proposals negates the need for an acceptance/rejection step, for reasons outlined in the references below. However, in reality, a small number of proposals are rejected due to numerical integration errors. Nonetheless, with a suitable time-step most proposals are accepted and samples have a lower correlation than those produced by simple MCMC.

Up until this point, Bruno and I have been working to implement and parallelize this algorithm with the help of our mentor Anton. In [the next post]({{site.baseurl}}/2022/09/15/multi-gpu-hamiltonian-monte-carlo.html) I talk about how we've been using jax, a python module which massively speeds up numpy on CPUs and GPUs.

| ![Two HMC chains exploring a potential]({{site.baseurl}}/assets/images/hmc-intro/chains.png) |
|:--:| 
| *Two HMC chains exploring a potential. Each chain runs on a different CPU core.* |

### References

- [Tom Begley's blog post](https://tcbegley.com/blog/mcmc-part-2) — thanks for granting me permission to use the animation above!
- Betancourt, M. (2017). [A Conceptual Introduction to Hamiltonian Monte Carlo](https://arxiv.org/abs/1701.02434). arXiv preprint arXiv:1701.02434.
