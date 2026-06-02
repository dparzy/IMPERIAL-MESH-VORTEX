# 📐 WZORZEC PEŁNEGO OPISU — Zasada Pełnego Opisu (ZPO)

> **Status:** ROZKAZ STAŁY (Cezar zatwierdził 2026-06-02)
> **Po co ten dokument:** Cezar jest nowicjuszem. Każdy moduł, neuron, strategia czy inspiracja
> MUSI być opisana tak, żeby dało się ją zrozumieć BEZ wiedzy eksperckiej i BEZ pytania mnie.
> **Zasada nadrzędna:** Nigdy skrótu bez rozwinięcia. Nigdy nazwy bez źródła. Nigdy liczby bez kontekstu.

---

## ⚖️ DLACZEGO TA ZASADA ISTNIEJE (powiązanie z Prawami)

- **Prawo I (Zero halucynacji):** jeśli czegoś nie zweryfikowałem — piszę to wprost (status weryfikacji).
- **Prawo XVII (Rozpoznanie terenu):** pełny opis = nie trzeba zgadywać z pamięci, wszystko jest w dokumencie.
- **Prawo XIX (Kod jest prawem):** opis mówi jasno, czy coś JEST w kodzie, czy to tylko plan.
- **Prawo XXI (Chirurgiczna precyzja):** klucz, nazwa, kategoria, status — zawsze dokładne, nigdy "mniej więcej".

**Złamanie ZPO:** podanie skrótu bez pełnej nazwy, projektu bez linku, lub liczby bez wyjaśnienia co znaczy.

---

## 🧩 SZABLON — KAŻDY wpis (neuron / moduł / inspiracja) ma TE pola

Skopiuj ten blok przy dodawaniu czegokolwiek nowego. Pola oznaczone 🔴 są OBOWIĄZKOWE.

```markdown
### [KLUCZ] | [Pełna nazwa robocza po polsku]

- 🔴 **Klucz:** np. `ML-24` (unikalny identyfikator w katalogu)
- 🔴 **Pełna nazwa (oryginalna):** rozwinięcie WSZYSTKICH skrótów, w języku źródła
  (np. "SHARP = Self-Evolving Rubric Policy" — nigdy samo "SHARP")
- 🔴 **Nazwa po polsku:** co to znaczy zwykłym językiem
- 🔴 **Źródło (link):** pełny URL (arxiv.org/abs/..., github.com/...) — NIE skrót, NIE "gdzieś w necie"
- 🔴 **Typ źródła:** praca naukowa (arXiv) / repozytorium (GitHub) / skrypt (TradingView) / blog / rozmowa
- 🔴 **Status weryfikacji:** ✅ zweryfikowany (otworzyłem, istnieje) /
  ⚠️ niezweryfikowany (podany przez Cezara, NIE sprawdziłem) /
  ❌ błędny (sprawdziłem, nie istnieje / link martwy)
- 🔴 **Kategoria:** litera + co znaczy (np. "E = Entropia/AI")
- 🔴 **Co robi (dla nowicjusza):** 1-2 zdania prostym językiem, zero żargonu bez wyjaśnienia
- 🔴 **Jak interpretuje:** kiedy daje LONG, kiedy SHORT, kiedy NEUTRAL (to robi każdy neuron)
- **Dane wejściowe:** czego potrzebuje (OHLCV / order book L2 / on-chain API / dane opcji...)
- **Skąd dane:** Brama Kalkulatora (Prawo I) / adapter API / feed zewnętrzny
- 🔴 **Status implementacji:** ✅ w kodzie (+test) / 🌙 budzony wewnętrznie / 🔇 czeka na feed / 🔴 tylko plan
- 🔴 **Faza wdrożenia:** Faza 0 (rdzeń) / Faza 2 (ML) / Faza 3 (multi-exchange) / Faza 4 (autonomia)
- **Waga (W1-W9):** jak ważny głos (W9 = krytyczny, W1 = pomocniczy) + dlaczego tyle
- 🔴 **Powód (dlaczego go chcemy):** jaką lukę wypełnia, czego rój dziś nie widzi
- **Ryzyko / ograniczenia:** czego wymaga, co może pójść nie tak, koszt (GPU? płatne API?)
- **Powiązania:** z którymi neuronami/strategiami/wizjami (W-xxx) współgra
```

---

## ✅ PRZYKŁAD WYPEŁNIONY (wzór do naśladowania)

### ML-24 | Samoewoluująca Polityka Rubryk

- **Klucz:** `ML-24`
- **Pełna nazwa (oryginalna):** SHARP — **S**elf-**H**arnessing **A**daptive **R**ubric **P**olicy
  *(uwaga: dokładne rozwinięcie akronimu wymaga weryfikacji w źródle — patrz status)*
- **Nazwa po polsku:** Samoewoluująca Polityka Rubryk (system, który sam poprawia własne kryteria oceny)
- **Źródło (link):** https://arxiv.org/abs/2605.06822
- **Typ źródła:** praca naukowa (arXiv)
- **Status weryfikacji:** ⚠️ niezweryfikowany — podany przez Cezara, link ma datę z przyszłości (2026-05), NIE potwierdziłem że istnieje
- **Kategoria:** E = Entropia/AI (samouczące się modele)
- **Co robi (dla nowicjusza):** zamiast sztywnych reguł "kup gdy RSI<30", system sam pisze i poprawia
  swoje kryteria oceny sygnałów na podstawie tego, co działało — jak uczeń, który poprawia własną ściągę.
- **Jak interpretuje:** to nie klasyczny neuron — to warstwa AUDYTU nad decyzjami Cesarza (DeepSeek).
  Ocenia jakość decyzji i podnosi/obniża zaufanie do innych głosów.
- **Dane wejściowe:** historia decyzji roju + ich wyniki (zysk/strata)
- **Skąd dane:** Pamięć Absolutna (biblioteki/) + wyniki Koloseum
- **Status implementacji:** 🔴 tylko plan (wizja W-009)
- **Faza wdrożenia:** Faza 2+ (wymaga modelu ML / API LLM)
- **Waga:** — (warstwa audytu, nie głosuje bezpośrednio)
- **Powód:** rój dziś ma stałe wagi; SHARP pozwoliłby im się uczyć z własnych błędów (samodoskonalenie).
- **Ryzyko / ograniczenia:** wymaga LLM (koszt API), ryzyko przeuczenia, trudny do audytu (Prawo I!)
- **Powiązania:** wizja W-009, neuron ML-08 (DeepAlpha), Reflexion (W-018)

---

## 📋 ZASADY SKRÓTOWE (czek-lista przy każdym wpisie)

- [ ] Każdy skrót ma rozwinięcie przy pierwszym użyciu (SHARP → Self-Evolving Rubric Policy)
- [ ] Każdy projekt zewnętrzny ma pełny link (nie "arxiv 2605..." tylko `https://arxiv.org/abs/2605.06822`)
- [ ] Status weryfikacji jest UCZCIWY (jeśli nie sprawdziłem — piszę ⚠️, nie udaję ✅)
- [ ] Jest wyjaśnienie "dla nowicjusza" prostym językiem
- [ ] Jest jasno napisane: kod czy plan (Prawo XIX)
- [ ] Jest powód — po co nam to, jaką lukę wypełnia
- [ ] Jest faza wdrożenia (kiedy, nie "kiedyś")

---

*VITRUVIUSZ — "Opis, którego nowicjusz nie rozumie, jest opisem dla nikogo. Pełnia albo nic."*
