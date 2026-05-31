# 💭 POMYSŁY LUŹNE — DELTA v1.21
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.21). Tylko nowości.

## v1.21 (30.05.2026) — DOKUMENT IMV: stos lekki + architektura poliglota + DEBUNK + Zasady v4.5

### ✅ STOS NA SŁABY SPRZĘT (wartościowe, wprost dla Fazy 0/1)
- **NullClaw** (678 KB, ~1 MB RAM) zamiast OpenClaw (>1 GB) → ~99% mniej RAM. **Zvec** (ultralekki vector store) zamiast Caliby. Start z **10–20 agentami** (nie 200+). ClickHouse na zewnętrznym SSD.
- Min: 4 rdzenie / 16 GB; rekom. 8+ rdzeni / 32–64 GB, Ubuntu. → dobre dla Twojego sprzętu. NullClaw/Zvec **do weryfikacji później** (czy realne narzędzia).

### 🏛️ ARCHITEKTURA POLIGLOTA „Cognitive Mesh" (realizuje wizję v1.4: Python+Rust+Zig)
- **MÓZG = Python** (decyzje) · **MIĘŚNIE = Rust** (egzekucja, szybkość) · **ZWIADOWCY = Zig** (`nullsliver` — ultralekkie neurony/**mini-boty**) · magistrala **ZeroMQ + Arrow**. W dokumencie jest kod + instrukcja kompilacji (ETAP 0–3).
- → mapuje na nasz organizm: **Zig = mini-boty czujniki, Rust = Ręce (≈ NautilusTrader), Python = Mózg.** Wzorzec wart adaptacji (nie kopiowania na ślepo).

### ⚠️ DEBUNK: „MAPA DROGOWA DO MILIONA" — to FANTAZJA (uczciwie, jak prosiłeś)
- Dokument obiecuje **1–5% DZIENNIE** i $50 → $1 000 000 w 6–18 mies. **To nierealne i niebezpieczne.** Dla skali: 2% dziennie ≈ 137 000% rocznie; 5% dziennie = astronomicznie niemożliwe. **Nikt nie utrzymuje 1–5% dziennie.** Dobrzy profesjonaliści cieszą się z **~15–30% ROCZNIE**, z okresami strat.
- Trzymamy NASZĄ realną oś: **lata, nie miesiące**; zwalidowana przewaga, nie „pewniak". Te liczby = marketing/survivorship → **odrzucamy**. Zostawiamy etapy tylko jako KIERUNEK (snajper → sfora → legion → imperium), bez bajkowych % i terminów.
- Też: „pewność 62% → 87–92%" = twierdzenie **niezweryfikowane** (warstwy walidacji nie dają automatycznie 90%). Sceptycznie.

### 📜 Zasady v4.5 (SHINSŌ) vs nasze v4
- Ich rdzeń: zero halucynacji/kłamstwa/manipulacji, tylko prawda, „nie wiem" gdy nie wiem, **każdy link zweryfikowany**, Markdown. = zgodne z naszym fundamentem (nasze v4 = 79 zasad, szersze). „Weryfikuj każdy link" = dokładnie nasz link-diving. **Nic nowego do dodania** — potwierdzenie kierunku.

## 📍 POSTĘP — dokument: przeczytane entries 130–132 + raporty finałowe.
⏭️ NASTĘPNE: QUINTESSENCE (11. moduł), kod Cognitive Mesh, entries 133–136+, ogon do ~L27000.
