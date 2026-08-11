#!/usr/bin/env python3
"""
Patch AnduinOS .deb packages to replace 'AnduinOS' branding with 'Andiora'.
Packages patched:
  1. anduinos-oobe         - Welcome screen text
  2. plymouth-anduinos     - Boot screen watermark + config files
  3. anduinos-dconf-defaults - Login screen logo + dconf text

Usage:
    python patch_debs.py
"""

import io
import os
import struct
import tarfile
import zstandard

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Watermark logo (300x61 RGBA PNG) ────────────────────────────────────────
ANDIORA_LOGO_PATH = os.path.join(SCRIPT_DIR, "andiora_watermark.png")

# ── Replacements ─────────────────────────────────────────────────────────────
TEXT_REPLACEMENTS = [
    (b"AnduinOS", b"Andiora "),   # keep same byte length (8 bytes each)
    (b"ANDUINOS", b"ANDIORA "),
    (b"anduinos", b"andiora "),   # careful — only in branding text, not paths/package names
]

# For text files (config / .desktop / .py), do clean string replacement
STR_REPLACEMENTS = [
    ("AnduinOS", "Andiora"),
    ("ANDUINOS", "ANDIORA"),
]

# Binary files where we do safe same-length byte replacement (e.g., .mo gettext files)
BINARY_REPLACEMENTS = [
    (b"AnduinOS", b"Andiora "),  # 8 bytes → 8 bytes (trailing space trimmed by gettext)
    (b"ANDUINOS", b"ANDIORA "),
]


# ─────────────────────────────────────────────────────────────────────────────
# AR (.deb) parser / builder
# ─────────────────────────────────────────────────────────────────────────────

def parse_ar(data: bytes) -> list[tuple[str, bytes]]:
    """Return list of (filename, content) from an AR archive."""
    assert data[:8] == b"!<arch>\n", "Not a valid AR archive"
    members = []
    pos = 8
    while pos < len(data):
        if pos + 60 > len(data):
            break
        hdr = data[pos:pos + 60]
        filename = hdr[0:16].decode("ascii").rstrip("/ ")
        size = int(hdr[48:58].decode("ascii").strip())
        content = data[pos + 60: pos + 60 + size]
        members.append((filename, content))
        pos += 60 + size + (size % 2)  # 2-byte alignment
    return members


def build_ar(members: list[tuple[str, bytes]]) -> bytes:
    """Build an AR archive from list of (filename, content) tuples."""
    out = bytearray(b"!<arch>\n")
    for filename, content in members:
        size = len(content)
        # 16-char filename padded with spaces, then standard AR header fields
        hdr = f"{filename:<16}{'0':<12}{'0':<6}{'0':<6}{'100644':<8}{size:<10}`\n"
        out += hdr.encode("ascii")
        out += content
        if size % 2 == 1:
            out += b"\n"  # padding
    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────────
# ZST tar helpers
# ─────────────────────────────────────────────────────────────────────────────

def decompress_zst(data: bytes) -> bytes:
    dctx = zstandard.ZstdDecompressor()
    return dctx.stream_reader(io.BytesIO(data)).read()


def compress_zst(data: bytes) -> bytes:
    cctx = zstandard.ZstdCompressor(level=3)
    return cctx.compress(data)


# ─────────────────────────────────────────────────────────────────────────────
# Tar modifier
# ─────────────────────────────────────────────────────────────────────────────

def patch_tar(tar_data: bytes,
              text_files: set[str],
              logo_files: set[str],
              logo_bytes: bytes,
              binary_files: set[str] = None) -> bytes:
    """
    Read a tar archive (uncompressed), patch files, return modified tar bytes.

    - text_files: set of member paths whose content should have text replaced
    - logo_files: set of member paths to replace entirely with logo_bytes
    - binary_files: set of member paths for safe binary byte replacement (e.g. .mo files)
    """
    if binary_files is None:
        binary_files = set()
    in_tf = tarfile.open(fileobj=io.BytesIO(tar_data), mode="r:")
    out_buf = io.BytesIO()
    out_tf = tarfile.open(fileobj=out_buf, mode="w:")

    for member in in_tf.getmembers():
        name = member.name.lstrip("./")

        if not member.isfile():
            out_tf.addfile(member)
            continue

        raw = in_tf.extractfile(member).read()

        if name in logo_files:
            raw = logo_bytes
            print(f"  [LOGO] Replaced: {member.name}")
        elif name in text_files:
            try:
                text = raw.decode("utf-8")
                for old, new in STR_REPLACEMENTS:
                    text = text.replace(old, new)
                raw = text.encode("utf-8")
                print(f"  [TEXT] Patched:  {member.name}")
            except Exception as e:
                print(f"  [WARN] Text patch failed for {member.name}: {e}")
        elif name in binary_files or any(name.endswith('.mo') for name in [name]):
            # Safe same-length binary replacement for .mo files
            for old, new in BINARY_REPLACEMENTS:
                if old in raw:
                    raw = raw.replace(old, new)
            print(f"  [BIN]  Patched:  {member.name}")

        # Update member size
        member.size = len(raw)
        out_tf.addfile(member, io.BytesIO(raw))

    out_tf.close()
    return out_buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Per-package patch definitions
