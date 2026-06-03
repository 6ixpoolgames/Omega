import Lake
open Lake DSL

package omega_formal where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.30.0"

lean_lib OmegaCore where
  roots := #[`OmegaCore]
