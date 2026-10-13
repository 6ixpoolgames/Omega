# Maintained locked-resource adapter

This separately versioned 16-state toy includes a one-unit local resource buffer
(`empty`, `locked`, `usable`, `waste`), one conserved apparatus/precursor slot,
and one conserved charged/spent energy-carrier slot. An ideal maintained
external boundary prescribes locked-resource and charged-carrier inflows and
locked-material, waste, and charged-carrier outflows, with boundary work at a
declared temperature. The boundary is not a finite reservoir represented in
the local state. Full buffers have no no-op arrival events. Equal boundary
prescriptions are used in the capable and paid-path-ablated laws; accepted flux
and work may differ with occupancy.

The paid release is a forward/reverse carrier-coupled pair. Basal release and
downstream use are also thermally paired. The ablation removes both directions
of paid release while retaining state space, basal access, boundaries,
downstream use, apparatus/precursor dynamics, and maintenance. Stored carrier
depletion is an internal state-energy transfer; boundary recharge/export carry
`Event.work`. No added reservoir reward enters the sampled-state history entropy.

The downstream reaction converts usable resource to waste and does not make
apparatus precursor or charged carrier. Thus this comparison tests maintained
access and throughput under an external drive, not feedback that sustains its
own enabler. Resource-to-maintenance coupling is a separate future model step.

The small fixture is an engineering mechanism model. Its parameter values are
declared conventions for this adapter, not measured chemistry, and the model
does not establish open-ended growth. `PROTOCOL.json` records the frozen cases,
cadences, horizons, boundary rates, and hard caps. The compact outcome assessment
is in `SCIENTIFIC_ASSESSMENT.md`; the full frozen output remains under ignored
`results/local_runs`.
