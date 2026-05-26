#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <EIDOS_FOUNDERS_RECORDINGS_FOLDER_ID>" >&2
  exit 2
fi

DEST_FOLDER_ID="$1"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${TMPDIR:-/tmp}/eidos-meeting2action"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx is required to install @google/clasp" >&2
  exit 1
fi

ACCOUNT="$(npx -y @google/clasp show-authorized-user 2>/dev/null | awk '/logged in as|Logged in as/ {sub("\\.$", "", $NF); print $NF; exit}')"
if [[ -z "${ACCOUNT}" ]]; then
  echo "clasp is not logged in. Run: npx -y @google/clasp login" >&2
  exit 1
fi

if [[ "${ACCOUNT}" != *@eidosagi.com ]]; then
  echo "refusing to install with non-Eidos Google account: ${ACCOUNT}" >&2
  exit 1
fi

rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}"
sed "s/__EIDOS_FOUNDERS_RECORDINGS_FOLDER_ID__/${DEST_FOLDER_ID}/g" \
  "${PLUGIN_DIR}/scripts/apps-script/Code.js" > "${WORK_DIR}/Code.js"
cp "${PLUGIN_DIR}/scripts/apps-script/appsscript.json" "${WORK_DIR}/appsscript.json"

cd "${WORK_DIR}"
npx -y @google/clasp create --type standalone --title "Eidos Meeting2Action"
npx -y @google/clasp push --force

SCRIPT_ID="$(awk -F'"' '/scriptId/ {print $4}' .clasp.json)"
echo "Script created: ${SCRIPT_ID}"
echo "Apps Script URL: https://script.google.com/d/${SCRIPT_ID}/edit"
echo "Next: open the URL, run installTimeTrigger once, approve scopes, then run syncMeetRecordings for a smoke test."
