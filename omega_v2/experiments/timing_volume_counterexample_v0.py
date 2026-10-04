"""Common relay/assembly dynamics for the frozen timing-volume falsification."""

from fractions import Fraction

from omega_v2.finite.timed_execution import Law, Net, Transition, state

PROTOCOL = "docs/research_notes/omega_v2/timing_volume_counterexample_protocol_v0.md"
PROTOCOL_SHA256 = "0d11446db47cab51d23131b2b5412b5dbc713d837b3c045ac837d3ecf63cd538"
FUEL = 10
BLANK = -1
HORIZONS = (0.5, 1.0, 2.0, 4.0, 8.0)
BOUNDARIES = (1, 2, 3, 4, 5, 8, 9, 10)
PREPARATION_BILL = {"loaded_fuel": 10, "register_and_actuator_units": 12}


def relay_net() -> Net:
    """One transition table; scenario names are not inputs to the dynamics."""
    transitions = []

    def add(fuel, phase, name, reads, writes, rate=Fraction(1)):
        guard = {"fuel": fuel, "spent": FUEL - fuel, "phase": phase, **reads}
        update = {"fuel": fuel - 1, "spent": FUEL - fuel + 1,
                  "phase": (phase + 1) % 5, **writes}
        transitions.append(Transition(f"{name}@fuel{fuel}", state(**guard),
                                      state(**update), rate))

    for fuel in range(1, FUEL + 1):
        for bit in (0, 1):
            add(fuel, 0, f"source_write_{bit}", {"source": bit},
                {"record": bit, "relay": BLANK, "downstream": BLANK})
        add(fuel, 1, "retain_record", {"clear": 0}, {})
        add(fuel, 1, "clear_record", {"clear": 1}, {"record": BLANK})
        add(fuel, 2, "disconnected_relay", {"wire": 0}, {"relay": BLANK})
        for bit in (0, 1):
            add(fuel, 2, f"relay_record_{bit}", {"wire": 1, "record": bit}, {"relay": bit})
            add(fuel, 2, f"blank_reader_{bit}", {"wire": 1, "record": BLANK},
                {"relay": bit}, Fraction(1, 2))
            add(fuel, 3, f"assemble_from_record_{bit}", {"socket": 1, "record": bit},
                {"link": 1, "wire": 1})
        for rotor in (0, 1):
            add(fuel, 3, f"rotate_unaligned_{rotor}", {"socket": 0, "rotor": rotor},
                {"rotor": 1 - rotor})
            add(fuel, 3, f"rotate_unkeyed_{rotor}",
                {"socket": 1, "record": BLANK, "rotor": rotor}, {"rotor": 1 - rotor})
        add(fuel, 4, "disconnected_downstream", {"link": 0}, {"downstream": BLANK})
        for value in (BLANK, 0, 1):
            add(fuel, 4, f"forward_{value}", {"link": 1, "relay": value},
                {"downstream": value})
    return Net(tuple(transitions))


def preparations() -> dict[str, Law]:
    switches = {"intact": (1, 0, 1), "damaged": (0, 0, 1),
                "erased": (1, 1, 1), "cycling": (1, 0, 0)}
    return {
        name: {
            state(source=bit, record=BLANK, relay=BLANK, downstream=BLANK,
                  wire=wire, clear=clear, socket=socket, link=0, rotor=0,
                  phase=0, fuel=FUEL, spent=0): Fraction(1, 2)
            for bit in (0, 1)
        }
        for name, (wire, clear, socket) in switches.items()
    }


def calibration_nets() -> dict[str, tuple[Net, Law, int]]:
    independent = Net((
        Transition("a", state(a=0), state(a=1)),
        Transition("b", state(b=0), state(b=1)),
    ))
    exclusive = Net((
        Transition("a", state(token=1), state(token=0, a=1)),
        Transition("b", state(token=1), state(token=0, b=1)),
    ))
    enabling = Net((
        Transition("a", state(a=0), state(a=1)),
        Transition("b", state(a=1, b=0), state(b=1)),
    ))
    return {
        "independent": (independent, {state(a=0, b=0): Fraction(1)}, 2),
        "exclusive": (exclusive, {state(a=0, b=0, token=1): Fraction(1)}, 1),
        "enabling": (enabling, {state(a=0, b=0): Fraction(1)}, 2),
    }
