#!/bin/sh
# Checks the locked packages against the published advisories with pip-audit
# (pip install pip-audit==2.9.0). Advisories that do not apply to Speakr are
# listed in scripts/audit-exceptions.txt with a review date and a reason; an
# exception past its review date no longer applies, so the advisory fails the
# check again until it is looked at.
#
#   scripts/audit-dependencies.sh
set -eu
cd "$(dirname "$0")/.."

today=$(date -u +%Y-%m-%d)
ignores=""
while read -r id until reason; do
    case "$id" in ''|'#'*) continue ;; esac
    first=$(printf '%s\n%s\n' "$today" "$until" | sort | head -n 1)
    if [ "$until" = never ] || [ "$first" = "$today" ]; then
        ignores="$ignores --ignore-vuln $id"
    else
        echo "Exception for $id expired on $until ($reason)" >&2
    fi
done < scripts/audit-exceptions.txt

status=0
for lock in requirements.lock requirements-embeddings.lock; do
    echo "== $lock"
    # Local versions such as torch==2.14.1+cpu are not on PyPI, so pip-audit
    # would skip them. Audit the base version instead; advisories apply to the
    # CPU wheel as well.
    audit_lock=$lock
    tmp_lock=
    if grep -q '+cpu' "$lock"; then
        tmp_lock=$(mktemp)
        sed 's/^\(torch==[0-9][^+ ]*\)+cpu/\1/' "$lock" > "$tmp_lock"
        audit_lock=$tmp_lock
    fi
    # shellcheck disable=SC2086
    pip-audit --disable-pip --require-hashes --progress-spinner off -r "$audit_lock" $ignores || status=1
    [ -z "$tmp_lock" ] || rm -f "$tmp_lock"
done
exit $status
