# Exact residual alternatives v0

2026-10-05. User authorized the next step after naive realized-history counts.
Use the unchanged LatticeChemistry law on its fully occupied four-particle
2x2 square. No legal move can change the positions in this closed class;
binding, unbinding, conformation, shared fuel and catalysis remain native.
This isolates chemical continuation structure; it is not a gas/mobility test.

Enumerate all 16 internal-bit patterns, 16 bond subsets and capacity+1 fuel
stocks. Compare capacities 1/4, bond strengths 0/2 and barriers 0/2. Native
equilibrium is computed exactly from exp(-energy) times binomial fuel
multiplicity, within this positional class. Prepared cases: unbound, one
bond, two adjacent bonds, two opposite bonds and all four bonds; exposed
internal bits and initial fuel min(2,capacity) are common. Adjacent/opposite
two-bond states have identical energy, fuel and bond count. Also compare
equilibrium and the same equilibrium configurations refueled.

Keep three levels explicit:

1. Complete state/channel graph with original rates. Reconvergence shares
   residual states; different prefixes are still different sequences.
2. Unweighted alternatives: distinct states within 0..8 native jumps, exact
   ordered state-sequence and channel-sequence counts at each depth. No
   timing is inferred from jump count. Channel multiplicity and sequential
   interleavings are retained as sensitivities of this naive count.
3. Native time law: state distributions and cumulative event means at cuts
   0/1/5/20; jump-count/state law for residual lags .25/1/4. Layers retain
   0..8 jumps and a separate absorbing overflow with its full probability.
   No overflow branch is dropped or renormalized. Report the actual probability
   of the next two jumps being distinct fuel-consuming bindings by each lag,
   with every competing reaction and replenishment rule unchanged.

Residual support counts are averaged over the native state law at each cut;
this is not a prior over values. Weighted counts of individual prefix
cylinders have a known limitation: at depth n they sum to P(N>=n), and over
all depths including zero they sum to 1+E[N]. Record this instead of claiming
it is a new extent. Current-state support at any positive time is likewise
constant in a finite irreducible class. Preserve both findings if they occur.

Save all state/channel laws, initial distributions, support profiles and
probability outputs. Matrix exponentials supply numerical finite-state
solutions, not Monte Carlo estimates. Check probability mass, exact target
detailed balance, a Poisson jump-count control and shared-fuel exclusion.
No independent futures/dimensions, concurrency or quantum conclusions follow
from an ordered walk count. No winner or fitted aggregation is required.
