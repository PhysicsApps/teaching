---
authors:
  - ptuemmler
categories:
  - Mathematics
tags:
  - Matplotlib
date: 2025-07-03
hide:
  - toc
---
# Taylor Expansions

The Taylor expansion is a fundamental concept in calculus for approximating functions using polynomials. It leverages the power of derivatives to express a function locally as an infinite sum, making it easier to compute and analyze in many practical scenarios.
<!-- more -->

{{embed_app("100%", "500px")}}

## Definition

Given a function \( f(x) \) that is infinitely differentiable at a point \( a \), the **Taylor series** of \( f(x) \) about the point \( a \) is given by:

\[
f(x) = f(a) + f'(a)(x - a) + \frac{f''(a)}{2!}(x - a)^2 + \frac{f^{(3)}(a)}{3!}(x - a)^3 + \cdots
\]

Or more compactly,

\[
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x - a)^n
\]

Where:
  - \( f^{(n)}(a) \) is the \( n \)-th derivative of \( f \) evaluated at point \( a \)
  - \( n! \) is the factorial of \( n \)
  - \( (x - a)^n \) is the \( n \)-th power of \( (x - a) \)

If the expansion is centered at \( a = 0 \), it is called a **Maclaurin series**.


## How It Works

The Taylor expansion builds a polynomial that approximates a function near a specific point \( a \). Each term in the expansion improves the approximation by incorporating more information about the function's derivatives at that point.

### Example: Exponential Function

The Taylor series for \( e^x \) centered at \( a = 0 \) (Maclaurin series) is:

\[
e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots = \sum_{n=0}^{\infty} \frac{x^n}{n!}
\]

This series converges to \( e^x \) for all real values of \( x \).


## Convergence and Accuracy

Not all Taylor series converge to the function they represent. The accuracy of a Taylor approximation depends on:
- The number of terms used (more terms generally mean higher accuracy)
- How close \( x \) is to the expansion point \( a \)
- Whether the function is analytic (i.e. equal to its Taylor series in a neighborhood of \( a \))

For practical purposes, we often truncate the series after a finite number of terms. The **remainder term** estimates the error introduced by this truncation.

