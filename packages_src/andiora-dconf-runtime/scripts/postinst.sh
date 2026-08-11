#!/bin/sh
set -e

# andiora-dconf-runtime owns the dpkg trigger for /etc/dconf/db/andiora.d.
# This postinst is invoked by dpkg:
#   - with "$1" = "triggered" when ANY package installs/removes files
#     under /etc/dconf/db/andiora.d/ during an apt transaction;
#   - with "$1" = "configure" when this package itself is installed/upgraded.
#
# In both cases we rebuild the andiora system database. On live systems we use
# `dconf update` to emit change notifications. In chroots we compile the
# andiora database directly to avoid leaking D-Bus signals into the host.

is_chroot() {
    if command -v systemd-detect-virt >/dev/null 2>&1 &&
       systemd-detect-virt --quiet --chroot >/dev/null 2>&1; then
        return 0
    fi

    if command -v ischroot >/dev/null 2>&1 && ischroot >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

rebuild_andiora_db() {
    db_dir=/etc/dconf/db/andiora.d
    db_file=/etc/dconf/db/andiora

    if ! command -v dconf >/dev/null 2>&1; then
        return 0
    fi

    if is_chroot; then
        echo "andiora-dconf-runtime: chroot detected; compiling /etc/dconf/db/andiora directly to avoid host D-Bus notifications."
        if [ -d "$db_dir" ]; then
            dconf compile "$db_file" "$db_dir"
        else
            rm -f "$db_file"
        fi
    else
        dconf update
    fi
}

case "$1" in
    triggered|configure)
        rebuild_andiora_db
        ;;
esac
