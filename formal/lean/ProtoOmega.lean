import ProtoOmega.Presentation.Native
import ProtoOmega.Recoverability.LegacyBridge
import ProtoOmega.Recoverability.Native
import ProtoOmega.Recoverability.NativeExamples
import ProtoOmega.Recoverability.NormalLax
import ProtoOmega.Recoverability.Recurrent
import ProtoOmega.Recoverability.RecurrentNative
import ProtoOmega.Recoverability.RecurrentNativeExamples
import ProtoOmega.Separations.MarginalJointNative
import ProtoOmega.Transport.LegacyBridge
import ProtoOmega.Transport.Native
import ProtoOmega.Transport.NativeExamples
import ProtoOmega.Transport.Preorder

/-!
ProtoOmega umbrella.

This layer contains derived presentation, transport, and recoverability
machinery over the Alpha primitive floor. `ProtoOmega.Presentation.Native`
separates presentation-native distinction/transport structures from full Alpha
substrates. `ProtoOmega.Transport.Native` and
`ProtoOmega.Recoverability.Native`, and
`ProtoOmega.Recoverability.RecurrentNative` are Alpha-native replacements for
legacy transport/recoverability facades. `MarginalJointNative` is the native
finite separation replacing the legacy marginal/joint facade. The deprecated
`ProtoOmega.Separations.MarginalJoint` facade remains available for direct
compatibility imports but is no longer part of this active umbrella.
-/
