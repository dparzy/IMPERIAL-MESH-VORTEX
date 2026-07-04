"""Test zabezpieczenia SSL_CERT_FILE w GlosImperium (Prawo XV) — bez sieci/API."""

import os
from imperium.cesarz.deepseek_glos import _napraw_zepsuty_cert_env


def test_usuwa_nieistniejacy_cert_file(monkeypatch):
    monkeypatch.setenv("SSL_CERT_FILE", "/nie/ma/takiego/cacert.pem")
    _napraw_zepsuty_cert_env()
    assert "SSL_CERT_FILE" not in os.environ   # martwy wpis usunięty


def test_zachowuje_istniejacy_cert_file(tmp_path, monkeypatch):
    plik = tmp_path / "cacert.pem"
    plik.write_text("x", encoding="utf-8")
    monkeypatch.setenv("SSL_CERT_FILE", str(plik))
    _napraw_zepsuty_cert_env()
    assert os.environ.get("SSL_CERT_FILE") == str(plik)   # poprawny NIE ruszony


def test_brak_zmiennej_nie_wybucha(monkeypatch):
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    _napraw_zepsuty_cert_env()   # nie rzuca


def test_usuwa_nieistniejacy_cert_dir(monkeypatch):
    monkeypatch.setenv("SSL_CERT_DIR", "/nie/ma/takiego/katalogu")
    _napraw_zepsuty_cert_env()
    assert "SSL_CERT_DIR" not in os.environ


def test_zachowuje_istniejacy_cert_dir(tmp_path, monkeypatch):
    """Istniejący katalog CA-bundle NIE jest kasowany (enterprise CA)."""
    monkeypatch.setenv("SSL_CERT_DIR", str(tmp_path))
    _napraw_zepsuty_cert_env()
    assert os.environ.get("SSL_CERT_DIR") == str(tmp_path)


def test_cert_dir_lista_zachowuje_gdy_jeden_istnieje(tmp_path, monkeypatch):
    """SSL_CERT_DIR = lista (os.pathsep); zachowaj gdy CHOĆ JEDEN komponent istnieje."""
    lista = os.pathsep.join(["/nie/ma", str(tmp_path)])
    monkeypatch.setenv("SSL_CERT_DIR", lista)
    _napraw_zepsuty_cert_env()
    assert os.environ.get("SSL_CERT_DIR") == lista   # cały wpis nietknięty


def test_cert_dir_lista_kasuje_gdy_zaden_nie_istnieje(monkeypatch):
    """Lista samych martwych katalogów → usuń cały wpis."""
    monkeypatch.setenv("SSL_CERT_DIR", os.pathsep.join(["/nie/ma/1", "/nie/ma/2"]))
    _napraw_zepsuty_cert_env()
    assert "SSL_CERT_DIR" not in os.environ
