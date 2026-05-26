#!/usr/bin/env bash
set -euo pipefail

ACCOUNT="$(npx -y @google/clasp show-authorized-user 2>/dev/null | awk '/logged in as|Logged in as/ {sub("\\.$", "", $NF); print $NF; exit}')"
if [[ -z "${ACCOUNT}" ]]; then
  echo "clasp: not logged in"
else
  echo "clasp: logged in as ${ACCOUNT}"
fi

if [[ -f "${TMPDIR:-/tmp}/eidos-meeting2action/.clasp.json" ]]; then
  SCRIPT_ID="$(awk -F'"' '/scriptId/ {print $4}' "${TMPDIR:-/tmp}/eidos-meeting2action/.clasp.json")"
  echo "last script: https://script.google.com/d/${SCRIPT_ID}/edit"
else
  echo "last script: none recorded in temp workspace"
fi
