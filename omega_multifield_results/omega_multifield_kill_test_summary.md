# Omega Multifield Compact Kill-Test Summary

Runtime cap: 45000ms
Rows: 36

Estimator: `R_bits = E_gamma[log2(|fiber_gamma|)]` over viable observed trajectories, weighted by viable trajectory counts. This estimates aggregate realization-fiber support, not macro-class entropy. `Hmacro_*` is reported separately.

Important limitation: this is a standalone toy simulator because no prior multifield code was present in the workspace.

## Summary

"regime","kappa","status","mean_delta_R","mean_viability_coupled","mean_perturbation_retention","reason"
"(F,T) attractive","center_of_mass","fail","-0.0006","0.99","0.2779","coupled realization robustness did not beat shuffled null consistently"
"(F,T) attractive","relative_distance","fail","0","0.99","0","coupled realization robustness did not beat shuffled null consistently"
"(F,T) attractive","joint_basin","fail","-0.6669","0.99","0.6264","coupled realization robustness did not beat shuffled null consistently"
"(F,F) repulsive","center_of_mass","weak","0.0326","1","0.0549","partial positive signal, but not robust across all checks"
"(F,F) repulsive","relative_distance","fail","0","1","0","coupled realization robustness did not beat shuffled null consistently"
"(F,F) repulsive","joint_basin","fail","-0.0351","1","0.718","coupled realization robustness did not beat shuffled null consistently"
"near-enrichment repulsive","center_of_mass","weak","0.1362","1","0.1648","partial positive signal, but not robust across all checks"
"near-enrichment repulsive","relative_distance","fail","0","1","0","coupled realization robustness did not beat shuffled null consistently"
"near-enrichment repulsive","joint_basin","pass","0.1886","1","0.8117","coupled beats shuffled in most horizon/sample checks with viability retained"

## Main Results

