import Foundation
import Capacitor
import StoreKit

/// Compras dentro de la app con StoreKit 2 (plugin propio de AMAGO).
/// Cada compra devuelve la transacción firmada por Apple (JWS); el servidor de AMAGO la comprueba y decide qué se entrega.
/// La transacción solo se cierra (finish) cuando la app confirma que el servidor la ha entregado, así que si se corta
/// la conexión a mitad, Apple la vuelve a dar en `unfinished` y se entrega al reconectar.
///
/// JS: Capacitor.Plugins.Store
///   products({ ids }) → { products: [{ id, price, value, currency }] }
///   buy({ id, account? }) → { ok, tx, jws, sku } | { ok: false, reason: "cancelled" | "pending" | "unknown" }
///   finish({ tx }) → {}
///   unfinished() → { list: [{ tx, sku, jws }] }
///   evento "purchase" → { tx, sku, jws } (compras aprobadas más tarde: «Preguntar para comprar», otro dispositivo…)
@objc(StorePlugin)
public class StorePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "StorePlugin"
    public let jsName = "Store"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "products", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "buy", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "finish", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "unfinished", returnType: CAPPluginReturnPromise)
    ]

    private var cache: [String: Product] = [:]
    private var updates: Task<Void, Never>?

    override public func load() {
        // compras que llegan fuera del flujo normal (aprobación de los padres, otro dispositivo, reintentos de Apple)
        updates = Task.detached { [weak self] in
            for await result in Transaction.updates {
                guard let self = self else { return }
                if let row = Self.row(result) { self.notifyListeners("purchase", data: row, retainUntilConsumed: true) }
            }
        }
    }

    deinit { updates?.cancel() }

    private static func row(_ result: VerificationResult<Transaction>) -> [String: Any]? {
        // se manda aunque StoreKit no la dé por verificada: quien decide es el servidor, con la firma
        let t: Transaction
        switch result {
        case .verified(let v): t = v
        case .unverified(let v, _): t = v
        }
        if t.revocationDate != nil { return nil }
        return ["tx": String(t.id), "sku": t.productID, "jws": result.jwsRepresentation]
    }

    private func product(_ id: String) async throws -> Product? {
        if let p = cache[id] { return p }
        for p in try await Product.products(for: [id]) { cache[p.id] = p }
        return cache[id]
    }

    @objc func products(_ call: CAPPluginCall) {
        let ids = (call.getArray("ids", String.self) ?? [])
        Task {
            do {
                let list = try await Product.products(for: ids)
                for p in list { cache[p.id] = p }
                call.resolve(["products": list.map { p in
                    ["id": p.id, "price": p.displayPrice, "value": NSDecimalNumber(decimal: p.price).doubleValue, "currency": p.priceFormatStyle.currencyCode]
                }])
            } catch {
                call.reject("No se pudieron cargar los productos", "PRODUCTS", error)
            }
        }
    }

    @objc func buy(_ call: CAPPluginCall) {
        guard let id = call.getString("id") else { call.reject("Falta el producto", "ARGS"); return }
        Task {
            do {
                guard let p = try await product(id) else { call.resolve(["ok": false, "reason": "unknown"]); return }
                var opts: Set<Product.PurchaseOption> = []
                // une la compra a la cuenta de AMAGO (UUID), para poder rastrearla en las notificaciones de Apple
                if let acc = call.getString("account"), let uuid = UUID(uuidString: acc) { opts.insert(.appAccountToken(uuid)) }
                switch try await p.purchase(options: opts) {
                case .success(let result):
                    if var row = Self.row(result) { row["ok"] = true; call.resolve(row) }
                    else { call.resolve(["ok": false, "reason": "revoked"]) }
                case .pending:
                    call.resolve(["ok": false, "reason": "pending"])
                case .userCancelled:
                    call.resolve(["ok": false, "reason": "cancelled"])
                @unknown default:
                    call.resolve(["ok": false, "reason": "unknown"])
                }
            } catch {
                call.reject("La compra no se pudo completar", "BUY", error)
            }
        }
    }

    @objc func finish(_ call: CAPPluginCall) {
        guard let tx = call.getString("tx"), let tid = UInt64(tx) else { call.resolve(); return }
        Task {
            for await result in Transaction.unfinished {
                let t: Transaction
                switch result { case .verified(let v): t = v; case .unverified(let v, _): t = v }
                if t.id == tid { await t.finish(); break }
            }
            call.resolve()
        }
    }

    @objc func unfinished(_ call: CAPPluginCall) {
        Task {
            var list: [[String: Any]] = []
            for await result in Transaction.unfinished { if let row = Self.row(result) { list.append(row) } }
            call.resolve(["list": list])
        }
    }
}
