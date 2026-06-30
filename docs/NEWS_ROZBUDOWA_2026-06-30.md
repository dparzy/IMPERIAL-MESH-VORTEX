# 📰 ROZBUDOWA SYSTEMU NEWS — research + plan (Stan na: 2026-06-30)

> Głęboki audyt NEWS-01 + sweep światowego rynku (Azja/EU/USA/świat) + propozycje
> oryginalnych modułów. Cel (Prawo XV): pełny potencjał, wyprzedzać konkurencję,
> najlepszy moment wejścia LONG/SHORT/HOLD. Wszystko mierzone (Prawo XVI).

## 1. STAN BAZOWY (co mamy — z kodu)

- **NEWS-01** (`sentyment.py`) — neuron: `NEWS_SENTYMENT[-1..1]` × `NEWS_PEWNOSC[0..1]` × `NEWS_N`.
  Próg szumu 0.30, mocny 0.65, min 2 nagłówki. Momentum informacyjny (poz→LONG, neg→SHORT).
- **AdapterNewsLLM** (`news_llm.py`) — klasyfikator: DeepSeek LLM + fallback słownikowy (~60 słów).
- **🆕 FetcherNewsRSS** (`news_fetcher.py`, 2026-06-30) — UNLOCK: pobiera nagłówki z darmowych
  RSS (CoinDesk/CoinTelegraph/Decrypt), filtr per-aktywo, dedup, offline-testowalny. **To
  zamyka brakujące ogniwo** — wcześniej adapter miał pusty feed → neuron zawsze milczał.

## 2. ŚWIATOWY RYNEK — co robią najlepsi (research 2026, ZPO)

**Dostawcy danych newsowych** (płatne API — punkt odniesienia jakości):
- CoinGecko News API — 100+ wydawców, 30+ języków, link news↔cena/on-chain
  (https://www.coingecko.com/learn/best-crypto-news-api)
- CoinDesk Data API — real-time + sentyment, event-driven (https://developers.coindesk.com/)
- Crypto News API — sentyment per artykuł + whale tx (https://cryptonews-api.com/)
- NewsData.io, CoinStats, Glassnode (on-chain intelligence).

**Badania (granica 2026):**
- **Event-Aware Sentiment Factors** (https://arxiv.org/abs/2508.07408) — KLUCZOWE: typ
  zdarzenia decyduje o kierunku. „Rumor/Speculation" i „Retail Buzz" mają **ujemny Sharpe**
  (KONTRARIAŃSKIE!). Płaski „pozytywny=LONG" jest BŁĘDNY dla części kategorii.
- **Janus-Q** (https://arxiv.org/abs/2602.19919) — end-to-end event-driven trading, gated reward.
- **Hybrid CNN-LSTM-AE + LLM sentiment** — anomaly detection w krypto (Springer 2026).
- GPT-4 fine-tuned na newsach krypto → 86.7% trafności klasyfikacji sentymentu.
- Techniki: **source credibility weighting**, **embedding event-linking** (ta sama historia
  u wielu wydawców), **original vs amplified** (oryginał vs powielenie).

## 3. PROPOZYCJE — nowe płaszczyzny (oryginalne moduły Imperium)

Każda = osobny wskaźnik/neuron, wdrażana z testami + pomiarem przewagi (Prawo XVI):

| # | Moduł | Co daje | Inspiracja/źródło | Status |
|---|-------|---------|-------------------|--------|
| 1 | **FetcherNewsRSS** | feed nagłówków (unlock) | CoinDesk/CT/Decrypt RSS | ✅ ZROBIONE |
| 2 | **Taksonomia zdarzeń** (NEWS-02) | LLM klasyfikuje TYP (hack/ETF/regulacja/rumor/macro); kierunek zależny od typu — rumor=kontrariański! | arXiv:2508.07408 | 🔵 plan |
| 3 | **Spike uwagi** (NEWS-03) | nagły wysyp nagłówków = zwiastun zmienności (niezależnie od kierunku) → modulator ryzyka | attention→vol | 🔵 plan |
| 4 | **Momentum sentymentu Δ** (NEWS-04) | ZMIANA sentymentu w czasie (przyspieszenie) = sygnał wyprzedzający | event-driven | 🔵 plan |
| 5 | **Waga wiarygodności źródła** | nagłówek z CoinDesk waży > anonimowy blog | source credibility (research) | 🔵 plan |
| 6 | **Nowość vs przeżute** | dedup wobec PAMIĘCI (W6/W8) — powtórzony news już wyceniony | novelty/original-vs-amplified | 🔵 plan |
| 7 | **Rozrzut/niezgoda** | nagłówki podzielone = niepewność (jak meta-labeling Gubernatora) | dispersion | 🔵 plan |
| 8 | **Zanik czasowy** | świeży nagłówek waży więcej (news szybko się starzeje) | half-life | 🔵 plan |
| 9 | **Sentyment social** | X/Reddit/Telegram (poza newsami) — retail buzz (uwaga: kontrariański!) | LunarCrush-like | 🔵 plan |
| 10 | **Whale/on-chain events** | duże transfery, ruchy giełd jako „news" twardych danych | Glassnode-like | 🔵 plan |

## 4. WSPARCIE METOD TRENINGOWYCH (Prawo XVI)

- **Logowanie do W1** (`pamiec_absolutna`): zapisuj `NEWS_SENTYMENT`+typ przy każdym barze →
  zmierz **korelację z przyszłym zwrotem** per kategoria (które newsy mają przewagę, które są szumem).
- **Cecha Jump Modelu** (W8 reżim): sentyment + spike uwagi jako wejście detektora reżimu.
- **Pamięć reżimowa** (W3/W4): „rumor pump w TREND_STRONG" inaczej waży niż w BEAR.
- **Walidacja kontrariańska**: zanim NEWS-02 dostanie wagę, OOS pomiar Sharpe per typ zdarzenia.

## 5. PROPOZYCJA NOWEJ ZASADY (do decyzji Cezara)

> **PRAWO XXII — PRZEWAGA KONKURENCYJNA (proponowane):** Imperium nieustannie mierzy się
> z najlepszymi na świecie. Gdy moduł jest słabszy od stanu sztuki — szukamy lepszego
> rozwiązania (research + adopcja), zachowując pełną symbiozę i pomiar (Prawo XVI). Cel
> nadrzędny: najlepszy zysk przy najlepszym momencie wejścia (LONG/SHORT/HOLD), sterowany
> kodem neuronów i bramek. Stagnacja przy gorszym rozwiązaniu = utrata potencjału (Prawo XV).

Mamy już Prawo XV (pełny potencjał) i Prawo XVI (pomiar) — XXII spina je w jawny imperatyw
„być lepszym od konkurencji". Dopisanie wymaga decyzji kierunkowej (Prawo XVIII).

## 6. REKOMENDOWANA KOLEJNOŚĆ

1. ✅ **FetcherNewsRSS** (zrobione — unlock)
2. **NEWS-02 Taksonomia zdarzeń** (największa przewaga: kierunek per typ, rumor=kontrariański)
3. **NEWS-03 Spike uwagi** + **NEWS-04 Δ sentymentu** (tanie, mocne, deterministyczne)
4. **Logowanie do W1 + pomiar predykcyjności** (zanim damy większą wagę)
5. Social/on-chain/credibility — gdy rdzeń zmierzony i działa
