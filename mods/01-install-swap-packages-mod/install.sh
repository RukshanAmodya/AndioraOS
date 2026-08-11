#!/bin/bash
set -e                  # exit on error
set -o pipefail         # exit on pipeline error
set -u                  # treat unset variable as error
#==========================
# Install Andiora swap packages
#==========================

print_ok "Installing Andiora APT configuration and keyring packages..."
apt install -y \
    "$APT_CONFIG_PACKAGE" \
    andiora-archive-keyring \
    base-files
judge "Install Andiora basic packages"

