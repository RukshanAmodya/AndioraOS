#!/bin/bash
set -e
set -o pipefail
set -u

print_ok "Updating initramfs for LIVE ISO..."

# =========================================================
# LIVE ISO BUILD SPECIFIC LOGIC
# We MUST use initramfs-tools here because Dracut cannot
# boot an Ubuntu 'casper' Live ISO natively.
# =========================================================

if command -v update-initramfs >/dev/null 2>&1; then
    print_ok "Using initramfs-tools to ensure 'casper' live-boot capability..."
    update-initramfs -u -k all
else
    print_error "ERROR: initramfs-tools is missing! Casper live boot will fail."
    exit 1
fi

judge "Update initramfs"
