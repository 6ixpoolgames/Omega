import Lake
open Lake DSL

package omega_formal where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.30.0"

lean_lib OmegaCore where
  roots := #[`OmegaCore]

lean_lib AlphaCore where
  roots := #[`AlphaCore]

lean_lib ProtoOmega where
  roots := #[`ProtoOmega]

lean_lib OmegaAdapters where
  roots := #[`OmegaAdapters]

lean_lib OmegaProper where
  roots := #[`OmegaProper]

lean_lib OmegaArchive where
  roots := #[`OmegaArchive]

lean_lib AlphaOmega where
  roots := #[`AlphaOmega]
