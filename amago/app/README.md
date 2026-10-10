# AMAGO para iOS (App Store Connect)

La app es el juego (`../index.html` y sus recursos) dentro de una app nativa hecha con [Capacitor](https://capacitorjs.com). El modo contra el bot funciona sin internet; el online conecta con el servidor de Railway.

No hace falta un Mac: GitHub Actions compila en un Mac de la nube, firma con tu cuenta de Apple y sube la compilación a App Store Connect (TestFlight). Workflow: `.github/workflows/amago-ios.yml`.

## Una sola vez

1. **Apple Developer Program** (99 €/año): [developer.apple.com/programs](https://developer.apple.com/programs/enroll/).
2. **Identificador de la app:** en [Certificates, IDs & Profiles → Identifiers](https://developer.apple.com/account/resources/identifiers/list) crea un *App ID* con el bundle ID `com.enriquemateo.amago`.
3. **La app en App Store Connect:** [appstoreconnect.apple.com](https://appstoreconnect.apple.com) → Apps → **+** → Nueva app. Plataforma iOS, nombre *AMAGO* (u otro libre), idioma español, bundle ID `com.enriquemateo.amago`, SKU `amago`.
4. **Clave de la API:** App Store Connect → Usuarios y acceso → **Integraciones → App Store Connect API** → generar clave con acceso **Administrador** (la firma automática necesita poder crear certificados). Descarga el `.p8` (solo se puede una vez) y apunta el *Key ID* y el *Issuer ID*.
5. **Team ID:** [developer.apple.com/account](https://developer.apple.com/account) → Membership details.
6. **En GitHub**, repo → Settings → Secrets and variables → Actions:
   - Secretos: `APPLE_TEAM_ID`, `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8` (pega el contenido entero del `.p8`).
   - Variable (pestaña *Variables*): `AMAGO_SERVER` = la dirección de Railway, por ejemplo `https://amago-production.up.railway.app`.

## Cada versión

Sube una etiqueta con la versión: `git tag amago-ios-v1.0.0 && git push origin amago-ios-v1.0.0`. El número de compilación sube solo. En unos 15 minutos la compilación aparece en App Store Connect → TestFlight.

## Para probar en local con un Mac

```bash
cd amago/app
npm install
AMAGO_SERVER=https://tu-servidor npm run sync
npx cap open ios
```

## Privacidad (obligatorio en App Store Connect)

- **URL de la política de privacidad:** `https://<tu-servidor-de-railway>/privacidad` (el archivo es `amago/privacidad.html`; rellena antes `[NOMBRE DEL RESPONSABLE]` y `[CORREO DE CONTACTO]`). También se abre desde Ajustes dentro del juego.
- **App Privacy** (cuestionario de Apple): no hay seguimiento ni anuncios. Datos que se envían: el nombre de jugador y los trofeos durante las partidas online (función de la app, no vinculados a la identidad).
- **Contenido de usuarios:** en el modo Online el rival ve un apodo automático; en salas con amigos los nombres pasan por un filtro de insultos.

## Notas

- Solo iPhone y en vertical. Sin cifrado propio (`ITSAppUsesNonExemptEncryption = false`), así que no hay trámite de exportación.
- Las compras con dinero real están desactivadas en la app hasta integrar las compras de Apple (StoreKit).
- El icono (`ios/App/App/Assets.xcassets/AppIcon.appiconset`, 1024×1024 sin transparencia) y la pantalla de carga son provisionales.
