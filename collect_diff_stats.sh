#!/usr/bin/env bash
# collect_diff_stats.sh
#
# Usage: ./collect_diff_stats.sh
#
# For each entry in docs/sem_ppt_plan/slides.json that has a non-empty
# "hash", this script runs `git show --stat` and injects the "<files>, +xx / -yy"
# LOC summary back into the "stat" field.
#
# Requirements:
#  - Run from repository root.
#  - Uses jq to update slides.json in-place with indent=2.
#  - Skips hashes not in local history and prints a warning.

set -euo pipefail

JSON_PATH="docs/sem_ppt_plan/slides.json"

if [[ ! -f "$JSON_PATH" ]]; then
  echo "Error: $JSON_PATH not found" >&2
  exit 1
fi

length=$(jq 'length' "$JSON_PATH")

for ((i=0; i<length; i++)); do
  hash=$(jq -r ".[$i].hash" "$JSON_PATH")
  if [[ -z "$hash" || "$hash" == "null" ]]; then
    continue
  fi

  if ! git cat-file -e "${hash}^{commit}" 2>/dev/null; then
    echo "Warning: commit $hash not found" >&2
    continue
  fi

  stat_line=$(git show --stat --pretty="" "$hash" | tail -n1)
  files=$(echo "$stat_line" | sed -nE 's/^[[:space:]]*([0-9]+) file(s?) changed.*$/\1/p')
  insert=$(echo "$stat_line" | grep -oE '[0-9]+ insertions?\(\+\)' | grep -oE '[0-9]+' || echo 0)
  delete=$(echo "$stat_line" | grep -oE '[0-9]+ deletions?\(-\)' | grep -oE '[0-9]+' || echo 0)

  if [[ -z "$files" ]]; then
    echo "Warning: could not parse stats for $hash" >&2
    continue
  fi

  if [[ "$files" -eq 1 ]]; then
    file_desc="1 file"
  else
    file_desc="$files files"
  fi

  newstat="$file_desc, +$insert / -$delete"

  jq --indent 2 --arg v "$newstat" ".[$i].stat = \$v" "$JSON_PATH" > "$JSON_PATH.tmp" && mv "$JSON_PATH.tmp" "$JSON_PATH"

done

# final pass to ensure consistent formatting
jq --indent 2 '.' "$JSON_PATH" > "$JSON_PATH.tmp" && mv "$JSON_PATH.tmp" "$JSON_PATH"

echo "Updated $JSON_PATH"
