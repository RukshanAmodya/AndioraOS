#!/usr/bin/env bash
# Pre-build: downloads Desktop Icons NG (DING) for each supported suite,
# then applies Andiora customizations.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/gnome-versions.sh"

UUID="ding@rastersoft.com"

# ── Localization table ──────────────────────────────────────────────────

declare -A DING_APPEARANCE=(
    ["ar"]="إعدادات مظهر Andiora"
    ["be"]="Налады вонкавага выгляду Andiora"
    ["ca"]="Paràmetres de l'aparença d'Andiora"
    ["cs"]="Nastavení vzhledu Andiora"
    ["da"]="Indstillinger for Andiora-udseende"
    ["de"]="Andiora-Aussehens-Einstellungen"
    ["es"]="Preferencias de la apariencia de Andiora"
    ["fi"]="Andiora-ulkonäön asetukset"
    ["fr"]="Préférences de l'apparence d'Andiora"
    ["fur"]="Andiora Appearance Settings"
    ["he"]="הגדרות המראה של Andiora"
    ["hr"]="Andiora Appearance Settings"
    ["hu"]="Andiora Appearance Settings"
    ["id"]="Pengaturan Tampilan Andiora"
    ["it"]="Impostazioni dell'aspetto di Andiora"
    ["ja"]="Andiora の外観の設定"
    ["ka"]="Andiora-ის გარეგნობის პარამეტრები"
    ["ko"]="Andiora 외관 설정"
    ["nl"]="Andiora-uiterlijk-instellingen"
    ["oc"]="Paramètres de l'aparéncia d'Andiora"
    ["pl"]="Ustawienia wyglądu Andiora"
    ["pt_BR"]="Configurações da Aparência do Andiora"
    ["ro"]="Setările aspectului Andiora"
    ["ru"]="Параметры внешнего вида Andiora"
    ["sk"]="Nastavenia vzhľadu Andiora"
    ["sv"]="Inställningar för Andiora-utseende"
    ["tr"]="Andiora Görünümü Ayarları"
    ["uk"]="Налаштування оформлення Andiora"
    ["zh_CN"]="Andiora 外观设置"
    ["zh_TW"]="Andiora 外觀設定"
)

for SUITE in "${!GNOME_TARGETS[@]}"; do
    TARGET=${GNOME_TARGETS[$SUITE]}
    DEPLOY_DIR="deploy/$SUITE/$UUID"

    rm -rf "$DEPLOY_DIR"
    mkdir -p "$DEPLOY_DIR"

    echo "[$SUITE] Resolving $UUID for GNOME $TARGET..."
    python3 "$SCRIPT_DIR/../lib/resolve-gnome-ext.py" "$UUID" --target "$TARGET" --download --out "$DEPLOY_DIR"

    # ── Andiora customizations ───────────────────────────────────────────
    echo "[$SUITE] Patching desktopManager.js: Desktop Icons Settings → Andiora Appearance Settings"

    sed -i "s/label: _('Desktop Icons Settings')/label: _('Andiora Appearance Settings')/" \
        "$DEPLOY_DIR/app/desktopManager.js"

    sed -i 's/this._settingsMenuItem.connect("activate", () => Prefs.showPreferences());/this._settingsMenuItem.connect("activate", () => { GLib.spawn_command_line_async('\''andiora-appearance'\''); });/' \
        "$DEPLOY_DIR/app/desktopManager.js"

    echo "[$SUITE] JS patch applied successfully."

    # ── DING v84 spawns ding.js as a child process, needs +x ──────────
    chmod +x "$DEPLOY_DIR/app/ding.js"

    # ── Inject "Andiora Appearance Settings" into ding.mo ────────────────
    locale_dir="$DEPLOY_DIR/locale"
    found=0

    if [[ -d "$locale_dir" ]]; then
        for lang_dir in "$locale_dir"/*/; do
            lang=$(basename "$lang_dir")
            mo_file="$lang_dir/LC_MESSAGES/ding.mo"

            if [[ -f "$mo_file" ]] && [[ -n "${DING_APPEARANCE[$lang]+isset}" ]]; then
                echo "[$SUITE] Patching ding.mo locale: $lang"
                msgunfmt "$mo_file" -o /tmp/ding.po

                cat << EOF >> /tmp/ding.po
msgid "Andiora Appearance Settings"
msgstr "${DING_APPEARANCE[$lang]}"

EOF
                msgfmt /tmp/ding.po -o "$mo_file"
                rm -f /tmp/ding.po
                found=$((found + 1))
            fi
        done
        echo "[$SUITE] Patched ding.mo for $found languages"
    fi
done

echo "Done."

# Pre-compile GSettings schemas at build time so postinst is unnecessary
for suite_dir in deploy/*/; do
    schema_dir="${suite_dir}ding@rastersoft.com/schemas"
    [ -d "$schema_dir" ] && glib-compile-schemas "$schema_dir" || true
done
