# Exhaustive reactive allocation: results

All 36 declared tables completed; 36 distinct physical kernels.
Maximum checked residual 8.88e-10; peak worker 364.5 MiB.

Finite whole-history lushness is primary. D/S values bound actual marginal histories.
Possible subject maximizers are outer sets; overlapping intervals do not resolve a winner.
Policies differ in hardwired apparatus-dependent control, with the same paid selector and physical substrate.

| T | Cadence | Whole winner (response at 1 / 2 units) | Gain vs hold | Best nonconstant minus best constant | D possible | S possible |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 16 | 0.125 | idle__idle | +18.996388 | -0.731147 | 5 | 6 |
| 16 | 0.25 | idle__idle | +16.339990 | -0.616724 | 5 | 6 |
| 16 | 0.5 | idle__idle | +13.652863 | -0.497081 | 5 | 6 |
| 64 | 0.125 | idle__donate | +79.653209 | +4.579475 | 5 | 23 |
| 64 | 0.25 | idle__donate | +67.520636 | +3.691920 | 5 | 23 |
| 64 | 0.5 | idle__donate | +55.406865 | +2.865168 | 5 | 22 |
| 256 | 0.125 | donate__extract | +338.838486 | +5.763627 | 14 | 20 |
| 256 | 0.25 | donate__extract | +286.446242 | +4.869839 | 14 | 21 |
| 256 | 0.5 | donate__extract | +234.432822 | +4.042148 | 14 | 20 |
| 1024 | 0.125 | donate__extract | +1160.875170 | +13.469271 | 13 | 20 |
| 1024 | 0.25 | extract__donate | +990.638626 | +13.048743 | 13 | 22 |
| 1024 | 0.5 | extract__donate | +823.237581 | +14.324957 | 13 | 19 |

## Full policy map at T256, cadence 0.25

