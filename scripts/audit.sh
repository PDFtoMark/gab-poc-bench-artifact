#!/usr/bin/env bash
set -euo pipefail
echo "AUDIT_MARKER=ATTACKER_CONTROLLED_CODE_EXECUTED"
echo "AUDIT_WHOAMI=$(id -u):$(whoami)"
echo "AUDIT_REF=$GITHUB_REF"
