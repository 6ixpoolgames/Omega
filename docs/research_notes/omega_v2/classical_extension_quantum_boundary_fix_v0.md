# Classical extension and the quantum boundary: a restricted repair

**Reading update, 2026-10-09:** the
[quantum continuation foundation](../../quantum/README.md) consolidates this
restricted construction with subsequent evidence and conditional bounds.
The original argument below remains part of the research record.

Date: 2026-10-08. Status: analytical construction and implementation recommendation; no new numerical experiment, adopted universal quantum extent, or push.

## What is being repaired

Lushness remains the intended effective weighted extent of complete future development from a sufficient present. The native quantum development remains the carrier. Records are physical correlations within it, not an added observer, a value reward, or a replacement definition of lushness.

The proposed limits are useful boundary conditions, but need different qualifications:

- In a specified physical classical development frame, the construction must recover complete-history perplexity.
- One effective continuation alternative has breadth one.
- A pure universal quantum state need not have only one classical alternative. Global purity cannot implement the second condition.

The repair below establishes the classical extension rule and a sufficient physical certificate for applying it within a quantum model. It does not yet give an extent to every coherent development.

## 1. Classical reference extent extends; probability marginalizes

At a declared physical resolution let H_n be the finite set of lawful complete developments from the root through cut n. Histories retain earlier differences after endpoint reconvergence. Deterministic checkpoints are not new alternatives. Concurrent serializations require the adapter's declared physical equivalence; arbitrary update strings are not assumed distinct.

Let pi_n:H_(n+1)->H_n forget the final extension. Use the commutative history algebra

    C_n = C^(H_n),       tau_n(a) = sum_h a(h).

This is an explicit unit-cell counting calibration, not a derivation of a continuum volume element. For comparisons across roots use a common adapter, physical resolution and history-cell prescription; inaccessible histories have zero probability.

The inclusion j_n(a)=a composed with pi_n obeys

    tau_(n+1)(j_n(a)) = sum_h k(h) a(h),

where k(h) is the number of lawful distinct extensions. There is no requirement that this equal tau_n(a). By contrast, physical probabilities obey

    p_(n+1)(h,e) = p_n(h) q(e|h),
    sum_e q(e|h) = 1,
    sum_e p_(n+1)(h,e) = p_n(h).

Thus the state functional omega_n(a)=sum_h p_n(h)a(h) satisfies

    omega_(n+1)(j_n(a)) = omega_n(a).

Probability consistency and reference-extent extension are different equations. No probability amplification or fitted growth multiplier is required.

With unit cells,

    L_n = exp[-sum_h p_n(h) log p_n(h)],

and the exact chain rule gives

    log L_(n+1) - log L_n = sum_h p_n(h) H(q(.|h)).

Examples:

- n successive fair binary alternatives: L_n=2^n, probability mass always one.
- Two equally weighted parents, A with three equiprobable children and B with one deterministic child: L_1=2 and L_2=2 sqrt(3). Reference counts grow from 2 to 4; effective extent grows from 2 to 2 sqrt(3).
- An added deterministic checkpoint has k=1 and H(q)=0: no change.
- Independent developments have product history laws and multiplicative L.

For a probability-one deterministic future, L=1. This is the accepted breadth calibration, not an excuse to add structural rewards.

A terminal outcome retains its probability and can be extended by a deterministic absorbing symbol. It supplies no further branching entropy. Removing it and renormalizing survivors is an additional conditional question. Original-root cumulative classical history breadth cannot decrease under this extension rule; damage changes future growth relative to a matched preparation, while a freshly rooted residual profile is a different query.

## 2. A physical certificate for classical histories within quantum dynamics

Keep the complete present psi_0, the native propagator, and the physical subsystem/locality specification. For candidate history class operators C_h ending at time t, write

    v_h = C_h psi_0,        psi_t = sum_h v_h.

A sufficient exact record certificate is an exhaustive orthogonal family of actual record projections R_h such that

    R_h psi_t = v_h.

This implies D(h,k)=<v_k|v_h>=0 for h!=k and p_h=||v_h||^2=<psi_t|R_h|psi_t>.

The certificate alone does NOT select a physical history family: abstract projections onto arbitrary orthogonal branch vectors would pass it. Require additional evidence from the native local interaction and state: which variables were coupled, how their correlations arose, and whether the corresponding record distinctions remain stable under the subsequent native dynamics. No additional reader is inserted to satisfy the test.

