#!/bin/sh
set -e

if [ "$1" = "configure" ]; then
    # 1. Register and set graphical splash theme
    update-alternatives --install \
        /usr/share/plymouth/themes/default.plymouth \
        default.plymouth \
        /usr/share/plymouth/themes/andiora/andiora.plymouth \
        150
    update-alternatives --set \
        default.plymouth \
        /usr/share/plymouth/themes/andiora/andiora.plymouth || true

    # 2. Register and set text fallback theme
    update-alternatives --install \
        /usr/share/plymouth/themes/text.plymouth \
        text.plymouth \
        /usr/share/plymouth/themes/andiora-text/andiora-text.plymouth \
        150
    update-alternatives --set \
        text.plymouth \
        /usr/share/plymouth/themes/andiora-text/andiora-text.plymouth || true

    # 3. Rebuild initramfs (dual-track with regenerate-all for dracut)
    if command -v dracut >/dev/null 2>&1; then
        dracut --force --regenerate-all 2>/dev/null || true
    elif command -v update-initramfs >/dev/null 2>&1; then
        update-initramfs -u 2>/dev/null || true
    fi
fi
