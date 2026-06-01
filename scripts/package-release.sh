#!/usr/bin/env bash
# Package dist/cursor and dist/claude into a release tarball.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
OUT="${1:-$ROOT/ai-dev-system-dist.tar.gz}"
STAGING="$(mktemp -d)"

cleanup() {
  rm -rf "$STAGING"
}
trap cleanup EXIT

for target in cursor claude; do
  if [[ ! -d "$DIST/$target" ]]; then
    echo "missing build output: $DIST/$target (run: python3 scripts/build.py)" >&2
    exit 1
  fi
done

VERSION="${AI_DEV_SYSTEM_VERSION:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(git -C "$ROOT" describe --tags --always 2>/dev/null || echo dev)"
fi

cp -R "$DIST/cursor" "$DIST/claude" "$STAGING/"
printf '%s\n' "$VERSION" > "$STAGING/VERSION"

tar -czf "$OUT" -C "$STAGING" cursor claude VERSION
echo "Created $OUT (version: $VERSION)"