For exact stable extension from t to t', descendant record projections must satisfy, on the dynamically relevant subspace,

    sum_e R_(h,e)(t') = U(t',t) R_h(t) U(t',t)^dagger.

This implements the same prefix inclusion as the classical construction and yields the same probability marginalization. It is a sufficient idealized regime, not a claim that every physical record is permanent. Approximate records need separately declared error and stability-horizon profiles.

The relevant established direction is records-based decoherent histories and strong decoherence. Gell-Mann and Hartle study conditions ensuring the continued decoherence of earlier alternatives under future extension; Hartle also formulates histories starting with records. Neither supplies a canonical Omega extent or uniquely selects all native records:

- https://arxiv.org/abs/gr-qc/9509054
- https://arxiv.org/abs/1608.04145

## 3. Use the record algebra's trace, not ambient rank

For a physically justified record family define

    C_rec = {sum_h a_h R_h},
    tau_rec(sum_h a_h R_h) = sum_h a_h,
    f_rec = sum_h p_h R_h.

Then tau_rec(f_rec)=1 and exp[-tau_rec(f_rec log f_rec)]=exp H(p).

The abstract trace assigns one unit to each distinguishable history cell, not rank(R_h) units to all microscopic states in its representing Hilbert subspace. Tensoring an unresolved identity on an inert blank register therefore does not double occupied extent. Copying the same record also does not create a new independent history alternative; additional independent physical outcomes do.

The full state can remain pure throughout. For

    psi = sum_h sqrt(p_h) |s_h>|r_h>,

with orthogonal physical records, restriction of the state to C_rec has probabilities p_h even though the full density operator has entropy zero. This reconciles universal purity with classical breadth without invoking collapse.

It does not prove that records exhaust quantum possibility extent. In particular, an unrecorded coherent evolution remains in the carrier even if this classical record algebra is trivial.

## 4. Where this differs from our failed record-overlap candidate

Do not form sum_h Tr_complement |v_h><v_h| for every mathematical checkpoint family. That erases cross-history terms and can simulate an unread measurement. Require a native physical record certificate first; otherwise retain the complete coherent class-operator composition.

For an echo that returns a particle before any recording interaction, propagate the echo coherently and then evaluate the actual later record. A mathematical intermediate site cut supplies no new record algebra generator. A genuine intermediate recording interaction is different physics.

For repeated ideal record-producing interactions with stable distinct history records, the trace extends with their actual alternatives and gives 2^n for fair binary developments. It is not the pushforward of a fixed initial reference of trace two, so the earlier artificial ceiling is absent.

For a later coherent reversal, the permanent-record extension certificate may fail. Retain the full original-root quantum development and its interference; do not silently carry earlier diagonal probabilities into a later incompatible classical family. A later residual record algebra may be smaller. This is not a proof that the complete original-root quantum extent contracts to one, and it does not erase the physical occurrence of the interaction.

## 5. What Sol's algebraic trace does and does not provide

For an already specified finite algebra, sum of ordinary traces over its simple blocks is a useful explicit reference convention. But both M_d and its diagonal algebra C^d have this trace of identity equal to d. Consequently decoherence is not, by itself, enlargement of this reference dimension.

The physically important changes may instead be occupation, the emergence of stable classical distinctions, or genuine chronological extension. These must not be identified with each other.

The ordinary algebra generated by interaction operators also forgets schedule and repetition. Use the native time-ordered process as carrier; attach the record algebras and certified extension maps to it where justified. Do not claim the history carrier has been constructed merely by closing a list of matrices under multiplication.

## 6. Remaining quantum problem and next deliverable

The coherent-one/classical-perplexity limits do not determine an interpolation or a unique physical algebra. Global purity is not the needed coherence criterion. Noncommuting interactions, transient correlations, and reversible records are precisely the cases where the missing definition matters.

The next narrow deliverable should implement or derive a native-record certificate and its extension maps on the existing retained-record, delayed-record echo, and full-reversal circuits. Reuse their actual dynamics. Compute a classical extent only for certified families; report a failed certificate as unavailable for that classical readout, never as quantum extent one or zero.

This is a boundary-constrained route to quantum extent, not a declaration that records are the complete futuresfield. Success would give a reliable classical anchor and an exact location for the coherent extension problem. A genuine universal fix still needs a physical prescription for continuation geometry in the uncertified coherent regions, with covariance, chronology, and composition intact.
