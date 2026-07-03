import OmegaProper.Decision.License
import OmegaProper.Decision.Examples
import OmegaProper.Decision.RobustCorridor
import OmegaProper.Decision.RobustCorridorExamples
import OmegaProper.Decision.Dominance
import OmegaProper.Decision.DominanceExamples
import OmegaProper.Decision.DominanceAcceptance
import OmegaProper.Decision.DominanceAcceptanceExamples
import OmegaProper.Decision.DominanceFinite
import OmegaProper.Decision.DominanceFiniteExamples
import OmegaProper.Decision.BlackwellDeterministic
import OmegaProper.Decision.BlackwellDeterministicExamples

/-!
OmegaProper.Decision umbrella.

ODT0-style decision-floor scaffolding. This namespace is intentionally thin:
it consumes certified presentation/reflection and corridor predicates rather
than deriving value, agency, identity, or a complete decision theory.
-/
