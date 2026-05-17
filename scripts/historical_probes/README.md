# Historical Probe Scripts

This folder contains executable scripts from earlier Omega validation branches.

They are retained for provenance, reproducibility, and failure analysis. They
are not the current front edge of the project.

Current active implementation work should start from the VAL0-CT design:

- `../../docs/research_notes/validation_design/README.md`
- `../../docs/research_notes/validation_design/val0_ct_implementation_spec.md`
- `../../docs/research_notes/validation_design/val0_constructor_task_algebra_probe.md`

## Contents

The scripts here cover historical branches:

- early single-Omega validation and supplementary sanity checks;
- coarse-graining/admissibility audits;
- COM/fiber transport probes;
- trajectory-space and invariant-stack probes;
- primitive distinction/asymmetry/relation probes;
- DAX q=3/r=1 rule-space probes;
- hardware smoke and stress probes.

Most scripts write outputs relative to the current working directory. If
rerunning a historical probe, run it from the repository root unless the script
itself says otherwise.

