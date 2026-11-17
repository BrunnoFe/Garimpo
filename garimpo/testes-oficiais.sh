#!/bin/bash
# Roda os testes da loja oficial do Runtipi (apps/__tests__ + bun) sobre uma loja convertida.
# Uso: bash garimpo/testes-oficiais.sh <pasta da loja oficial clonada> <pasta da loja convertida>
set -euo pipefail
oficial=$1
loja=$2
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$oficial"/. "$tmp"/
rm -rf "$tmp/.git"
find "$tmp/apps" -mindepth 1 -maxdepth 1 ! -name __tests__ -exec rm -rf {} +
cp -r "$loja/apps"/. "$tmp/apps"/
cd "$tmp"
bun install --frozen-lockfile --ignore-scripts >/dev/null  # sem o gancho de git da loja oficial
bun test apps/__tests__ 2>&1 | tail -n 15
