---
authors:
  - ptuemmler
categories:
  - Mathematics
tags:
  - Calculus
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

Where \( f^{(n)}(a) \) is the \( n \)-th derivative of \( f \) evaluated at point \( a \) and \( n! \) is the factorial of \( n \).

If the expansion is centered at \( a = 0 \), it is called a **Maclaurin series**.

### Example: Exponential Function

The Taylor series for \( e^x \) centered at \( a = 0 \) is:

\[
e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots = \sum_{n=0}^{\infty} \frac{x^n}{n!}
\]

### Example: Sine Function
The Taylor series for \( \sin(x) \) centered at \( a = 0 \) is:

\[
\sin(x) = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \frac{x^7}{7!} + \cdots = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!}
\]


### Example: Cosine Function
The Taylor series for \( \cos(x) \) centered at \( a = 0 \) is:

\[
\cos(x) = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \frac{x^6}{6!} + \cdots = \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!}
\]
