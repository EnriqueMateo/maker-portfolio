import Foundation
import Capacitor
import AuthenticationServices

/// Iniciar sesión con Apple (plugin propio de AMAGO).
/// JS: Capacitor.registerPlugin("AppleAuth").signIn({ nonce }) → { identityToken, authorizationCode, user, email, givenName }
@objc(AppleAuthPlugin)
public class AppleAuthPlugin: CAPPlugin, CAPBridgedPlugin, ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    public let identifier = "AppleAuthPlugin"
    public let jsName = "AppleAuth"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "signIn", returnType: CAPPluginReturnPromise)
    ]
    // solo se toca en el hilo principal
    private var pending: CAPPluginCall?
    private var controller: ASAuthorizationController?

    @objc func signIn(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            // un inicio de sesión a la vez: el segundo se rechaza en vez de dejar colgado el primero
            if self.pending != nil {
                call.reject("Ya hay un inicio de sesión en marcha", "BUSY")
                return
            }
            self.pending = call
            let request = ASAuthorizationAppleIDProvider().createRequest()
            request.requestedScopes = [.email] // sin el nombre: no lo necesitamos y así no se recoge
            if let nonce = call.getString("nonce") { request.nonce = nonce }
            let controller = ASAuthorizationController(authorizationRequests: [request])
            controller.delegate = self
            controller.presentationContextProvider = self
            self.controller = controller // se retiene mientras dura el flujo
            controller.performRequests()
        }
    }

    public func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        if let w = bridge?.viewController?.view.window { return w }
        let scene = UIApplication.shared.connectedScenes.first { $0.activationState == .foregroundActive } as? UIWindowScene
        return scene?.windows.first { $0.isKeyWindow } ?? ASPresentationAnchor()
    }

    public func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        guard let call = pending else { return }
        pending = nil
        self.controller = nil
        guard let cred = authorization.credential as? ASAuthorizationAppleIDCredential,
              let tokenData = cred.identityToken,
              let token = String(data: tokenData, encoding: .utf8) else {
            call.reject("Apple no devolvió el token", "NO_TOKEN")
            return
        }
        let code = cred.authorizationCode.flatMap { String(data: $0, encoding: .utf8) } ?? ""
        call.resolve([
            "identityToken": token,
            "authorizationCode": code,
            "user": cred.user,
            "email": cred.email ?? ""
        ])
    }

    public func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        guard let call = pending else { return }
        pending = nil
        self.controller = nil
        if let e = error as? ASAuthorizationError, e.code == .canceled {
            call.reject("Cancelado", "CANCELED")
        } else if let e = error as? ASAuthorizationError, e.code == .unknown {
            // típico cuando el iPhone no tiene Apple ID o el usuario cierra el aviso de Ajustes
            call.reject(error.localizedDescription, "NO_ACCOUNT")
        } else {
            call.reject(error.localizedDescription, "FAILED")
        }
    }
}