| Policy | Whole gain vs hold | D gain interval | S gain interval | Net transfer to D | D energy change vs hold | S energy change vs hold |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| donate__extract | +286.446242 | [+254.5371, +306.4701] | [+44.8877, +95.2482] | +0.772098 | +0.015699 | -0.090203 |
| extract__donate | +285.475623 | [+254.7094, +307.3337] | [+40.2561, +89.9384] | +0.426527 | -0.029196 | -0.055887 |
| extract__extract | +281.576403 | [+249.7757, +300.9971] | [+42.9121, +92.9109] | +0.960083 | +0.073189 | -0.119165 |
| idle__extract | +280.577586 | [+249.8770, +300.5486] | [+36.3973, +85.6250] | +0.854880 | +0.042044 | -0.104519 |
| combined__extract | +280.407911 | [+247.5186, +298.8231] | [+39.9685, +88.9039] | +0.897319 | +0.031361 | -0.134602 |
| combined__donate | +276.567121 | [+246.5029, +298.8132] | [+32.7263, +80.1165] | +0.253406 | -0.016545 | -0.037858 |
| donate__donate | +276.372789 | [+249.1441, +301.7750] | [+32.9674, +81.0225] | +0.091946 | +0.023291 | +0.015529 |
| idle__donate | +275.301766 | [+247.8876, +299.5762] | [+27.7930, +75.2940] | +0.138091 | -0.003350 | -0.002134 |
| extract__combined | +274.834100 | [+242.7303, +293.8664] | [+36.4998, +84.1747] | +0.880546 | +0.031132 | -0.126425 |
| donate__combined | +272.178241 | [+241.6479, +293.0987] | [+34.0982, +81.0266] | +0.596654 | +0.027511 | -0.066220 |
| idle__combined | +265.940449 | [+236.6706, +286.8483] | [+25.3065, +70.7691] | +0.666979 | +0.052649 | -0.078637 |
| productive__extract | +265.008657 | [+232.7897, +283.5857] | [+29.9808, +78.0235] | +0.702005 | +0.045933 | -0.108501 |
| combined__combined | +261.056327 | [+231.1216, +281.6583] | [+27.0365, +72.1146] | +0.662220 | +0.090757 | -0.083590 |
| productive__donate | +260.592003 | [+231.4361, +283.2454] | [+22.3378, +68.8071] | +0.035954 | +0.000497 | -0.006504 |
| productive__combined | +250.753896 | [+219.9085, +270.2182] | [+19.1571, +63.3104] | +0.514891 | +0.056279 | -0.082534 |
| extract__productive | +249.389222 | [+219.0661, +269.3123] | [+20.8570, +66.5718] | +0.640362 | +0.041906 | -0.092687 |
| donate__productive | +246.471926 | [+217.8352, +268.4195] | [+18.2104, +63.1950] | +0.334989 | +0.041738 | -0.029137 |
| combined__productive | +240.495973 | [+210.7581, +260.6762] | [+13.4256, +56.4465] | +0.467214 | +0.052853 | -0.073979 |
| idle__productive | +239.336783 | [+212.0480, +261.3267] | [+8.8931, +51.9764] | +0.385680 | +0.066662 | -0.039122 |
| extract__idle | +236.493517 | [+207.5280, +255.8540] | [+21.1360, +67.1652] | +0.669812 | +0.046305 | -0.084515 |
| donate__idle | +233.244946 | [+206.0411, +254.6977] | [+18.2317, +63.4817] | +0.351986 | +0.046171 | -0.020956 |
| combined__idle | +227.443073 | [+199.0866, +247.0610] | [+13.7604, +57.1542] | +0.499215 | +0.057340 | -0.065744 |
| productive__productive | +224.595126 | [+197.1593, +246.5120] | [+4.4660, +46.5547] | +0.271901 | +0.111810 | -0.029695 |
| idle__idle | +223.919394 | [+199.0991, +246.5029] | [+9.2708, +52.8217] | +0.413124 | +0.119729 | -0.018616 |
| productive__idle | +211.844216 | [+184.2534, +231.7238] | [+3.7282, +45.7481] | +0.282974 | +0.073976 | -0.035073 |
| hold__extract | +210.159639 | [+180.0044, +229.6179] | [+31.4233, +80.1440] | +0.766979 | +0.073934 | -0.107453 |
| hold__donate | +203.058672 | [+176.9063, +227.7191] | [+22.5171, +69.4936] | -0.011419 | +0.021897 | +0.014996 |
| hold__combined | +192.670846 | [+164.1789, +213.1586] | [+17.9501, +61.9304] | +0.524490 | +0.086911 | -0.075151 |
| hold__productive | +161.660833 | [+135.3306, +183.2348] | [-0.9249, +40.0996] | +0.218162 | +0.097104 | -0.028545 |
| extract__hold | +161.618917 | [+133.1567, +182.5667] | [+28.3094, +77.5677] | +0.789274 | +0.079468 | -0.100599 |
| donate__hold | +156.918696 | [+131.5258, +181.8680] | [+22.1590, +69.8707] | +0.212803 | +0.048531 | -0.003587 |
| hold__idle | +151.889727 | [+128.0208, +174.0673] | [+1.6214, +43.8104] | +0.278494 | +0.110535 | -0.017309 |
| combined__hold | +145.890948 | [+118.6108, +167.4834] | [+16.6635, +61.2065] | +0.572298 | +0.088878 | -0.075277 |
| idle__hold | +129.777897 | [+105.8691, +153.4047] | [+8.7232, +53.2437] | +0.430716 | +0.099614 | -0.027697 |
| productive__hold | +115.723701 | [+90.1397, +138.0207] | [-0.8013, +40.9014] | +0.287450 | +0.077586 | -0.034019 |
| hold__hold | +0.000000 | [+0.0000, +0.0000] | [+0.0000, +0.0000] | +0.171964 | +0.000000 | +0.000000 |

## Scope

All policies include the same physical registers; hold still permits autonomous selector relaxation.
Constant tables command a target rather than pinning the selector. No abstract action-label entropy is counted.
Material gains, net flow and breadth are separate. Donating/extracting mode names do not establish actual net direction.
This fixed-contact count assay includes paid transfer, production and their combination, but no spatial confinement, irreversible harm, discovery or certified conscious valuers.
A whole-field rate difference across policies is not a same-generator root advantage. No unbounded asymptotic moral priority is used.
The three-cadence map is temporal sensitivity evidence, not invariance across state grains.
SCORES.csv preserves every policy, horizon and cadence; PHYSICAL.csv preserves full signed resource/event ledgers.
PAIRWISE.csv retains 7560 pair/clock/horizon comparisons; 0 have certified D/whole opposition and 19 have certified D/S opposition. These counts are comparisons, not independent observations or domination verdicts.
TEMPORAL_SIGNS.csv flags 0 policy/horizon sign reversals against hold across the three cadences.
Matching realized work or activity is a diagnostic follow-up, not a restriction imposed on the primary optimizer.
