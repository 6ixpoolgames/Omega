# Project Overview

Omega is a research program about alignment, abstraction, and value-bearing continuation.

The basic thought is simple: before an intelligent system can safely optimize for a future, it needs models and metrics that do not erase the distinctions that make that future possible. A bad abstraction can make a lost option look recoverable, a false path look reachable, or a dangerous proxy look complete.

This repo builds a formal toolbench for that problem.

## The Big Idea

Most alignment stories eventually need to talk about agents, preferences, rewards, values, selves, and futures. Omega tries to start one step earlier.

It asks:

```text
Which distinctions are consequence-bearing?
Which abstractions are allowed to erase them?
Which summaries fail to determine the targets they are used to represent?
Which presentations hide loss or fabricate continuation?
```

The long-term ambition is agent-agnostic ethics and alignment: a way to reason about value-bearing futures without assuming that "the agent", "the self", or "the boundary" is already a primitive object.

## Value Requires Valuers

Value requires valuers, or at least value-capable trajectories. If no possible future contains systems able to encounter, preserve, revise, compare, create, or be affected by what matters, then no possible future contains realized value.

That is why the project starts below value. The first target is not a final utility function. It is the substrate of compatible continuations in which valuers can arise, persist, interact, and mature without destroying the conditions that make future value possible.

## Alpha-Omega

Alpha and Omega are working names for studying that value-bearing substrate from two ends.

Alpha is the primitive end. It studies relation, distinction, asymmetry, and consequence before value language is introduced. The question is: how can a difference matter at all?

Omega is the terminal ambition. It asks what it would mean for consequence-bearing structure to unfold into the richest compatible space of value-bearing futures.

The lower stack does not prove the upper ambition by definition. It earns the right to talk about it by proving small, failure-resistant facts about consequence, abstraction, reachability, viability, and loss.

## From Intuition To Formal Machinery

The formal stack asks whether a representation preserves the value-bearing continuation structure it is being used to reason about.

A difference must be consequence-bearing. A proposed abstraction must not erase consequence-separated states. A proxy must not be trusted when the target changes while the proxy stays fixed. A viability or reachability claim must survive exact checking, because bad presentations can fabricate possible futures or hide irreversible loss.

That is why the repo focuses on sound quotients, non-factorization, clique soundness, support-disjoint recovery, fixed-point reachability and viability, reflection contracts, phantom-reachability examples, hidden-loss examples, and loss-aware presentation contracts.

## Proto-Teleology

Proto-teleology is the current milestone.

It is not purpose, intention, agency, morality, or value. It is directed consequence:

```text
A difference matters when erasing it changes what can follow.
```

This matters because it gives us a weak alignment constraint before we have a full theory of value. If an abstraction hides irreversible loss, fabricates reachability, or merges consequence-separated states, it is already unsafe as a map of the corridor.

That is the practical bridge to Gradient Ethics, also described as value preservation under uncertainty. Under uncertainty and irreversibility, preserving the conditions for future value-bearing continuation is not a complete moral theory, but it is a structural safety constraint.

## The Standard Mathematical Compression

Recent work has translated much of the project into standard mathematical language:

- Sound quotient: a quotient is safe only when its kernel is contained in consequence-identifiability.
- Clique soundness: a valid class is pairwise compatible, not merely chain-connected.
- Non-factorization: a target cannot be recovered from a summary if the summary stays fixed while the target changes.
- Exact recovery: declared finite recovery is equivalent to observed support disjointness.
- Fixed-point reachability and viability: continuation constraints can be stated as least and greatest fixed-point objects.
- Reflection and loss-aware contracts: safe abstraction must preserve and reflect the right target, step, and loss facts.

The main overview of this compression is [standard_core_compression_v0.md](research_notes/omega_theory/standard_core_compression_v0.md).

## Why Toy Worlds

Many examples in the repo are tiny finite systems. That is intentional.

Toy worlds make failure modes crisp. If a quotient, proxy, or abstraction can already fabricate reachability in a four-state graph, then the corresponding principle is not safe just because it sounds plausible in a richer system.

The finite layer is not the final substrate. It is the audit bench.

## Relation To Known Work

This project is near several established lines of work: abstract interpretation, Goodhart and proxy failure, viability theory, option value, empowerment, attainable utility, power-seeking, impact measures, and safe control.

The repo does not try to replace those fields. It tries to build a compact proof discipline around one recurring question:

```text
Does the presentation preserve the consequence-bearing target?
```

That question is relevant whether the presentation is a benchmark score, a reward model, a compressed world model, a boundary, a quotient, a safety monitor, or a policy abstraction.

## Current Claim Boundary

The repo does not currently prove:

- value;
- valuerhood;
- agency;
- selfhood;
- identity;
- moral truth;
- Omega as a completed object.

It does prove and test pieces of the lower machinery needed before those claims can be made responsibly.

## Useful Entry Points

- [README](../README.md): the public front door.
- [Omega Formalism Primer](OMEGA_FORMALISM_PRIMER.md): older but still useful conceptual orientation.
- [External Reader Guide](EXTERNAL_READER_GUIDE.md): guide for outside reviewers.
- [Dynamics Abstraction Status](research_notes/omega_theory/dynamics_abstraction_status_v0.md): current reachability/viability abstraction state.
- [Loss-Aware Presentation Contract](research_notes/omega_theory/loss_aware_presentation_contract_v0.md): current abstraction-contract layer.
- [Claims Ledger](CLAIMS_LEDGER.md): current claim hygiene.
- [Validation](VALIDATION.md): how to validate local and CI-facing checks.
- [Human-AI Workflow](HUMAN_AI_WORKFLOW.md): transparent note on how the repo is produced.
- [No-Self Evidence Archival Note](references/no_self_evidence_archival_note.md): influence note for an external paper that shaped the boundary/non-self posture.
