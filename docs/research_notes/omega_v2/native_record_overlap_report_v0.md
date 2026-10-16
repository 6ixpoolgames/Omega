# Native record overlap: coherence-limit results v0

2026-10-08. Exploratory exact test of the user's proposed endpoints: fully overlapping continuation has extent one; fully distinguishable classical developments recover classical weighted breadth. No gas/optimality claim or universal quantum extent adopted.

## Outcome

The weighted overlap construction reproduces both endpoints and growing classical history breadth. It also passes independent products, inert blank ancillas and passive basis changes. Nevertheless it fails an unchanged-physics checkpoint test, because its arithmetic discards cross-history terms before evaluating the physical record state.

The boundary intuition remains a possible requirement. This particular implementation is rejected as intrinsic extent. Global purity, record-state mixedness and independence of declared developments remain different properties; a universal purity switch cannot implement these limits.

## Candidate and physical model

Reuse the two-site particle with local blank detector registers. Balanced hopping has U=exp(-i pi X/4); each selected local detector interaction records occupation at R. Detector strength is a controlled Y rotation phi, so conditional marker overlap is cos(phi). All gates are ideal scheduled native unitaries in these toy models, not autonomous energy-accounted interactions.

For a declared site-history family, branch vectors v_h are generated coherently from the sufficient present. Compare

\[
W_E=\sum_h\operatorname{Tr}_{\bar E}|v_h\rangle\langle v_h|,
\qquad
\rho_E=\operatorname{Tr}_{\bar E}\left|\sum_hv_h\right\rangle\left\langle\sum_hv_h\right|.
\]

The candidate is exp S(W_E); actual reduced-state effective rank is exp S(rho_E), a control. Also retain the diagonal breadth of the physically specified record-register basis and the full history kernel. E is the actual detector bank in this adapter, explicitly selected by its physical role. No universal preferred subsystem is assumed.

When v_h=a_h |x_h>|E_h>, W_E is a mixture of conditional record states. Its spectrum is the nonzero spectrum of their weighted overlap Gram matrix. Identical E_h give extent one; mutually orthogonal E_h give exp H(|a_h|^2). This is the proposed interpolation, but its history weights come from diagonal class-operator weights, which need not define unmeasured coherent alternatives.

W_E equals the record output of the process with unread projective measurements inserted at the chosen site checkpoints. Those measurements are not in the native physics here. The risk is analytical and was named in the protocol before execution. Actual rho_E retains their cross terms. Environment-induced decoherence and the physical selection of stable distinctions motivate testing records, but do not identify either entropy with universal extent; see [Zurek's review](https://arxiv.org/abs/quant-ph/0105127).

## Boundary interpolation

One balanced hop followed by one conditional detector interaction gives eigenvalues (1+-cos(phi))/2 for both W_E and actual rho_E in this special case.

| Marker action | Conditional overlap | Effective record extent |
|---:|---:|---:|
| 0 | 1 | 1 |
| pi/6 | sqrt(3)/2 | 1.278612 |
| pi/4 | 1/sqrt(2) | 1.516637 |
| pi/2 | 0 | 2 |

At phi=0 the particle can be spatially spread while the detector is unchanged. The value one here concerns conditional-record independence, not a proof that all coherent physical continuation has one unit of lushness.

## Classical growth works for the overlap construction

Each balanced hop is recorded into its own fresh blank detector. Histories have mutually orthogonal complete record strings, so this site-history family is exactly decoherent.

| Recorded hops | Overlap candidate | Actual detector-state effective rank | Record-string diagonal breadth |
|---:|---:|---:|---:|
| 1 | 2 | 2 | 2 |
| 2 | 4 | 2 | 4 |
| 3 | 8 | 2 | 8 |
| 4 | 16 | 2 | 16 |

This candidate avoids the fixed-initial-reference cap of the preceding probe. It is not yet intrinsic because of the next test.

Actual rho_E remains rank at most two because the global particle/detector state is pure and the complementary particle Hilbert space is two-dimensional. The record strings still have 2^n mutually exclusive diagonal outcomes. Coherences between strings ending at the same particle site can remain in the detector's reduced state. A decoherent family of recorded histories does not imply that the entire retained detector density matrix is diagonal in the record basis.

All global states in this table are pure. Thus neither full-state purity nor reduced-state effective rank can automatically identify the intended classical-history breadth.

## Decisive unchanged-physics witness

Start at L, perform a balanced hop, reverse it exactly, and only then record the site into a blank detector. The final particle is L and the detector remains 0.

| Mathematical history description | Candidate exp S(W_E) | Actual record-state extent | Actual record-basis breadth |
|---|---:|---:|---:|
| No intermediate site resolution | 1 | 1 | 1 |
| Resolve site between the two hops | 2 | 1 | 1 |

Both branch expansions reconstruct exactly the same final state. No physical record or measurement was added. The refined candidate effectively removes the interference responsible for return to L, producing a counterfactual mixed record instead. Maximum entrywise difference between W_E and rho_E is0.5.

A genuine midpoint recording interaction is a different physical case. It changes the later interference and produces actual record extent2. The candidate must distinguish that physical interaction from a purely mathematical site cut; it currently does not.

This is not a requirement that all questions or resolutions have equal answers. It rejects interpreting the refined W_E as the actual physical record-overlap state, or its entropy as an intrinsic extent of the same unmeasured process.

## Copying and changing the retained region

After two perfectly recorded hops, copy both detector bits into two additional blank registers by native CNOTs.

| Reduced-state query | Effective rank |
|---|---:|
| Original memory bank before copies | 2 |
| Original memory bank after copies, copies outside query | 4 |
| Original memory bank plus copies after copying | 2 |

The physical record-basis breadth is4 in all three descriptions; the copies are redundant, not new independent record strings. The complete quantum state remains pure. Including the copied records in the retained quantum subsystem restores access to joint coherences; reduced entropy is not a universally monotone count of record alternatives.

This supplies a concrete reason to formulate coherence relative to physical developments/relations rather than as a single global pure-versus-mixed classification. It does not prove any of these three reductions is the preferred frame for Omega.

## Checks and scope

Four interpolation cases, four growth cases, two echo descriptions, one genuine midpoint-record contrast and one copy experiment were computed. Maximum reconstruction/normalization/covariance/product error was4.22e-15. Eight targeted tests and Ruff passed. Source: omega_v2/finite/native_record_overlap.py; runner: omega_v2/validation/native_record_overlap_v0.py. Raw JSON is ignored under results/local_runs/native_record_overlap_v0/results.json. No push.

The protocol anticipated the analytical pitfalls; this was a small implementation/calibration audit, not discovery that environmental entropy and classical history entropy differ. No new parameter tuning or changes to the proposed endpoints were introduced after execution.

## Consequence for the programme

The desired limits are mathematically achievable for a fixed physical family of conditional records. They are not sufficient to identify universal extent: a formula can obey both and still count a mathematical resolution as a physical measurement.

Do not repair this by selecting whichever checkpoint family yields a desired number. Preserve native amplitudes and coherent composition before forming any physical record profile. A future extent construction must explain which continuation distinctions can be assigned independent reference units without dropping intervening interference. Record-basis breadth remains an exact classical-frame diagnostic. The universal coherent extension remains open, and lushness remains the intended extent, not a renamed record or organization score.
