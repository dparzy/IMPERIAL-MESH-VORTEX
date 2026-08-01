#!/bin/bash
# 🪙 EXACTOR RENUNTIATIONIS — hook Stop: sprawdzenie meldunku BEZ UDZIAŁU PAMIĘCI ARCHITEKTA.
#
# Wrapper jest CIENKI Z ROZMYSŁEM (ten sam wzorzec, co CUSTOS LIMINIS i VIGIL): cała decyzja
# siedzi w organie `imperium/pretorianie/exactor.py`, który ma testy. Skrypt powłoki bez testów
# jest miejscem, w którym reguły cicho gniją.
#
# POWÓD ISTNIENIA (nota N-b74ce133, TALAR wagi 2): krok 8 CLAUSURY każe podać PEŁNY blok
# PowerShell (`cd` + `git push origin <gałąź>`). Architekt podał sam `git push`, choć rozkaz
# stał w konstytucji, w pamięci prywatnej, a pieczęć wydrukowała go na ekran kilka minut
# wcześniej. Wiedza była — brakowało MECHANIZMU. Skill wywołuje się z pamięci, czyli opiera
# się dokładnie na tym, co zawiodło; hook nie pyta nikogo o zgodę na sprawdzenie.
#
# ZASIĘG ŚWIADOMIE WĄSKI: badany jest WYŁĄCZNIE krok 8 — jedyna powinność ze zmierzonym
# ZEREM fałszywych alarmów (na 156 przekazaniach ze 190 historycznych meldunków). Poziom
# „domkniecie" NIE jest skalibrowany i do automatu odpalanego po KAŻDEJ turze nie wchodzi:
# strażnik krzyczący bez pokrycia uczy ignorowania siebie.
#
# ZAWSZE kończy kodem 0. Blokada jest wyrażana protokołem (JSON `decision: block`), nie kodem
# wyjścia — a przy powtórnym wejściu (`stop_hook_active`) organ milczy, żeby nie zrobić pętli.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
exec python -m imperium.pretorianie.exactor --hook
