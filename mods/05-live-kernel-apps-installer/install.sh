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

print_ok "Installing anduinos-desktop (full AnduinOS desktop metapackage)..."
# DKMS legitimately needs gcc/make/dpkg-dev, but dpkg-dev only recommends the
# unrelated build-essential C++ stack. Keep that soft dependency out of the ISO.
apt install -y \
    anduinos-desktop \
    anduinos-desktop-apps \
    anduinos-gnome-extensions \
    anduinos-appstore \
    anduinos-theme \
    anduinos-wallpapers \
    anduinos-fonts \
    anduinos-no-snapd \
    anduinos-session \
    anduinos-software-properties-common \
    anduinos-system-tweaks \
    firefox-anduinos \
    gnome-shell-extension-appindicator-anduinos \
    gnome-shell-extension-dash-to-panel-anduinos \
    gnome-shell-extension-desktop-icons-ng-anduinos \
    plymouth \
    alsa-ucm-conf-anduinos \
    firmware-sof-anduinos \
    initramfs-tools \
    build-essential- \
    --install-recommends
judge "Install anduinos-desktop"

print_ok "Attempting to install optional plymouth-andiora branding..."
apt install -y plymouth-andiora --no-install-recommends || \
apt install -y plymouth-anduinos --no-install-recommends || \
dpkg -i /andiora_local_repo/plymouth-andiora*.deb 2>/dev/null || \
print_warn "plymouth-andiora package not found, using stock plymouth."

print_ok "Installing local Andiora branding overrides (dconf-defaults & oobe)..."
apt install -y andiora-dconf-defaults andiora-oobe --no-install-recommends || \
apt install -y anduinos-dconf-defaults anduinos-oobe --no-install-recommends || \
(dpkg -i /andiora_local_repo/andiora-dconf-defaults*.deb /andiora_local_repo/andiora-oobe*.deb 2>/dev/null) || \
print_warn "Local Andiora branding packages not found."

print_ok "Installing Andiora native installer..."
apt install -y andiora-installer-beta --no-install-recommends || \
apt install -y anduinos-installer-beta --no-install-recommends || \
apt install -y anduinos-installer-config --no-install-recommends || \
print_warn "Neither andiora-installer-beta nor anduinos-installer-beta found."
judge "Install Andiora installer"

# Carry the Btrfs recovery UI inside the ISO without making it a desktop
# metapackage dependency. The native installer retains this package for Btrfs
# targets and purges it from ext4 targets through its explicit cleanup policy.
#print_ok "Installing conditional Disk Snapshots Manager payload..."
# apt install -y andiora-btrfs-snapshots-manager \
#    --no-install-recommends
# judge "Install andiora-btrfs-snapshots-manager payload"
