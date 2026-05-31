# 💭 POMYSŁY LUŹNE — DELTA v1.17
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.17). Tylko nowości.

## v1.17 (30.05.2026) — LINK-DIVE: DoWhy + Parrondo (gem + myth-bust)

### ✅ DoWhy / PyWhy (github: microsoft/dowhy) — realny standard, broń ANTI-OVERFIT
- Microsoft + AWS (ekosystem PyWhy), **1M+ pobrań**, standard branżowy przyczynowości w Pythonie.
- 4 kroki: model (graf przyczynowy + założenia) → identyfikacja (czy efekt estymowalny) → estymacja → **REFUTACJA** (placebo, bootstrap, test ukrytych zakłócaczy, analiza wrażliwości). API refutacji = serce biblioteki.
- Dla nas: odróżnia REALNĄ przyczynę od **pozornej korelacji** (klasyk: lody ↔ ataki rekinów — oba od słonecznej pogody). W tradingu broń przeciw „sygnał X przewidział ruch Y", gdy to był przypadek/zbieg → **anti-overfitting**.
- ⚠️ Uczciwie: przyczynowość na **niestacjonarnym** rynku jest TRUDNA (zakłócacze wszędzie, graf trudny do poprawnego określenia) — to nie srebrna kula. Ale sama DYSCYPLINA „refutuj własne znaleziska" = nasz rygor (Zasada walidacji).

### ⚠️ Parrondo's Paradox — MYTH-BUST (uczciwie: jako strategia to ślepa uliczka)
- Realne zjawisko matematyczne (Parrondo 1996): dwie przegrywające gry, mieszane w kolejności → mogą wygrywać. ALE **w tradingu mało użyteczne** (Wikipedia + analizy asset-management mówią wprost): mechanizm wymaga gier **zależnych od kapitału i sprzężonych** — czego w realnych rynkach **NIE ma**. Dodatkowo: żeby wyszło, musisz mieć grę >67% win — a wtedy grałbyś tylko nią, bez mieszania.
- ✅ Realny, użyteczny KUZYN: **volatility pumping / rebalancing premium (demon Shannona)** — systematyczne rebalansowanie między zmiennymi, powracającymi do średniej aktywami wyciąga realny zwrot ZE zmienności (związek z teorią portfela). **TO** możemy badać.
- 📌 **Korekta v1.6:** literalny Parrondo → odpuszczamy. Zamiast tego: volatility pumping / rebalancing.

## 📍 POSTĘP — link-diving (11): Kronos·NEXUS·TradingAgents·Freqtrade·VectorBT·FinRL·OpenBB·FinCrew·RegimeNAS·**DoWhy·Parrondo** ✅.
⏭️ Zostały m.in.: EvoAgentX, Hummingbot, NautilusTrader, Pandas-TA, Kronos-demo (na żywo) — albo wracamy do czytania dokumentu IMV do końca.
