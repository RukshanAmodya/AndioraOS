#!/bin/bash

set -e                  # exit on error
set -o pipefail         # exit on pipeline error
set -u                  # treat unset variable as error

wait_network

print_ok "Installing Casper (live boot)..."
apt install -y \
    casper \
    linux-image-generic \
    linux-headers-generic \
    zstd \
    discover \
    laptop-detect \
    os-prober \
    keyutils \
    --no-install-recommends
judge "Install live-boot"

print_ok "Updating apt package list..."
apt update || true

print_ok "Installing andiora-desktop (full Andiora desktop metapackage)..."
# DKMS legitimately needs gcc/make/dpkg-dev, but dpkg-dev only recommends the
# unrelated build-essential C++ stack. Keep that soft dependency out of the ISO.
apt install -y \
    andiora-desktop \
    andiora-desktop-apps \
    andiora-gnome-extensions \
    andiora-appstore \
    andiora-theme \
    andiora-wallpapers \
    andiora-fonts \
    andiora-no-snapd \
    andiora-session \
    andiora-software-properties-common \
    andiora-system-tweaks \
    firefox-andiora \
    gnome-shell-extension-appindicator-andiora \
    gnome-shell-extension-dash-to-panel-andiora \
    gnome-shell-extension-desktop-icons-ng-andiora \
    plymouth \
    alsa-ucm-conf-andiora \
    firmware-sof-andiora \
    initramfs-tools \
    build-essential- \
    --install-recommends
judge "Install andiora-desktop"

print_ok "Attempting to install optional plymouth-andiora branding..."
apt install -y plymouth-andiora --no-install-recommends || print_warn "plymouth-andiora package not found, using stock plymouth."

print_ok "Installing Andiora native installer..."
apt install -y andiora-installer-beta --no-install-recommends || \
apt install -y andiora-installer-config --no-install-recommends || \
print_warn "Neither andiora-installer-beta nor andiora-installer-config found."
judge "Install Andiora installer"

# Carry the Btrfs recovery UI inside the ISO without making it a desktop
# metapackage dependency. The native installer retains this package for Btrfs
# targets and purges it from ext4 targets through its explicit cleanup policy.
#print_ok "Installing conditional Disk Snapshots Manager payload..."
# apt install -y andiora-btrfs-snapshots-manager \
#    --no-install-recommends
# judge "Install andiora-btrfs-snapshots-manager payload"
