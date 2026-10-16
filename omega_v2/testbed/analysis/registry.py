"""Versioned readouts declare requirements and emit typed interpretation records."""
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class SurveySpec:
    id: str
    version: str
    units: str
    evaluate: Callable
    requires: tuple[str, ...] = ()
    estimator: str = "finite-state numerical propagation"


class ReadoutRegistry:
    def __init__(self):
        self._readouts = {}

    def register(self, spec):
        if spec.id in self._readouts:
            raise ValueError(f"Duplicate readout {spec.id}")
        self._readouts[spec.id] = spec

    def evaluate(self, model, context):
        results = {}
        for name, spec in self._readouts.items():
            missing = [c for c in spec.requires if model["capabilities"].get(c) is not True]
            record = {"id": name, "version": spec.version, "units": spec.units,
                      "estimator": spec.estimator, "status": "open_outcome"}
            if missing:
                record.update(status="unsupported", value=None,
                              reason=f"Missing capabilities: {missing}")
            else:
                record["value"] = spec.evaluate(model, context)
            results[name] = record
        return results


def interpret_channel(result):
    """Descriptive findings, with no survival reward or automatic ethical label."""
    findings = []
    tolerance=result.get('comparison_tolerance',1e-9)
    if result.get("channel_empty", False):
        findings.append({"status": "open_outcome", "id": "no_exact_closure",
                         "text": "No structural closure in this law; inspect deadline recovery."})
    if result.get("winner_active", float("inf")) < result.get("benchmark_active", -float("inf"))-tolerance:
        findings.append({"status": "open_outcome", "id": "margin_tradeoff",
                         "text": "Breadth winner retains less functioning capacity; a margin trade-off."})
    if result.get("winner_closure", -float("inf")) > result.get("benchmark_closure", float("inf"))+tolerance:
        findings.append({"status": "open_outcome", "id": "closure_tension",
                         "text": "Breadth and apparatus-channel protection diverge in this comparison."})
    if result.get("seed_excess", 0) < -tolerance:
        findings.append({"status": "open_outcome", "id": "negative_preparation_result",
                         "text": "The seed is behind its matched coarse reference."})
    return findings


def score_outcomes(metrics, definitions):
    """Score frozen numerical predicates through named operators, never eval."""
    scored=[]
    operators={'eq':lambda x,y,t:abs(x-y)<=t,'le':lambda x,y,t:x<=y+t,
               'ge':lambda x,y,t:x>=y-t,'lt':lambda x,y,t:x<y-t,'gt':lambda x,y,t:x>y+t}
    for definition in definitions:
        name=definition['metric'];op=definition['operator']
        record={'id':definition['id'],'metric':name,'operator':op}
        if name not in metrics or metrics[name] is None:
            record.update(status='unsupported',value=None,reason='Metric not available for this law')
        elif op=='record':record.update(status='open_outcome',value=metrics[name])
        else:
            threshold=definition['threshold'];tol=definition.get('tolerance',0.)
            record.update(status='pass' if operators[op](metrics[name],threshold,tol) else 'fail',
                          value=metrics[name],threshold=threshold,tolerance=tol)
        scored.append(record)
    return scored
