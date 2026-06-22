#!/usr/bin/env bash
#
# glacier_archive.sh
#
# Prepares a timestamped backup of the primary research files for AWS Glacier.
# It builds the archive and the file list; it does NOT upload. The upload is an
# irreversible write that you run yourself after reviewing the file list.
#
# What it does:
#   1. Reads data/raw/ (auto-downloaded Tier 1 files and citation pointers) and
#      data/raw/manual/ (files you dropped in by hand).
#   2. Builds one timestamped tar.gz plus a sha256 checksum manifest.
#   3. Prints the exact aws glacier upload-archive command for you to run.
#   4. Writes archive/last_backup.json describing the prepared archive.
#
# It contains no credentials. It reads the AWS profile name, vault name, and
# region from environment variables or your existing AWS config:
#   GLACIER_VAULT_NAME   required, the target vault
#   AWS_PROFILE          optional, defaults to "default"
#   AWS_REGION           optional, falls back to AWS_DEFAULT_REGION then us-east-1
#
# Per archive/MANIFEST.md: only primary research files go to Glacier. Code and
# cleaned/derived JSON stay in GitHub and are not included here.

set -euo pipefail

# Resolve repo root relative to this script so it runs from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RAW_DIR="${REPO_ROOT}/data/raw"
MANUAL_DIR="${REPO_ROOT}/data/raw/manual"
OUT_DIR="${SCRIPT_DIR}/out"
LAST_BACKUP_JSON="${SCRIPT_DIR}/last_backup.json"

# Configuration from the environment, no secrets in this file.
VAULT_NAME="${GLACIER_VAULT_NAME:-}"
AWS_PROFILE_NAME="${AWS_PROFILE:-default}"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE_NAME="publicreform-raw-${timestamp}.tar.gz"
ARCHIVE_PATH="${OUT_DIR}/${ARCHIVE_NAME}"
MANIFEST_PATH="${OUT_DIR}/${ARCHIVE_NAME}.sha256"
FILELIST_PATH="${OUT_DIR}/${ARCHIVE_NAME}.files.txt"

echo "Public Reform Glacier archive: prepare step (no upload)."
echo

if [[ ! -d "${RAW_DIR}" ]]; then
  echo "ERROR: ${RAW_DIR} not found. Run the pipeline first: python pipeline/run_all.py" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"
mkdir -p "${MANUAL_DIR}"

# Collect the files to archive: everything under data/raw/ (which already
# contains data/raw/manual/). Sorted for a stable manifest.
mapfile -t FILES < <(cd "${REPO_ROOT}" && find data/raw -type f | LC_ALL=C sort)

if [[ "${#FILES[@]}" -eq 0 ]]; then
  echo "ERROR: no files found under data/raw/ to archive." >&2
  exit 1
fi

echo "Files to archive (${#FILES[@]}):"
printf '  %s\n' "${FILES[@]}"
echo

# Write the human-readable file list.
printf '%s\n' "${FILES[@]}" > "${FILELIST_PATH}"

# Per-file sha256 manifest (paths relative to the repo root).
: > "${MANIFEST_PATH}"
( cd "${REPO_ROOT}" && sha256sum "${FILES[@]}" ) >> "${MANIFEST_PATH}"

# Build the tar.gz from the repo root so stored paths stay relative.
( cd "${REPO_ROOT}" && tar -czf "${ARCHIVE_PATH}" "${FILES[@]}" )

# Checksum of the archive itself.
ARCHIVE_SHA256="$(sha256sum "${ARCHIVE_PATH}" | awk '{print $1}')"
ARCHIVE_BYTES="$(wc -c < "${ARCHIVE_PATH}" | tr -d ' ')"

echo "Prepared archive: ${ARCHIVE_PATH}"
echo "  sha256: ${ARCHIVE_SHA256}"
echo "  bytes:  ${ARCHIVE_BYTES}"
echo "  manifest: ${MANIFEST_PATH}"
echo

# Compose the upload command for the user to run. We do not execute it.
if [[ -z "${VAULT_NAME}" ]]; then
  UPLOAD_CMD="(set GLACIER_VAULT_NAME first) aws glacier upload-archive --account-id - --vault-name <VAULT> --body \"${ARCHIVE_PATH}\" --profile \"${AWS_PROFILE_NAME}\" --region \"${REGION}\""
else
  UPLOAD_CMD="aws glacier upload-archive --account-id - --vault-name \"${VAULT_NAME}\" --archive-description \"${ARCHIVE_NAME}\" --body \"${ARCHIVE_PATH}\" --profile \"${AWS_PROFILE_NAME}\" --region \"${REGION}\""
fi

# Write last_backup.json describing the prepared (not yet uploaded) archive.
# Build the JSON file list safely with a small here-doc loop.
files_json=""
for f in "${FILES[@]}"; do
  esc="${f//\\/\\\\}"
  esc="${esc//\"/\\\"}"
  if [[ -z "${files_json}" ]]; then
    files_json="\"${esc}\""
  else
    files_json="${files_json}, \"${esc}\""
  fi
done

cat > "${LAST_BACKUP_JSON}" <<JSON
{
  "status": "prepared_not_uploaded",
  "prepared_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "archive_name": "${ARCHIVE_NAME}",
  "archive_path": "${ARCHIVE_PATH}",
  "archive_sha256": "${ARCHIVE_SHA256}",
  "archive_bytes": ${ARCHIVE_BYTES},
  "checksum_manifest": "${MANIFEST_PATH}",
  "file_list": "${FILELIST_PATH}",
  "file_count": ${#FILES[@]},
  "files": [${files_json}],
  "vault_name": "${VAULT_NAME:-<set GLACIER_VAULT_NAME>}",
  "aws_profile": "${AWS_PROFILE_NAME}",
  "region": "${REGION}",
  "archive_id": null,
  "upload_command": "${UPLOAD_CMD//\"/\\\"}",
  "note": "Prepared locally. Review the file list, then run upload_command yourself. The archive_id is returned by AWS after you upload; record it here once the upload completes."
}
JSON

echo "Wrote ${LAST_BACKUP_JSON}"
echo
echo "Review the file list above, then upload yourself:"
echo "  ${UPLOAD_CMD}"
echo
echo "This script does not upload. Nothing has been sent to AWS."