"regime","regime_id","coupling_type","alpha","kappa","horizon","sample_count","R_coupled","R_independent","R_shuffled","R_perturbed","Rn_coupled","Rn_shuffled","Hmacro_coupled","Hmacro_shuffled","Delta_R_coupled_minus_shuffled","Delta_R_coupled_minus_independent","viability_coupled","viability_independent","viability_shuffled","viability_perturbed","perturbation_retention","macro_classes_coupled","macro_classes_shuffled"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","center_of_mass","20","25","0.4837","0.5444","0.2702","0.08","0.1055","0.0582","4.1012","4.3737","0.2135","-0.0607","0.96","1","1","1","0.1654","20","22"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","relative_distance","20","25","0","0","0","0","0","0","4.585","4.6439","0","0","0.96","1","1","1","0","24","25"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","joint_basin","20","25","3.3629","3.6895","3.6895","3.0023","0.7335","0.7945","1.222","0.9543","-0.3266","-0.3266","0.96","1","1","1","0.8928","6","5"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","center_of_mass","20","75","0.3502","0.6241","0.9015","0.2534","0.0562","0.1447","5.8786","5.3273","-0.5513","-0.2739","1","1","1","0.9867","0.7237","65","54"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","relative_distance","20","75","0","0","0","0","0","0","6.2288","6.2288","0","0","1","1","1","0.9867","0","75","75"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","joint_basin","20","75","3.8117","5.0318","5.0318","2.7732","0.6119","0.8078","2.4171","1.197","-1.2201","-1.2201","1","1","1","0.9867","0.7276","22","9"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","center_of_mass","40","25","0.4","0.08","0.08","0","0.0861","0.0172","4.2439","4.5639","0.32","0.32","1","1","1","1","0","21","24"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","relative_distance","40","25","0","0","0","0","0","0","4.6439","4.6439","0","0","1","1","1","1","0","25","25"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","joint_basin","40","25","3.4575","3.4575","3.4575","0.8661","0.7445","0.7445","1.1863","1.1863","0","0","1","1","1","1","0.2505","6","6"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","center_of_mass","40","75","0.4049","0.6083","0.3895","0.0901","0.065","0.0633","5.824","5.7603","0.0154","-0.2034","1","0.9733","0.9467","1","0.2225","62","61"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","relative_distance","40","75","0","0","0","0","0","0","6.2288","6.1497","0","0","1","0.9733","0.9467","1","0","75","71"
"(F,T) attractive","FT_attractive_alpha_0.3","attractive","0.3","joint_basin","40","75","3.8159","5.0023","4.9369","2.4211","0.6126","0.8028","2.4129","1.2129","-1.121","-1.1864","1","0.9733","0.9467","1","0.6345","24","9"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","20","25","0","0.08","0","0.16","0","0","4.6439","4.6439","0","-0.08","1","1","1","1","0","25","25"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","relative_distance","20","25","0","0","0","0","0","0","4.6439","4.6439","0","0","1","1","1","1","0","25","25"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","joint_basin","20","25","3.0823","3.0023","3.2284","2.5343","0.6637","0.6952","1.5615","1.4154","-0.1461","0.08","1","1","1","1","0.8222","7","7"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","20","75","0.4155","0.4495","0.3916","0.0913","0.0667","0.0641","5.8133","5.7169","0.0239","-0.034","1","0.96","0.92","0.9867","0.2197","64","59"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","relative_distance","20","75","0","0","0","0","0","0","6.2288","6.1085","0","0","1","0.96","0.92","0.9867","0","75","69"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","joint_basin","20","75","3.658","3.5412","3.4671","2.8504","0.5873","0.5676","2.5708","2.6414","0.1908","0.1167","1","0.96","0.92","0.9867","0.7792","23","22"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","40","25","0","0","0","0","0","0","4.6439","4.3923","0","0","1","0.92","0.84","1","0","25","21"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","relative_distance","40","25","0","0","0","0","0","0","4.6439","4.3923","0","0","1","0.92","0.84","1","0","25","21"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","joint_basin","40","25","2.7795","2.1785","2.386","1.4888","0.5985","0.5432","1.8644","2.0063","0.3935","0.601","1","0.92","0.84","1","0.5356","9","8"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","40","75","0.2501","0.1167","0.1434","0","0.0401","0.023","5.9788","6.0854","0.1067","0.1333","1","1","1","0.9867","0","66","70"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","relative_distance","40","75","0","0","0","0","0","0","6.2288","6.2288","0","0","1","1","1","0.9867","0","75","75"
"(F,F) repulsive","FF_repulsive_alpha_0.3","repulsive","0.3","joint_basin","40","75","3.6593","4.0907","4.2379","2.6897","0.5875","0.6804","2.5695","1.9909","-0.5786","-0.4314","1","1","1","0.9867","0.735","22","17"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","20","25","0.4","0.08","0.1902","0.08","0.0861","0.041","4.2439","4.4537","0.2098","0.32","1","1","1","1","0.2","20","23"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","relative_distance","20","25","0","0","0","0","0","0","4.6439","4.6439","0","0","1","1","1","1","0","25","25"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","joint_basin","20","25","2.1767","1.5502","1.5502","1.3902","0.4687","0.3338","2.4671","3.0937","0.6265","0.6265","1","1","1","1","0.6387","9","12"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","20","75","0.6903","0.4267","0.5216","0.1067","0.1108","0.0837","5.5385","5.7072","0.1687","0.2637","1","1","1","1","0.1545","55","59"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","relative_distance","20","75","0","0.0267","0","0","0","0","6.2288","6.2288","0","-0.0267","1","1","1","1","0","75","75"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","joint_basin","20","75","3.0065","3.2264","3.2264","2.4581","0.4827","0.518","3.2223","3.0024","-0.2199","-0.2199","1","1","1","1","0.8176","18","18"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","40","25","0.32","0.2702","0.24","0","0.0689","0.0517","4.3239","4.4039","0.08","0.0498","1","1","1","1","0","22","22"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","relative_distance","40","25","0","0","0","0","0","0","4.6439","4.6439","0","0","1","1","1","1","0","25","25"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","joint_basin","40","25","1.8406","1.6816","1.6816","1.6212","0.3964","0.3621","2.8032","2.9623","0.1591","0.1591","1","1","1","1","0.8808","9","11"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","center_of_mass","40","75","0.3834","0.5102","0.2969","0.1167","0.0616","0.0477","5.8454","5.932","0.0865","-0.1268","1","1","1","1","0.3045","63","65"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","relative_distance","40","75","0","0","0","0","0","0","6.2288","6.2288","0","0","1","1","1","1","0","75","75"
"near-enrichment repulsive","near_enrichment_repulsive_alpha_0.3","repulsive","0.3","joint_basin","40","75","3.4256","3.2369","3.2369","3.1159","0.55","0.5197","2.8032","2.9919","0.1887","0.1887","1","1","1","1","0.9096","13","17"
