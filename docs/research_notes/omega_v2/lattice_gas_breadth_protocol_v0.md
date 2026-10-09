# FHP-I gas-reference breadth probe v0

2026-10-07. First new local-update substrate; no prescribed winner.

Use the published six-channel FHP-I triangular lattice gas (Frisch et al.,
Complex Systems 1, 1987, Figure4/section2.2): head-on opposite pair scatters to
either other opposite pair with probability1/2; alternating triple reverses
deterministically; other local occupancies unchanged. Local choices independent.
One physical tick is simultaneous collision then one-link streaming. Periodic
axial-coordinate torus, side3 and4, exactly4 particles, zero total vector momentum.
Unit-speed particles conserve number, momentum and kinetic energy; no fuel tax,
external drive, reaction mechanism or arbitrary rate parameter. No rest particles.

Primary reference: https://content.wolfram.com/sites/13/2018/02/01-4-7.pdf .
Narrow independent reference check confirmed this table and the stationarity
argument before running.

Enumerate the entire fixed-(N,P) sector, not just reachable states of one favored
root. Local collision is doubly stochastic; streaming is a bijection. Therefore
uniform distribution on this sector is invariant. Verify columns and rows sum1.
Do not assume ergodicity: compute closed communicating classes and also compare
each root with its own component's uniform invariant reference.

Four predeclared roots: two simultaneous head-on pairs; pairs aimed to meet after
streaming; spatially separated counterstreams; four particles packed at one site.
Same N, energy, momentum, box and law within each comparison. Side3vs4 changes
density and recurrences, not merely representation/resolution. No claims of a
hydrodynamic limit or constructed ecology at four particles.

Measure exact L_x(n)=exp H(X_1,...,X_n|X_0=x) via backward recurrence ell'=h+Pell,
where h(x)=H(P(x,.)); integer raw path counts via support recurrence. Horizons
0,1,2,4,8,16,32,64. Actual full-state collision-and-stream outcomes counted once,
not artificial serializations of different sites' updates.

Thermal reference reports distribution of rooted ell over uniform sector,
mean ell (log geometric-mean L), and log mean L separately. Never add initial
ensemble entropy to a rooted comparison. Compare component mean ell too.
Posthoc maxima must be identified as such, not predeclared organized winners.

Analytic screen: h(x) is the number of stochastic pair-collision sites times ln2,
because independent pair outcomes remain distinct under bijective streaming.
Thus ell counts expected cumulative pair-collision bits. This is a feature of
this measurement/model to report, not repair by rule tuning. Exact stationary
mean ell must be n times mean h. Gas is allowed to win.

Checks: exhaustive local64 conservation and double stochasticity; global sectors
closed/conserved; exact stationary reference; translation covariance; two-site
branching; deterministic streaming. Raw summaries ignored locally; only source,
tests, protocol and written report intended for future publication. No push now.
