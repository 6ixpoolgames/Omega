import OmegaAdapters.Audit.AdapterFailures
import OmegaAdapters.FiniteBoolean
import OmegaAdapters.FiniteBooleanNative
import OmegaAdapters.FiniteChannel
import OmegaAdapters.FiniteChannelNative
import OmegaAdapters.ProbabilisticChannel
import OmegaAdapters.ProbabilisticChannelNative
import OmegaAdapters.ProbabilisticChannelPolicy

/-!
OmegaAdapters umbrella.

Adapter and presentation-specific machinery. These modules expose how finite
substrates instantiate or fail checked transport/recovery machinery; they do
not validate Omega-level claims.
-/
