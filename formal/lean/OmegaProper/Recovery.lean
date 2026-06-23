import OmegaProper.Recovery.ConfusionBound
import OmegaProper.Recovery.CoarseningPermanence
import OmegaProper.Recovery.Deterministic
import OmegaProper.Recovery.Examples
import OmegaProper.Recovery.FiniteChannel
import OmegaProper.Recovery.Joint
import OmegaProper.Recovery.ObservationRefinement
import OmegaProper.Recovery.PolicyContinuation
import OmegaProper.Recovery.Prior
import OmegaProper.Recovery.Randomized
import OmegaProper.Recovery.Robust
import OmegaProper.Recovery.RobustRandomized

/-!
OmegaProper.Recovery

Public umbrella for finite recovery theory.

This layer treats support-exact recovery as the zero-error endpoint of a
source-indexed recovery profile, with deterministic, randomized, robust,
prior-relative, joint, and finite-horizon policy-conditioned variants kept as
separate axes. It does not define identity, agency, value, valuerhood,
deformer structure, or Omega proper.
-/
