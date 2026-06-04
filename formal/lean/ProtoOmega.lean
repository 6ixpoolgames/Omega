import ProtoOmega.Recoverability.NormalLax
import ProtoOmega.Recoverability.Recurrent
import ProtoOmega.Separations.MarginalJoint
import ProtoOmega.Transport.LegacyBridge
import ProtoOmega.Transport.Native
import ProtoOmega.Transport.NativeExamples
import ProtoOmega.Transport.Preorder

/-!
ProtoOmega umbrella.

This layer contains derived transport and recoverability machinery over the
Alpha primitive floor. `ProtoOmega.Transport.Native` is the first Alpha-native
replacement for a legacy transport facade. Other modules remain facade imports
over checked legacy OmegaCore modules until physical namespace migration.
-/
