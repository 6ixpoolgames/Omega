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

lean_lib AlphaCalculus where
  roots := #[`AlphaCalculus]

lean_lib OmegaAdapters where
  roots := #[`OmegaAdapters]

lean_lib AlphaAdapters where
  roots := #[`AlphaAdapters]

lean_lib OmegaProper where
  roots := #[`OmegaProper]

lean_lib Omega where
  roots := #[`Omega]

lean_lib OmegaArchive where
  roots := #[`OmegaArchive]

lean_lib OmegaV2 where
  roots := #[`OmegaV2]

lean_lib AlphaOmega where
  roots := #[`AlphaOmega]
