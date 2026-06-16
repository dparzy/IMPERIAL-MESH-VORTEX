import logging; logging.disable(logging.CRITICAL)
from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
from imperium.legiony.rejestr import wszystkie_neurony
import numpy as np

bary = wczytaj_csv("dane/4h/Binance_BTCUSDT_4h.csv", interwal="4h", limit=600)
bud = BudowniczyWskaznikow()
neurony = wszystkie_neurony()
NOWE = {"V-06","V-07","VP-01","Z-06","Z-07"}

def sygn(s):
    k = 1 if s.kierunek=="LONG" else (-1 if s.kierunek=="SHORT" else 0)
    val = k*s.pewnosc
    # Amihud: defensywny → użyj -pewnosc_przeciwnika jako sygnał (tłumienie)
    if val==0 and getattr(s,"pewnosc_przeciwnika",0)>0:
        val = -getattr(s,"pewnosc_przeciwnika")
    return val

serie = {n.KLUCZ: [] for n in neurony}
start = max(360, len(bary)-220)   # ostatnie ~220 barów, Pi Cycle ma ≥360 historii
for i in range(start, len(bary)):
    w = bud.zbuduj(bary[:i+1])
    for n in neurony:
        try: serie[n.KLUCZ].append(sygn(n.interpretuj(w)))
        except Exception: serie[n.KLUCZ].append(0.0)

def corr(a,b):
    a,b=np.array(a),np.array(b)
    if np.std(a)<1e-9 or np.std(b)<1e-9: return None
    return float(np.corrcoef(a,b)[0,1])

print(f"Okno: {len(bary)-start} barów 4h BTC\n")
for nk in sorted(NOWE):
    var = np.std(serie[nk])
    if var < 1e-9:
        print(f"{nk}: STAŁY (zerowa wariancja w oknie) — brak sygnału tu"); continue
    kor=[]
    for n in neurony:
        if n.KLUCZ==nk: continue
        c=corr(serie[nk], serie[n.KLUCZ])
        if c is not None: kor.append((abs(c),n.KLUCZ,c))
    kor.sort(reverse=True)
    top=kor[:3]
    maxr = top[0][0] if top else 0
    flag = "✅ dekorel." if maxr<0.8 else "⚠️ redundancja"
    aktyw = sum(1 for x in serie[nk] if abs(x)>0.01)
    print(f"{nk}: aktywny {aktyw}/{len(serie[nk])} barów | max|r|={maxr:.2f} {flag}")
    for a,k,c in top: print(f"     vs {k}: r={c:+.2f}")
