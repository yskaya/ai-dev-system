#!/usr/bin/env bash
# Install ai-dev-system into a project from a GitHub release (or main branch fallback).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/OWNER/ai-dev-system/main/scripts/install-remote.sh | bash
#   curl -fsSL ... | bash -s -- /path/to/project
#   curl -fsSL ... | bash -s -- --cursor-only .
#
# Environment:
#   AI_DEV_SYSTEM_REPO      GitHub repo (default: yskaya/ai-dev-system)
#   AI_DEV_SYSTEM_VERSION   Release tag, e.g. v1.0.0 (default: latest release, else main)
#   AI_DEV_SYSTEM_REF        Branch for source fallback (default: main)
#   AI_DEV_SYSTEM_TARBALL    Local path to dist tarball (skips download; for testing)
set -euo pipefail

DEFAULT_REPO="yskaya/ai-dev-system"
REPO="${AI_DEV_SYSTEM_REPO:-$DEFAULT_REPO}"
VERSION="${AI_DEV_SYSTEM_VERSION:-}"
REF="${AI_DEV_SYSTEM_REF:-main}"
TARBALL="${AI_DEV_SYSTEM_TARBALL:-}"
ASSET_NAME="ai-dev-system-dist.tar.gz"

PROJECT_DIR="."
CURSOR_ONLY=0
CLAUDE_ONLY=0

usage() {
  cat <<EOF
Usage: install-remote.sh [OPTIONS] [PROJECT_DIR]

Install ai-dev-system into PROJECT_DIR (default: current directory).

Options:
  --cursor-only   Install Cursor artifacts only (.cursor/)
  --claude-only   Install Claude artifacts only (.claude/)
  -h, --help      Show this help

Environment:
  AI_DEV_SYSTEM_REPO      GitHub repo (default: $DEFAULT_REPO)
  AI_DEV_SYSTEM_VERSION   Release tag (default: latest release, else branch $REF)
  AI_DEV_SYSTEM_REF       Branch for source fallback (default: main)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor-only)
      CURSOR_ONLY=1
      shift
      ;;
    --claude-only)
      CLAUDE_ONLY=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    -*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      PROJECT_DIR="$1"
      shift
      ;;
  esac
done

if [[ "$CURSOR_ONLY" -eq 1 && "$CLAUDE_ONLY" -eq 1 ]]; then
  echo "use only one of --cursor-only or --claude-only" >&2
  exit 1
fi

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "required command not found: $1" >&2
    exit 1
  fi
}

need_cmd curl
need_cmd tar
need_cmd mktemp

WORKDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

copy_tree() {
  local src="$1"
  local dest="$2"
  if [[ ! -d "$src" ]]; then
    echo "missing artifact directory: $src" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$src" "$dest"
}

install_target() {
  local platform="$1"
  local prefix="$2"
  local root="$WORKDIR/extract"
  local label

  case "$platform" in
    cursor) label="Cursor (.cursor/)" ;;
    claude) label="Claude (.claude/)" ;;
    *) echo "unknown platform: $platform" >&2; exit 1 ;;
  esac

  echo "$label"
  copy_tree "$root/$platform/rules" "$PROJECT_DIR/$prefix/rules"
  echo "  $prefix/rules"
  copy_tree "$root/$platform/commands" "$PROJECT_DIR/$prefix/commands"
  echo "  $prefix/commands"
  copy_tree "$root/$platform/skills" "$PROJECT_DIR/$prefix/skills"
  echo "  $prefix/skills"
  copy_tree "$root/$platform/schemas" "$PROJECT_DIR/$prefix/schemas"
  echo "  $prefix/schemas"
}

download_release_asset() {
  local tag="$1"
  local url="https://github.com/${REPO}/releases/download/${tag}/${ASSET_NAME}"
  if curl -fsSL "$url" -o "$WORKDIR/dist.tar.gz"; then
    return 0
  fi
  return 1
}

resolve_latest_tag() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
    | head -n 1
}

