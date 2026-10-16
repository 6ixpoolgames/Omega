# Fixture A model definition

These models are a deliberately coarse population-level adaptation. `M(x)` is
one free monomer and `D(x)` is a preassembled two-monomer complex. The site is
inert bookkeeping required by BioNetGen's molecule syntax. No spatial location,
orientation, or bond graph is resolved. Inventory is `M + 2 D`.

The base model uses reversible `2 M(x) <-> D(x)`. Its coefficients are both
one. BioNetGen's generated symmetry coefficient and the adapter's falling
factorial propensity together produce the intended association rate
`M (M-1)`; do not divide by another factorial. Dissociation has propensity
`D`.

The metastable arm changes both coefficients to 0.01. It is slow on the common
clock but has exactly the same equilibrium distribution. The feedback arm adds
`D(x) + 2 M(x) <-> 2 D(x)`. One D appears on both sides and is the retained
catalyst; two separate M molecules are substrates. Reverse feedback consumes
two D molecules and returns one D catalyst while releasing two M molecules.
Both directions have coefficient one. This channel is reversible catalysis,
not fuel-driven production.

At standard activities `a_M=a_D=1`, each reaction pair obeys the same
local-detailed-balance ratio `k_forward/k_reverse = a_D/a_M^2 = 1`.
On fixed-inventory classes the stationary law is proportional to
`1/(M! D!)`. The feedback channel changes kinetics and connectivity without
changing that law. The small cases are irreducible because base association and
dissociation remain positive.

The model is not a literal microscopic assembly mechanism and does not establish
generativity or optimizer ethics. It tests network generation, multiplicity,
reversible assembly, equilibrium-preserving feedback, roots and declared
history measurement on a tiny finite substrate.
