/-!
OmegaProper.Decision.CertificateStaleness

Static compensation certificate staleness, in the narrow coverage sense.

This file closes the preregistered v0 target only: a fixed-domain certificate
that covers a register at time `n` is stale at `n + 1` when sound register
growth adds a relevant fact outside the certificate domain.

It does not prove replacement, rights, cross-valuer compensation, value,
standing, patienthood, agency, identity, or Omega validation.
-/

namespace OmegaProper
namespace Decision
namespace CertificateStaleness

universe u

/-- A time-indexed declared register of facts. -/
abbrev Register (Fact : Type u) := Nat -> Fact -> Prop

/-- Monotone register growth: facts once declared remain declared. -/
def MonotoneRegister (R : Register Fact) : Prop :=
  forall n f, R n f -> R (n + 1) f

/--
A static certificate has a fixed domain of facts it covers.

The preregistered protocol treats this domain as finite. The v0 theorem below
uses only fixed-domain coverage; finiteness is the non-omniscience reading, not
a hidden proof step.
-/
structure StaticCertificate (Fact : Type u) where
  dom : Fact -> Prop

/-- `c` covers register time `n` when every registered fact is in `c.dom`. -/
def Covers (c : StaticCertificate Fact) (R : Register Fact) (n : Nat) : Prop :=
  forall f, R n f -> c.dom f

/--
A growth step relevant to certificate staleness: a newly registered fact at
`n + 1` lies outside the fixed certificate domain.
-/
def GrowthOutsideCertificate
    (c : StaticCertificate Fact) (R : Register Fact) (n : Nat) (f : Fact) :
    Prop :=
  R (n + 1) f /\ Not (c.dom f)

/--
Static-certificate staleness.

If the next register contains a fact outside the fixed certificate domain, then
the old certificate cannot cover the next register. The content is the growth
witness; this is coverage language only.
-/
theorem static_certificate_stale
    (c : StaticCertificate Fact)
    (R : Register Fact)
    (n : Nat)
    {f : Fact}
    (_hCover : Covers c R n)
    (hGrowth : GrowthOutsideCertificate c R n f) :
    Not (Covers c R (n + 1)) := by
  intro hCoverNext
  exact hGrowth.2 (hCoverNext f hGrowth.1)

/--
Any registered fact outside a static certificate domain witnesses a time at
which the certificate does not cover the register.
-/
theorem exists_time_not_covers_of_fact_outside_domain
    (c : StaticCertificate Fact)
    (R : Register Fact)
    (hOutside : exists n, exists f, R n f /\ Not (c.dom f)) :
    exists n, Not (Covers c R n) := by
  rcases hOutside with ⟨n, f, hRf, hNotDom⟩
  exact ⟨n, by
    intro hCover
    exact hNotDom (hCover f hRf)⟩

end CertificateStaleness
end Decision
end OmegaProper
