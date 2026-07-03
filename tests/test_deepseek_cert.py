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
