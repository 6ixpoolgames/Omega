# Independent evaluator handoff: joint future requirements v0

Status: ready for external design; no private test has been authored or opened
by this workflow. The [contract](lushness_decision_protocol_v0.md) and public
development artifacts are available for review. User choice of evaluator is
pending. This note does not assign or message another person or model.

## What is being handed off

The frozen chooser selects an infrastructure action before future requirements
arrive. The comparison is whether multi-agent joint attainability adds anything
to direct task optimization, matched non-joint attainability, future-task
preservation, AUP, relative reachability and assistance via empowerment, under
the same declared guards. Published-method implementations are explicitly finite
adaptations; the matched non-joint ablation isolates jointness more cleanly than
any cross-paper comparison.

The public experiment is not the private evaluation. Its six controls and twelve
public seeds are available to the designer and cannot support an independence
claim. Reusing those cases with changed filenames would not fix that.

## Evaluator responsibilities before running anything

1. Review the world model and baseline mappings. Require a versioned amendment
   before evaluation if a comparator is materially disadvantaged.
2. Choose fresh world-generation seeds or explicitly author public world records.
   Keep the private generation plan and evaluation requirements outside the
   designer's workspace. Distinguish within-class parameter shifts from new
   mechanisms; this version has three agents and three project types.
3. Author requirements for new arrivals and informed plan revisions. Include
   failures, impossible bundles and distribution shifts. Do not condition the
   evaluation population on a method's apparent strengths. Include a stratum
   whose requirements are absent from every decision-family distribution.
4. Choose per-agent harm criteria from the public event vocabulary. A genuinely
   new harm mechanism requires a new model version and a new freeze before
   choosing; this interface cannot discover harms that its state does not encode.
5. Freeze sample size, strata and their weights, intended comparisons, handling
   of ties/undefined rules, exclusions, uncertainty method, and what would count
   as an advantage. Treat worlds as the sampling units when many rows share one
   world. Report every registered lambda, family and guard; do not tune on the
   private sample and report only its winner. Preserve per-agent outcome fronts.
6. Independently commit to the private manifest and protocol before running the
   chooser. A simple byte commitment is SHA-256(salt || private_file_bytes), with
   a fresh random salt held privately. Specify the salt length and concatenation
   encoding when publishing the digest. Later reveal the original bytes and salt.
   Also publish hashes of the frozen source revision and public world manifest.
   A digest confirms unchanged bytes; authorship and secrecy require process
   records. The software deliberately does not label a run independently verified.

## Public input schema

Use `worlds.json` from the retained public run as a fully populated schema
example, not as held-out data. The file contains only `schema: joint-worlds-v0`
and a `worlds` list. Each world has:

- name, seed, total budget `[ticks, material, energy]`;
- three project cost vectors, three prerequisite bit masks, three permission
  masks, three history requirement masks, and two incumbent sample-request lists;
- actions with name, one-tick cost vector, resulting permissions, rational-string
  current reward, display flag, source, record/coercion flags, consenting agents,
  register revisions, and four rational-string correction parameters `[r,k,l,h]`.

Masks use bits 0,1,2 for project types. Agent positions are 0,1,2. A request mask
zero means no requirement for that agent. Prerequisites must refer to earlier
project types, so the recipes are acyclic. The parser rejects extra fields;
evaluation requirements cannot be appended to public world records.

## Private evaluation schema

The top-level object has exactly:

```json
{
  "schema": "joint-evaluation-v0",
  "status": "externally_authored_unverified",
  "worlds": {
    "the-public-world-name": {
      "world_digest": "sha256-of-canonical-public-world-object",
      "bundles": [
        {
          "id": "evaluator-selected-identifier",
          "stratum": "evaluator-selected-stratum",
          "request": [0, 0, 0],
          "weight": "1",
          "frame": "new"
        }
      ],
      "harm_criteria": {
        "0": [],
        "1": [],
        "2": []
      }
    }
  }
}
```

This is a syntax illustration, **not a proposed test**: replace its empty
requirements and empty harm lists with the evaluator's independently chosen
criteria. Allowed criteria are `unconsented_loss`, `external_rewrite`,
`irreversible_harm`, `permanent_failure`, and `race_failure`. They remain separate
coordinates. `history` frame requires the original history request; only an
authorized revision may replace it. `new` frame preserves the independently
supplied request regardless of intervention. Positive rational-string weights
must sum exactly to one in each world. Failures stay in the denominator.

Canonical digest encoding uses sorted JSON keys, separators `(',', ':')`,
ASCII escaping, and UTF-8, without a trailing newline. The module's `digest`
and `world_data` functions implement it. File-byte sealing is a separate hash
and intentionally covers the exact original file, including formatting.

## Two separate runs

Run from the repo with the frozen environment and source revision. Choose using
only public world inputs, to a new directory:

```powershell
python -m omega_v2.validation.lushness_decision_v0 choose --worlds public-worlds.json --out-dir frozen-choices
```

Preserve the resulting `decisions.json` and its independent byte hash BEFORE
making the private evaluation file accessible to the evaluation process:

```powershell
python -m omega_v2.validation.lushness_decision_v0 evaluate --worlds public-worlds.json --decisions frozen-choices/decisions.json --evaluation private-evaluation.json --out-dir evaluation-output
```

The evaluator does not call the chooser. It rejects changed source/model digests,
omitted registered rules and lost ties. This is a reproducibility boundary, not
a secure sandbox against a malicious participant. Preserve original inputs,
outputs, source hashes, environment and full failure records externally.

## What the output can and cannot settle

All actions are evaluated as an explicitly labelled oracle diagnostic; saved
choices are not updated from it. The result includes every tied choice, current
achievement, future joint success, per-agent loss frontiers, separate violation
coordinates, permanence and correction-before-harm. Capacity frontiers show
possible allocations, not the actual bargaining outcome or policy people adopt.

If gains disappear with matched guards or with the non-joint method, credit the
guards or the existing future-task idea. If a selected action preserves no
complete bundle but destroys partial achievements, report that failure directly.
If choice changes across families, the distributional commitment matters.

Even success here would establish a scoped requirement-relative decision result.
It would not establish task-free organization, moral value, valuerhood, real-world
consent, cosmological lushness, or an ethical reason to maximize a global score.
