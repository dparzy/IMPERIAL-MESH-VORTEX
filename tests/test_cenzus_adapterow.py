"""Testy CENZUS ADAPTERÓW (Prawo XV, Prawo XXI) — struktura bez sieci.

Nie uruchamia realnego cenzusu (wymaga giełdy) — waliduje spójność listy celów
z 22 modułami adapterowymi audytu i integralność map powodów. Chroni przed
cichym rozjazdem listy CELE (osierocony klucz) po zmianie neuronów.
"""
from narzedzia import cenzus_adapterow as ca

# 22 moduły adapterowe (audyt_spojnosci.py --luki) — Prawo XV.
OCZEKIWANE_22 = {
    "AUG-01", "C-01", "NEWS-01", "NEWS-02", "NEWS-03", "NEWS-04",
    "OC-06", "OC-07", "OC-08", "PSY-01", "PSY-02", "PSY-03", "PSY-04",
    "RADAR-01", "RADAR-02", "RADAR-03", "RADAR-04", "RADAR-05",
    "V-03", "X-28", "Z-06", "Z-07",
}


def test_cenzus_ma_dokladnie_22_cele():
    assert len(ca.CELE) == 22, f"oczekiwano 22 celów, jest {len(ca.CELE)}"
    assert len(set(ca.CELE)) == 22, "duplikaty w CELE"


def test_cenzus_cele_zgodne_z_audytem():
    assert set(ca.CELE) == OCZEKIWANE_22, (
        f"rozjazd z listą 22 modułów adapterowych: "
        f"nadmiar={set(ca.CELE) - OCZEKIWANE_22}, brak={OCZEKIWANE_22 - set(ca.CELE)}"
    )


def test_powody_warunkowe_podzbiorem_celow():
    # Każdy klucz z mapą powodu musi istnieć w CELE (żaden osierocony powód).
    obce = set(ca.POWODY_WARUNKOWE) - set(ca.CELE)
    assert not obce, f"powody dla kluczy spoza CELE: {obce}"


def test_pasek_nie_wywala_sie():
    # Pasek postępu (Prawo XXIV) — smoke: brak wyjątku na granicy i=n.
    ca._pasek(1, 3, "test")
    ca._pasek(3, 3, "koniec")
