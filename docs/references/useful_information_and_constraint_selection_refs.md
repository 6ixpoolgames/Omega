# Useful Information And Constraint Selection References

Status: reference archive
Scope: bibliographic records for the bounded-useful-structure adapter batch

This note archives stable source records for the two papers used in the
bounded-useful-structure adapter update. PDF copies are not vendored in this
repository in this pass; the authoritative versioned PDFs remain linked through
arXiv. If the project later needs local PDF mirrors, check each paper's current
license and add the copied file with a license note next to it.

## Bennett 2024

Michael Timothy Bennett, "Is Complexity an Illusion?", arXiv:2404.07227
[cs.AI], version 4, last revised 2024-05-30.

Source links:

- Abstract page: <https://arxiv.org/abs/2404.07227>
- Versioned citation DOI: <https://doi.org/10.48550/arXiv.2404.07227>
- arXiv PDF: <https://arxiv.org/pdf/2404.07227>

Repo-use summary:

The paper motivates a guardrail against treating simple form or complexity as
the causal source of generalization. For this repo, the imported lesson is:
test the declared functional constraint or recovery target directly; do not
trust a complexity/simple-form summary unless the target factors through it.

## Finzi Et Al. 2026

Marc Finzi, Shikai Qiu, Yiding Jiang, Pavel Izmailov, J. Zico Kolter, and
Andrew Gordon Wilson, "From Entropy to Epiplexity: Rethinking Information for
Computationally Bounded Intelligence", arXiv:2601.03220 [cs.LG], version 2,
last revised 2026-03-16.

Source links:

- Abstract page: <https://arxiv.org/abs/2601.03220>
- Versioned citation DOI: <https://doi.org/10.48550/arXiv.2601.03220>
- arXiv PDF: <https://arxiv.org/pdf/2601.03220>
- Code link from arXiv page: <https://github.com/mfinzi/epiplexity>

Repo-use summary:

The paper motivates a guardrail against treating Shannon entropy, Kolmogorov
complexity, or unordered distribution summaries as sufficient measures of
useful information for bounded systems. For this repo, the imported lesson is:
make bounded observer/decoder classes explicit, retain ordering-sensitive
counterexamples, and treat raw entropy as a proxy that must pass
non-factorization and recovery audits.
