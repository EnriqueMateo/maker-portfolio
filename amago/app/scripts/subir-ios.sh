#!/bin/bash
# Compila AMAGO para iOS y lo sube a App Store Connect (TestFlight) desde el Mac.
# Uso (desde la carpeta amago/app):  bash scripts/subir-ios.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SERVER="${AMAGO_SERVER:-https://maker-portfolio-production-7712.up.railway.app}"
echo "→ Preparando el juego (servidor: $SERVER)"
npm install --silent
AMAGO_SERVER="$SERVER" npm run sync
ARCH="$PWD/build/AMAGO.xcarchive"
rm -rf build && mkdir -p build
echo "→ Compilando (archive)"
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Release \
  -destination "generic/platform=iOS" -archivePath "$ARCH" -allowProvisioningUpdates DEVELOPMENT_TEAM=47TF333JU2 archive | tail -5
echo "→ Subiendo a App Store Connect"
xcodebuild -exportArchive -archivePath "$ARCH" -exportOptionsPlist scripts/upload.plist \
  -exportPath build/export -allowProvisioningUpdates | tail -5
rm -rf www
echo "✓ Subido. En 10-20 min aparece en App Store Connect → TestFlight."
