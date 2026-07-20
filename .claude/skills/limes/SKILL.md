---
name: limes
description: SIGILLUM LIMES — wał graniczny, twarda bramka Prawa XXI przed każdym commitem. Użyj przed commitem oraz gdy Cezar pisze „bramka", „sprawdź wszystko", „limes". Uruchamia testy, audyt spójności (17 warstw z ruff), łowcę powtórek z Księgi Wad, spis obalonych twierdzeń (INDEX FALSORUM) i bilans długu honorowego.
---

# 🔏 SIGILLUM LIMES — bramka Prawa XXI

*Limes* to rzymski wał graniczny: nic nie przechodzi bez kontroli. Żaden commit nie
powstaje, dopóki wszystkie bramki nie są zielone.

## Wykonanie

Wypisz komendy pieczęci, a potem uruchom je po kolei:

```bash
python -m imperium.biblioteki.sigillarium limes
```

Bramki (kolejność ma znaczenie — pierwsza czerwona zatrzymuje resztę):

1. `python tests/run_tests.py` — musi być **X/X zielone**
2. `python narzedzia/audyt_spojnosci.py` — musi być **exit 0** (17 warstw, w tym ruff W13)
3. `python narzedzia/skan_wad_kodu.py` — łowca powtórek znanych klas błędów
4. `python narzedzia/skan_wad_kodu.py --falsa` — INDEX FALSORUM: żadne obalone
   twierdzenie nie wróciło do korpusu
5. `python -m imperium.biblioteki.codex_notarum bilans` — dług honorowy musi być **0**

## Zasady

- Czerwona bramka → **NIE commitujesz**: naprawiasz u źródła, potem powtarzasz LIMES.
- Przed pushem dochodzi jeszcze recenzja adversarialna `/code-review` na diffie
  (perspektywa recenzenta, nie autora).
- Jeśli pieczęć zgłosi `🚨 MARTWE KOMENDY`, któryś skrypt bramki zniknął lub zmienił
  nazwę — bramka udawałaby sprawną. Napraw natychmiast.
