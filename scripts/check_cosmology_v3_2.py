"""Check edition assembly, local links and the new elementary witnesses."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
from collections import defaultdict
from fractions import Fraction

from build_cosmology_v3_2 import EDITION, OUTPUT, ROOT, build


def entropy(values, weights):
    mass = defaultdict(Fraction)
    for value, weight in zip(values, weights, strict=True):
        mass[value] += weight
    return -sum(float(p) * math.log2(float(p)) for p in mass.values() if p)


def information_summary(inputs, records, weights):
    hx, hf = entropy(inputs, weights), entropy(records, weights)
    hxf = entropy(list(zip(inputs, records, strict=True)), weights)
    mi = hx + hf - hxf
    singles = sum(
        entropy([x[i] for x in inputs], weights)
        + hf
        - entropy([(x[i], f) for x, f in zip(inputs, records, strict=True)], weights)
        for i in range(3)
    )
    return [hf, mi - singles]


def partition(records):
    return tuple(tuple(i for i, other in enumerate(records) if other == value) for value in records)


def repairs(records):
    result = []
    for erased in range(3):
        fibres = defaultdict(set)
        for row in records:
            fibres[tuple(row[i] for i in range(3) if i != erased)].add(row[erased])
        result.append(all(len(values) == 1 for values in fibres.values()))
    return result


def one_gate_outputs(records):
    outputs = {tuple(0 for _ in records), tuple(1 for _ in records)}
    for n in (1, 2):
        for controls in itertools.combinations(range(3), n):
            for polarities in itertools.product((0, 1), repeat=n):
                outputs.add(
                    tuple(
                        int(all(row[c] == p for c, p in zip(controls, polarities, strict=True)))
                        for row in records
                    )
                )
    return outputs


def main():
    assert OUTPUT.read_text(encoding="utf-8") == build(), "Stale combined edition"
    audit = ROOT / "docs/research_notes/omega_v2/opus_towards_v3_2_assessment_audit_2026-10-03.md"
    links = 0
    for path in [*EDITION.glob("*.md"), audit]:
        text = path.read_text(encoding="utf-8")
        assert text.count(chr(96) * 3) % 2 == 0, path
        assert not re.search(r"^## [^\n]+\n\n## ", text, re.MULTILINE), path
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            assert (path.parent / target.split("#")[0].strip("<>")).exists(), (path, target)
            links += 1

    inputs = list(itertools.product((0, 1), repeat=3))
    weights = [Fraction(1, 5) ** sum(x) * Fraction(4, 5) ** (3 - sum(x)) for x in inputs]
    assert sum(weights) == 1
    a = [(s ^ f, 0, 1 - s) for s, f, _ in inputs]
    b = [(0, s, f) for s, f, _ in inputs]
    assert partition(a) == partition(b)
    target = tuple(1 - f for _, f, _ in inputs)
    assert target not in one_gate_outputs(a)
    assert target in one_gate_outputs(b)
    assert tuple(row[0] ^ row[2] for row in a) == target
    access = information_summary(inputs, a, weights)
    assert all(abs(x - y) < 1e-10 for x, y in zip(access, [1.4438561897747246, 0]))
    assert access == information_summary(inputs, b, weights)
    uv = [((1 - f1) & (1 - f2), 1 - s) for s, f1, f2 in inputs]
    ra = [(u, u & v, v) for u, v in uv]
    rb = [(u, u, v) for u, v in uv]
    parity = [(u, v, u ^ v) for u, v in uv]
    assert partition(ra) == partition(rb)
    assert repairs(ra) == [False, True, False]
    assert repairs(rb) == [True, True, False]
    assert repairs(parity) == [True, True, True]
    recovery = information_summary(inputs, ra, weights)
    assert all(
        abs(x - y) < 1e-10
        for x, y in zip(recovery, [1.6646112841428546, 0.21240176256428756], strict=True)
    )
    assert recovery == information_summary(inputs, rb, weights)
    dependent = information_summary([(0, 0, 0), (1, 1, 1)], [0, 1], [Fraction(1, 2)] * 2)
    assert dependent == [1.0, -2.0]
    source = ROOT / "docs/cosmology/v3.1-source/OMEGA_COSMOLOGY_V3_1_COMPLETE.md"
    metadata = json.loads(source.with_name("retrieval.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata["saved_utf8_lf_sha256"]
    result = {
        "status": "passed",
        "scope": "Edition assembly, local link targets, Examples 19-21 and tally arithmetic",
        "chapters": 17,
        "local_links_checked": links,
        "access_H_Syn": access,
        "symmetric_decoder_costs": [2, 1],
        "recovery_H_Syn": recovery,
        "repairable_locations": [repairs(ra), repairs(rb)],
        "parity_repair": repairs(parity),
        "dependent_H_Syn": dependent,
        "subset_tallies": [10 * 2**9, 2**13 - 1],
        "limits": "No new atlas, physics, ethics sweep or inherited-proof validation.",
    }
    (EDITION / "publication_checks.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
