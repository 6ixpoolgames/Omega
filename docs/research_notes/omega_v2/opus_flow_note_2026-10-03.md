# Reading the new flow probe

3 October 2026. Exploratory interpretation of the supplied [Opus report](../../references/opus/2026-10/flow_probe_results_v0.md). Its code, raw outputs and protocol were not attached; the reported numbers have not been replicated here. This is a different probe from our [aggregation prototype](frame_aggregation_report_v0.md).

The useful result is the separation of quantities: turnover, stored correlation, memory, incremental prediction and propagation range need not order structures alike. Their disagreement is evidence against identifying any one of them with the whole continuation comparison; it does not require rejecting the underlying dynamics.

The cleanest diagnostic is CTL = I(X_r(0); X_rest(tau) | X_rest(0)). If the rest already contains a perfect copy of X_r(0), that source adds no conditional information: CTL is zero regardless of whether the existing physical channel is reliable or useful. This follows directly from the definition. It measures extra prediction beyond the recipient's present, not the entire access relation. Losing its increment when copying becomes perfect is not by itself deterioration of the field.

Several interpretations need narrower wording:

- Detailed balance gives zero net stationary currents and the corresponding entropy production. It does not imply absent microscopic transitions or that equilibrium cannot retain structure. The report itself finds memory and passive coupling there.
- A larger ring outranking two clocks is not automatically a failure: no general plurality ordering has been derived. Likewise, an additional heat leak is a physical change and need not leave the full object invariant. Those filters are hypotheses, not definitions of acceptable lushness.
- The claimed 128-link decay length comes from a five-link relay. Without a derivation or extension it is an inferred length parameter, not observed transmission over 128 links; the Reynolds analogy remains an analogy.
- The reported gas comparator is a selected population of random driven copy networks, conditioned on reaching the matched throughput. The exclusions must remain visible; this is not a general result about thermal gas.
- The report says signed flows across complementary cuts sum to zero at stationarity. Summing both orientations over all frames would therefore cancel. Its nonzero FLOW sums require an explicit convention (for example magnitudes, positive contributions, or one cut orientation) that the supplied definition does not state. Do not infer the convention from the reported rankings.

The thermodynamic information-flow machinery is established: [Horowitz and Esposito](https://arxiv.org/abs/1402.3276) relates information terms to mutual-information rates and subsystem entropy balances. That does not establish those rates as a lushness extent.

The next useful object remains the physical relation through time: what a distinction can affect, through which couplings, with what weight, and what continuation remains. Preserve the apparent failures rather than combining these readouts until every preferred filter passes. Neither the supplied flow results nor our bounded aggregation output validates the full count-once proposal.
