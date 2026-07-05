import OmegaProper.Decision.License
import OmegaProper.Decision.Examples
import OmegaProper.Decision.RobustCorridor
import OmegaProper.Decision.RobustCorridorExamples
import OmegaProper.Decision.AmbiguityFamily
import OmegaProper.Decision.AmbiguityFamilyExamples
import OmegaProper.Decision.Containment
import OmegaProper.Decision.ContainmentExamples
import OmegaProper.Decision.HistoryContainment
import OmegaProper.Decision.HistoryContainmentExamples
import OmegaProper.Decision.TrajectoryBridge
import OmegaProper.Decision.TrajectoryBridgeExamples
import OmegaProper.Decision.TrajectoryConverse
import OmegaProper.Decision.TrajectoryConverseExamples
import OmegaProper.Decision.AdaptiveFixedWorld
import OmegaProper.Decision.Dominance
import OmegaProper.Decision.DominanceExamples
import OmegaProper.Decision.DominanceAcceptance
import OmegaProper.Decision.DominanceAcceptanceExamples
import OmegaProper.Decision.DominanceFinite
import OmegaProper.Decision.DominanceFiniteExamples
import OmegaProper.Decision.BlackwellDeterministic
import OmegaProper.Decision.BlackwellDeterministicExamples
import OmegaProper.Decision.BlackwellStochastic
import OmegaProper.Decision.BlackwellStochasticExamples
import OmegaProper.Decision.Arbitration
import OmegaProper.Decision.ArbitrationExamples

/-!
OmegaProper.Decision umbrella.

ODT0-style decision-floor scaffolding. This namespace is intentionally thin:
it consumes certified presentation/reflection and corridor predicates rather
than deriving value, agency, identity, or a complete decision theory.
-/