download_from_source() {
  local branch="$1"
  local archive_url="https://github.com/${REPO}/archive/refs/heads/${branch}.tar.gz"
  echo "Downloading source archive (${branch})..."
  curl -fsSL "$archive_url" -o "$WORKDIR/source.tar.gz"
  tar -xzf "$WORKDIR/source.tar.gz" -C "$WORKDIR"
  local extracted
  extracted="$(find "$WORKDIR" -maxdepth 1 -mindepth 1 -type d ! -name extract | head -n 1)"
  if [[ ! -d "$extracted/dist/cursor" || ! -d "$extracted/dist/claude" ]]; then
    echo "source archive missing dist/ (repo may need a release build)" >&2
    exit 1
  fi
  mkdir -p "$WORKDIR/extract"
  cp -R "$extracted/dist/cursor" "$extracted/dist/claude" "$WORKDIR/extract/"
}

fetch_artifacts() {
  if [[ -n "$TARBALL" ]]; then
    if [[ ! -f "$TARBALL" ]]; then
      echo "tarball not found: $TARBALL" >&2
      exit 1
    fi
    echo "Using local tarball: $TARBALL"
    cp "$TARBALL" "$WORKDIR/dist.tar.gz"
    tar -xzf "$WORKDIR/dist.tar.gz" -C "$WORKDIR"
    mkdir -p "$WORKDIR/extract"
    mv "$WORKDIR/cursor" "$WORKDIR/claude" "$WORKDIR/extract/"
    [[ -f "$WORKDIR/VERSION" ]] && mv "$WORKDIR/VERSION" "$WORKDIR/extract/VERSION"
    return
  fi

  local tag=""

  if [[ -n "$VERSION" ]]; then
    tag="$VERSION"
    echo "Fetching release ${tag} from ${REPO}..."
    if download_release_asset "$tag"; then
      tar -xzf "$WORKDIR/dist.tar.gz" -C "$WORKDIR"
      mkdir -p "$WORKDIR/extract"
      mv "$WORKDIR/cursor" "$WORKDIR/claude" "$WORKDIR/extract/"
      [[ -f "$WORKDIR/VERSION" ]] && mv "$WORKDIR/VERSION" "$WORKDIR/extract/VERSION"
      return
    fi
    echo "release asset not found for ${tag}; trying source fallback..." >&2
    download_from_source "$REF"
    return
  fi

  tag="$(resolve_latest_tag || true)"
  if [[ -n "$tag" ]]; then
    echo "Fetching latest release ${tag} from ${REPO}..."
    if download_release_asset "$tag"; then
      tar -xzf "$WORKDIR/dist.tar.gz" -C "$WORKDIR"
      mkdir -p "$WORKDIR/extract"
      mv "$WORKDIR/cursor" "$WORKDIR/claude" "$WORKDIR/extract/"
      [[ -f "$WORKDIR/VERSION" ]] && mv "$WORKDIR/VERSION" "$WORKDIR/extract/VERSION"
      return
    fi
    echo "latest release has no ${ASSET_NAME}; trying source fallback..." >&2
  else
    echo "No GitHub release found; using ${REPO}@${REF} source archive..."
  fi

  download_from_source "$REF"
}

fetch_artifacts

INSTALLED_VERSION=""
if [[ -f "$WORKDIR/extract/VERSION" ]]; then
  INSTALLED_VERSION="$(tr -d '\n' < "$WORKDIR/extract/VERSION")"
fi

echo "Installing into ${PROJECT_DIR}"
if [[ -n "$INSTALLED_VERSION" ]]; then
  echo "Version: ${INSTALLED_VERSION}"
fi
echo

DO_CURSOR=1
DO_CLAUDE=1
[[ "$CLAUDE_ONLY" -eq 1 ]] && DO_CURSOR=0
[[ "$CURSOR_ONLY" -eq 1 ]] && DO_CLAUDE=0

if [[ "$DO_CURSOR" -eq 1 ]]; then
  install_target cursor ".cursor"
fi
if [[ "$DO_CLAUDE" -eq 1 ]]; then
  [[ "$DO_CURSOR" -eq 1 ]] && echo
  install_target claude ".claude"
fi

echo
echo "Done. See https://github.com/${REPO}/blob/main/GUIDE.md for usage."
