# 📊 Dane tematyczne — korpus `dane` dla Bibliotheca-RAG

> Ten folder to miejsce na **dane tematyczne nie-książkowe**, które mają trafić do
> pamięci semantycznej RAG obok książek i encyklopedii.

## Co tu wrzucać

| Format | Przykład | Jak ekstraktor czyta |
|--------|----------|----------------------|
| `.csv` | wyniki backtestów, tabele wskaźników | nagłówek + wiersze jako `kolumna: wartość` |
| `.json` | konfiguracje, słowniki pojęć | spłaszczone `klucz.podklucz: wartość` |
| `.txt` | notatki, transkrypcje, lekcje | tekst surowy |
| `.md` | opracowania tematyczne | tekst markdown |

## Jak zindeksować

```bash
# po wrzuceniu plików — przyrostowo (tylko nowe):
python narzedzia/rag/indeksuj.py --tylko-nowe
```

Pliki z tego folderu trafiają do korpusu **`dane`** — można je filtrować w wyszukiwaniu:

```bash
python narzedzia/rag/szukaj.py "wynik backtest MTF" --korpus dane
```

## Zasada (Prawo XIX — kod jest prawem)

Dane tu wrzucone są **wiedzą pomocniczą**, nie źródłem prawdy o kodzie. Źródłem prawdy
o systemie pozostaje `docs/MANIFEST_KODU.md`. Ten folder to materiał do przeszukiwania,
nie do audytu spójności.
