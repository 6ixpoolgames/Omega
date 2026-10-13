# Bounded resource-use feedback: first implementation

The module closes a paid access/resource conversion/carrier return pathway and
allows that carrier to pay for construction. The same thermal carrier and
apparatus routes remain in every arm; no independent driven carrier inlet is
present. Energies and all kinetic parameters are frozen in PROTOCOL.json before
comparisons. Each internal route has its thermodynamic reverse, including the
new coupling. Population is a count with explicit precursor and carrier pools.

Thirty-six exact cases covered catalytic/uncatalytic/absent feedback, capacities
one/two, maintained/depleted inflow, and cadences0.125/0.25/0.5. Primary comparison
is capacity1/cadence0.25. All four frozen mechanism predictions passed. Smoke:
0.757s,121.11MiB; scientific run:1.403s,78.71MiB; no caps under120s/1GiB/32MiB.

At the primary cadence, catalytic versus absent changes finite history entropy
at T64 from35.721282 to36.363592bits and stationary apparatus from0.115945 to
0.116924. The rate increment is0.002062bits/time and remains positive at all
three cadences. Recovery endpoint probability after apparatus loss increases
from0.079633 to0.079973. These are modest changes.

The uncatalytic control reaches36.601296bits and0.119108 mean apparatus. It
outperforms the catalytic arm. This is a mechanism control with different coupling
availability, not an activity-matched gas baseline. It remains a live adverse
comparison rather than being removed for lacking organization.

Catalytic feedback generates net0.000184charged carriers/time while access spends
0.000595, replacing30.94%. The remaining energy is principally supplied through
thermal routes. This regime does not demonstrate autonomous upkeep. With the
resource inflow removed, all arms have the same asymptotic rate after depletion
(maxspread1.9e-15), and apparatus returns to thermal mean0.119203; the driven
catalytic apparatus mean is slightly below that. The small gain against the
absent-feedback driven arm does not establish superiority over the thermal state.

Capacity2 permits construction from one active unit to two; the catalytic arm
hits two by T64 with probability0.090202 versus0.077302 without feedback. This
is paid growth inside a fixed inventory, not open-ended compounding.

The new composition interface supports named heterogeneous subsystems and native
joint transfer modules. Independent kernel/product entropy checks and an explicit
energy-conserving carrier-transfer check pass. Strong-lumping checks reject
hidden unequal macro continuations, while clearly distinguishing a correct macro
transition law from preservation of fine-history entropy.

Future compatibility is partial and tested, not a claim that all desired physics
is implemented. See EXTENSION_CONTRACTS.md for lazy enumeration, material growth,
native joint enabling, cross-scale maps, observation costs and coupled agency.
This comparison has no optimizing controller; adding the feedback law to the
controlled ecology is the next integration step after reading these outcomes.

See [automated results](report/RESULTS.md), [full compact evidence](report/SUMMARY.json),
[frozen prescription](PROTOCOL.json), and [extension contracts](EXTENSION_CONTRACTS.md).

Interpretation correction: the v1 'uncatalytic' arm is an always-available coupling
with the same coefficient as a fully active catalyst, not slow uncatalyzed
chemistry. The [corrected shared-law benchmark](../corrected_catalysis/RESULTS.md)
retains positive basal feedback and speeds both directions when apparatus exists.
Historical v1 rows remain unchanged.
