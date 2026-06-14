# Human-AI Workflow

This repository is human-led and AI-assisted.

S. Poole sets the research direction, accepts or rejects claims, decides what enters the repository, and is responsible for the project. AI systems are used as collaborators, critics, drafting aids, code assistants, proof-search partners, and review simulators.

## How AI Is Used

The current workflow often looks like this:

1. A human proposes or revises the research direction.
2. One or more AI systems critique the idea, suggest adjacent frameworks, or propose theorem targets.
3. Codex edits the repo, writes Lean/Python/docs, runs local validation where appropriate, and reports what changed.
4. The human reviews the output and decides whether to continue, revise, merge, or discard.

AI outputs are not treated as authority. A claim is trusted only to the extent that it is supported by:

- checked Lean proof;
- executable Python validation;
- reproducible artifact;
- explicit citation;
- or clear speculative labeling.

## Why State This

The project is partly about making abstractions and provenance auditable. The production process should follow the same norm.

AI assistance has been useful for:

- finding standard mathematical compressions;
- stress-testing language for hidden identity or value assumptions;
- generating finite counterexamples;
- proposing theorem names and proof outlines;
- drafting explanatory documents;
- improving external legibility.

It has also produced overstatements, premature abstractions, and misleading names. The repo's emphasis on claim boundaries, negative controls, validation scripts, and theorem status notes is partly a response to that failure mode.

## Practical Reading Note

Some documents in this repo are polished theory notes. Others are working notes or AI-assisted drafts retained for provenance. A document's status should be read from its path, header, and surrounding validation context.

The strongest artifacts are the checked Lean files and reproducible validation scripts. The research notes explain the ambition and interpretation, but they are not substitutes for proof or validation.
