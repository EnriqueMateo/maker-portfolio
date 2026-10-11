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
    private var pending: CAPPluginCall?

    @objc func signIn(_ call: CAPPluginCall) {
        pending = call
        DispatchQueue.main.async {
            let request = ASAuthorizationAppleIDProvider().createRequest()
            request.requestedScopes = [.fullName, .email]
            if let nonce = call.getString("nonce") { request.nonce = nonce }
            let controller = ASAuthorizationController(authorizationRequests: [request])
            controller.delegate = self
            controller.presentationContextProvider = self
            controller.performRequests()
        }
    }

    public func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return bridge?.viewController?.view.window ?? ASPresentationAnchor()
    }

    public func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        guard let call = pending else { return }
        pending = nil
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
            "email": cred.email ?? "",
            "givenName": cred.fullName?.givenName ?? ""
        ])
    }

    public func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        guard let call = pending else { return }
        pending = nil
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
