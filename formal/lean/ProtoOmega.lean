import ProtoOmega.Recoverability.LegacyBridge
import ProtoOmega.Recoverability.Native
import ProtoOmega.Recoverability.NativeExamples
import ProtoOmega.Recoverability.NormalLax
import ProtoOmega.Recoverability.Recurrent
import ProtoOmega.Recoverability.RecurrentNative
import ProtoOmega.Recoverability.RecurrentNativeExamples
import ProtoOmega.Separations.MarginalJoint
import ProtoOmega.Separations.MarginalJointNative
import ProtoOmega.Transport.LegacyBridge
import ProtoOmega.Transport.Native
import ProtoOmega.Transport.NativeExamples
import ProtoOmega.Transport.Preorder

/-!
ProtoOmega umbrella.

This layer contains derived transport and recoverability machinery over the
Alpha primitive floor. `ProtoOmega.Transport.Native` and
`ProtoOmega.Recoverability.Native`, and
`ProtoOmega.Recoverability.RecurrentNative` are Alpha-native replacements for
legacy transport/recoverability facades. `MarginalJointNative` is the native
finite separation replacing the legacy marginal/joint facade. Other modules
remain facade imports over checked legacy OmegaCore modules until physical
namespace migration.
-/
