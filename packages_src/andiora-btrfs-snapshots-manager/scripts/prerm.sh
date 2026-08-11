set -eu

case "${1:-}" in
    remove|deconfigure)
        # Disable while the unit file still exists. Doing this from postrm
        # produces a misleading "unit does not exist" warning after dpkg has
        # already removed the package payload.
        systemctl disable --now andiora-btrfs-snapshots-manager-confirm.service >/dev/null 2>&1 || true
        systemctl disable --now andiora-btrfs-snapshots-manager-scheduler.timer >/dev/null 2>&1 || true
        ;;
esac

systemctl stop andiora-btrfs-snapshots-manager-scheduler.service >/dev/null 2>&1 || true
systemctl stop andiora-btrfs-snapshots-manager-helper.service >/dev/null 2>&1 || true
