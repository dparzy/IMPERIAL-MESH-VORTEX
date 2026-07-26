---
name: limes
description: SIGILLUM LIMES — wał graniczny, twarda bramka Prawa XXI przed każdym commitem. Użyj przed commitem oraz gdy Cezar pisze „bramka", „sprawdź wszystko", „limes". Uruchamia testy, pełny audyt spójności (z ruff W13), łowcę powtórek z Księgi Wad, spis obalonych twierdzeń (INDEX FALSORUM) i bilans długu honorowego.
---

# 🔏 SIGILLUM LIMES — bramka Prawa XXI

*Limes* to rzymski wał graniczny: nic nie przechodzi bez kontroli. Żaden commit nie
powstaje, dopóki wszystkie bramki nie są zielone.

## Wykonanie

1. **Wypisz komendy bramki i uruchom je po kolei** (kolejność ma znaczenie — pierwsza
   czerwona zatrzymuje resztę):

```bash
python -m imperium.biblioteki.sigillarium limes
```

Ten skill **celowo nie wypisuje komend bramki** — są jednym źródłem prawdy w rejestrze
`SIGLA` (`imperium/biblioteki/sigillarium.py`). Kopia tutaj rozjechałaby się przy zmianie
bramki (to samo gnicie, które SIGILLARIUM ma eliminować). Pieczęć podaje aktualną listę.

2. Po zielonej bramce, **przed pushem**, dochodzi recenzja adversarialna `/code-review`
   na diffie (perspektywa recenzenta, nie autora) — nie jest częścią bramki LIMES, bo to
   nie jest komenda CLI z jednoznacznym exit code.

## Zasady

- Czerwona bramka → **NIE commitujesz**: naprawiasz u źródła, potem powtarzasz LIMES.
- Jeśli pieczęć zgłosi `🚨 MARTWE KOMENDY`, któryś skrypt/moduł bramki zniknął lub zmienił
  nazwę — bramka udawałaby sprawną. Napraw natychmiast.
