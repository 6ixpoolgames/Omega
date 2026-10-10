# Sol state-time-resource tube proposal: assessment

2026-10-05. User-supplied proposal. Algebraic assessment and inspection of the
existing chemistry representation; no new simulation or adopted lushness rule.

## Useful ingredients

Retain physical histories, native frame-conditioned probabilities, resources,
timing and a model-declared resolution. These can be investigated classically
without settling fundamental quantum ontology. Counting valid configurations
is a possible explicit finite-model convention; it is not automatically a
uniquely physical volume element.

The proposed volume mixes three different standard constructions. Separating
them exposes exact limitations before implementing an atlas.

## State-time occupancy collapses to elapsed time

Let X_t be the full resolved physical state, including present fuel stock.
Give each discrete state cell volume one. The state-time graph of one path is

    G_gamma = {(X_t,t): 0 <= t <= T}.

For z=(s,t), the probability that a path visits z is P(X_t=s). Consequently,

    V_occupation(T) = integral_0^T sum_s P(X_t=s) dt = T.

For state cells of equal volume v this is v*T. This is true under any fixed
frame conditioning that supplies a normalized law on the included states.
No change of the frame weights is needed or justified. Appending an accumulated
resource coordinate does not resolve the issue: at every t each run still
occupies exactly one joint state/resource cell.

For an irreducible finite CTMC, every state has positive occupancy probability
at any t>0. The union of all state-time graphs then has counting-times-time
volume |S|*T, independently of the rates. A resource constraint can restrict
this support; the claim here is about the unrestricted construction and equally
supported constrained examples, not all conceivable budget profiles.

Nonuniform cell volumes yield integral E[v(X_t)]dt, which need not be constant.
But the discrimination then comes from the stipulated cell-volume function.
It must be physically specified, not fitted to desired catalytic rankings.
Integrating a probability density against its reference measure instead again
integrates to one per time slice. Membership probabilities and densities must
not be interchanged.

If time is divided into bins and each state visited anywhere within a bin is
counted, the value instead includes within-bin exploration. For a finite-rate
CTMC and bin width delta, multiplying by delta makes it tend to T as delta
decreases; excess is bounded by delta times the expected jump count. Binning
does not automatically supply a new physical extent.

## First-visit coverage is different

Drop time from the target cell and let tau_s be its first hitting time. Then

    V_range(T) = sum_s P(tau_s <= T)
               = E[number of distinct states visited by T].

More generally integral P(path hits z by T) dmu(z) is expected measure of the
visited range. This retains kinetic information and does not count revisits
to the same state twice. For two reversible states, both rates lambda, starting
at one state, V_range(T)=2-exp(-lambda*T). At T=1 it is 1.632120559 for lambda=1
and 1.999954600 for lambda=10. The occupation volume remains one in both cases.

This is a useful exploration baseline, not automatically volume of consequential
continuation. It loses visit order and simultaneous/pathwise compatibility.
Integrating P(tau_s <= t) over t is yet another quantity: E[sum_s(T-tau_s)_+],
which keeps crediting a previously visited state even after it has been left.

## Loops and historical structure

In state-time space a revisit at t2 is a different cell from a visit at t1.
Even an immobile one-state trajectory has tube volume T. Thus the stated
claim that loops cannot keep increasing volume is incompatible with counting
new time slices. Duration is physically consequential and may deserve
representation; the problem is the mismatch between the claimed property and
the definition, not a requirement to discard duration.

A union of trajectory graphs retains which states occur at which times, but
not which occurrences belong to the same compatible history. Occupancy
probabilities are marginals, not the joint path law. A stationary symmetric
two-state chain has identical .5/.5 marginals at every time for all positive
rates lambda, while P(X_t=X_0)=(1+exp(-2*lambda*t))/2 changes with lambda.
Both the unweighted state-time support and the full occupancy field tie, but
temporal persistence differs. Quantum or classical correlations across time
cannot be reconstructed from these marginals alone.

Reconvergence may allow a shared residual suffix, but does not erase earlier
consequential history. Keeping the individual paths elsewhere in a data file
does not make a scalar union formula sensitive to the information it discards.

## Chemistry-specific representation issues

The current State contains positions, internal states, explicit bonds and fuel.
Occupancy is derived from positions; fuel is already a resource coordinate.
They are not independent extra Cartesian factors. Legal bonds also depend on
contact geometry. Work on the constrained state space, not the full coordinate
box. Cumulative resource expenditure can be added as a separate history
observable when explicitly distinguished from current stock.

The finite fuel stock is already an aggregate coordinate: the model's free
energy includes log binomial(capacity,fuel) as microscopic multiplicity.
One encoded configuration therefore need not mean one equally sized physical
microcell. Bookkeeping particle IDs also cannot manufacture distinctions.
The finite resolution is an effective-model assumption, not established as
the universe's finest physical resolution.

Full exact state enumeration of the current 16-particle lattice is not the
same task as replaying its sampled trajectories. Finite state space does not
imply practical enumerability; continuous-time paths also have arbitrary
finite jump counts. An exact prototype requires a much smaller apparatus or
a specified finite restriction.

## Quantum scope and recommendation

Decoherent histories provide a principled route to classical probabilities
when interference between the histories is negligible. That does not by itself
select a counting measure over branches or a geometric extent. A generic
CTMC is not automatically the derived coarse limit of a specified unitary
model. These are extension obligations, not reasons to postpone the classical
measurement problem.

Keep occupation and first-visit range as explicit baselines. Do not implement
the proposed state-time weighted integral as a new lushness extent: its main
equal-cell case is analytically constant. Pursue extent on the weighted
relational continuation object with joint compatibility and residual dynamics
actually entering the functional. The elementary extent still needs a
specific candidate; this note does not claim to have derived one.

Primary references checked:
- [Aldous and Fill, hitting times and occupation times](https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch2.S2.html).
- [Halliwell, A Review of the Decoherent Histories Approach to Quantum Mechanics](https://arxiv.org/abs/gr-qc/9407040).

Local representation: omega_v2/finite/lattice_chemistry.py, especially State,
free_energy, contacts and events. The identities and two-state examples above
are direct calculations, not new empirical results.
