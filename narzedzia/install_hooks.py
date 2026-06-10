#!/usr/bin/env python3
"""
Instalator git hooków Imperium.

Uruchom po git clone lub gdy hooki znikną:
    python narzedzia/install_hooks.py

Instaluje:
  .git/hooks/pre-commit — blokuje commit gdy testy/audyt czerwone (Prawo XXI)
"""

import os
import shutil
import stat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_DIR = os.path.join(ROOT, ".git", "hooks")
SOURCE_DIR = os.path.join(ROOT, "narzedzia", "hooks_src")

HOOKS = ["pre-commit"]


def install():
    for hook_name in HOOKS:
        src = os.path.join(SOURCE_DIR, hook_name)
        dst = os.path.join(HOOKS_DIR, hook_name)

        if not os.path.exists(src):
            print(f"  ⚠️  Brak źródła: {src} — pominięto")
            continue

        shutil.copy2(src, dst)
        # Nadaj prawo wykonania
        st = os.stat(dst)
        os.chmod(dst, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  ✅ Zainstalowano: .git/hooks/{hook_name}")

    print("\nGit hooki Imperium gotowe. Każdy commit będzie weryfikowany (Prawo XXI).")


if __name__ == "__main__":
    os.makedirs(HOOKS_DIR, exist_ok=True)
    install()