# ─────────────────────────────────────────────────────────────────────────────

PATCHES = {
    "oobe_orig.deb": {
        "out_name": "anduinos-oobe_2.0.1-1+resolute_all.deb",
        "text_files": {
            "usr/bin/anduinos-oobe",
            "usr/share/applications/anduinos-oobe.desktop",
            "etc/xdg/autostart/anduinos-oobe.desktop",
        },
        "logo_files": set(),
        "binary_files": set(),  # .mo files auto-patched via endswith('.mo') check
    },
    "plymouth_orig.deb": {
        "out_name": "plymouth-anduinos_2.0.0+24.004.60+git20250831.4a3c171d-0ubuntu8-5+resolute-addon_amd64.deb",
        "text_files": {
            "usr/share/plymouth/themes/anduinos/anduinos.plymouth",
            "usr/share/plymouth/themes/anduinos-text/anduinos-text.plymouth",
        },
        "logo_files": {
            "usr/share/plymouth/themes/anduinos/watermark.png",
        },
    },
    "dconf_orig.deb": {
        "out_name": "anduinos-dconf-defaults_2.0.1-1+resolute_all.deb",
        "text_files": {
            "etc/dconf/db/anduinos.d/01-custom-keybindings.conf",
            "etc/dconf/db/anduinos.d/02-ptyxis-terminal.conf",
            "etc/dconf/db/anduinos.d/03-system-extensions.conf",
            "etc/gdm3/greeter.dconf-defaults",
            "usr/share/glib-2.0/schemas/99-anduinos-defaults.gschema.override",
        },
        "logo_files": {
            "usr/share/pixmaps/anduinos_text_smaller.png",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def patch_deb(in_path: str, out_name: str, text_files: set, logo_files: set, logo_bytes: bytes, binary_files: set = None):
    print(f"\n{'='*60}")
    print(f"Patching: {os.path.basename(in_path)}")
    print(f"{'='*60}")

    with open(in_path, "rb") as f:
        deb_data = f.read()

    members = parse_ar(deb_data)
    new_members = []

    for filename, content in members:
        if filename in ("data.tar.zst", "data.tar.gz", "data.tar.xz"):
            print(f"  Processing {filename} ...")
            # Decompress
            if filename.endswith(".zst"):
                tar_data = decompress_zst(content)
            else:
                raise ValueError(f"Unsupported compression: {filename}")

            # Patch tar
            tar_data = patch_tar(tar_data, text_files, logo_files, logo_bytes, binary_files or set())

            # Recompress
            content = compress_zst(tar_data)
            print(f"  Recompressed {filename}: {len(content)} bytes")

        elif filename == "control.tar.zst":
            # Patch control text (Package description etc.)
            try:
                tar_data = decompress_zst(content)
                in_tf = tarfile.open(fileobj=io.BytesIO(tar_data), mode="r:")
                out_buf = io.BytesIO()
                out_tf = tarfile.open(fileobj=out_buf, mode="w:")
                for member in in_tf.getmembers():
                    if member.isfile():
                        raw = in_tf.extractfile(member).read()
                        try:
                            text = raw.decode("utf-8")
                            for old, new in STR_REPLACEMENTS:
                                text = text.replace(old, new)
                            raw = text.encode("utf-8")
                        except Exception:
                            pass
                        member.size = len(raw)
                        out_tf.addfile(member, io.BytesIO(raw))
                    else:
                        out_tf.addfile(member)
                out_tf.close()
                content = compress_zst(out_buf.getvalue())
                print(f"  Patched control.tar.zst")
            except Exception as e:
                print(f"  [WARN] control.tar patch failed: {e}")

        new_members.append((filename, content))

    out_deb = build_ar(new_members)
    out_path = os.path.join(SCRIPT_DIR, "patched", out_name)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(out_deb)

    print(f"\n  [OK] Written: {out_path} ({len(out_deb):,} bytes)")
    return out_path


def main():
    print("Loading Andiora logo...")
    with open(ANDIORA_LOGO_PATH, "rb") as f:
        logo_bytes = f.read()
    print(f"Logo loaded: {len(logo_bytes)} bytes")

    os.makedirs(os.path.join(SCRIPT_DIR, "patched"), exist_ok=True)

    for deb_file, patch_info in PATCHES.items():
        in_path = os.path.join(SCRIPT_DIR, deb_file)
        if not os.path.exists(in_path):
            print(f"\n[SKIP] Not found: {in_path}")
            continue
        patch_deb(
            in_path=in_path,
            out_name=patch_info["out_name"],
            text_files=patch_info["text_files"],
            logo_files=patch_info["logo_files"],
            logo_bytes=logo_bytes,
            binary_files=patch_info.get("binary_files", set()),
        )

    print("\n" + "="*60)
    print("ALL DONE! Patched packages are in: patch_debs/patched/")
    print("="*60)


if __name__ == "__main__":
    main()
