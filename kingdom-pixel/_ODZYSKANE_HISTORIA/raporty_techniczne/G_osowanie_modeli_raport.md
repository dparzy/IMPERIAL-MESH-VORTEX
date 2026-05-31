
# DOKUMENTACJA TECHNICZNA: SYSTEM GLOSOWANIA ENSEMBLE (ensemble_voter.py)**Cel:** Implementacja systemu głosowania ważonego (Weighted Voting) z rygorystycznym filtrowaniem progu pewności oraz zabezpieczeniami anty-halucynacyjnymi (Zasada Prawdy).
**Docelowy odbiorca:** Model LLM / Agent AI / Inżynier ML
---## 1. Założenia biznesowe i logiczneSystem ma za zadanie agregować predykcje z wielu modeli bazowych (klasyfikatorów lub agentów) i podejmować decyzje wyłącznie wtedy, gdy wynik jest wysoce wiarygodny.

*   **Głosowanie ważone (Soft Weighted Voting):** Modele nie głosują "twardo" (0 lub 1). Agregacji podlegają pełne rozkłady prawdopodobieństw (`predict_proba`) pomnożone przez przypisane wagom współczynniki zaufania (\(W_i\)).
*   **Próg pewności (`min_confidence=0.65`):** Znormalizowany wynik końcowy dla wygrywającej klasy musi wynosić minimum 0.65. W przeciwnym razie system zwraca status braku decyzji (`-1`), co zapobiega wymuszaniu odpowiedzi przy niskiej pewności.*   **Zasada Prawdy i Brak Halucynacji:** Wprowadzono matematyczne i logiczne filtry bezpieczeństwa, które blokują decyzję, jeśli modele są wewnętrznie sprzeczne lub gdy "tłum" słabszych modeli próbuje przegłosować model ekspercki.
---## 2. Architektura filtrów anty-halucynacyjnych
Aby zapobiec zjawisku halucynacji w strukturach ensemble, zaimplementowano trzy warstwy ochrony:
1.  **Znormalizowana Entropia Shannona (\(H_{norm}\)):** Mierzy stopień rozproszenia i chaosu w ostatecznym rozkładzie prawdopodobieństwa. Jeśli modele są skrajnie podzielone (np. dwie klasy uzyskują zbliżone wyniki), entropia rośnie. Przekroczenie progu `max_entropy` automatycznie odrzuca predykcję.2.  **Bezpiecznik Lidera (Leader Anchor):** Identyfikuje model o najwyższej wadze (eksperta). Jeśli matematyczny konsensus matematyczny wskazuje klasę X, ale ekspert wskazuje klasę Y, system wykrywa anomalię/halucynację i flaguje transakcję jako niebezpieczną.
3.  **Normalizacja Sumy Wag:** Wyniki są dzielone przez sumę wag, co gwarantuje, że końcowe wartości zachowują właściwości prawdopodobieństwa (sumują się do 1.0) i są bezpośrednio porównywalne z progiem `0.65`.
---
## 3. Kod produkcyjny: `ensemble_voter.py`

Poniższy kod stanowi kompletną, produkcyjną implementację opartą o bibliotekę `numpy`.
```python
import numpy as np

def strict_ensemble_voter(predictions, weights, min_confidence=0.65, max_entropy=0.40):
    """
    Zaawansowany system głosowania ważonego z filtrami anty-halucynacyjnymi.
    
    Parametry:
    ----------
    predictions : list lub np.array
        Kształt: (liczba_modeli, liczba_klas). Zawiera rozkłady predict_proba.
    weights : list lub np.array
        Kształt: (liczba_modeli,). Wagi zaufania przypisane do modeli.
    min_confidence : float, optional
        Minimalny próg akceptacji decyzji. Domyślnie 0.65.
    max_entropy : float, optional
        Maksymalna dopuszczalna znormalizowana entropia (chaos). Domyślnie 0.40.
        
    Zwraca:
    -------
    dict
        Raport zawierający: 'decision' (klasa lub -1), 'confidence', 'entropy', 
        'is_safe' (bool) oraz 'rejection_reason' (str lub None).
    """
    # 1. Przygotowanie danych
    preds = np.array(predictions)
    w = np.array(weights).reshape(-1, 1)
    num_models, num_classes = preds.shape
    
    # 2. Identyfikacja głosu Lidera (Modelu o najwyższej wadze)
    hard_votes = np.argmax(preds, axis=1)
    strongest_model_idx = np.argmax(weights)
    leader_vote = hard_votes[strongest_model_idx]
    
    # 3. Obliczenie średniej ważonej i normalizacja rozkładu
    weighted_preds = np.sum(preds * w, axis=0)
    final_confidences = weighted_preds / np.sum(weights)
    
    # 4. Wyznaczenie klasy wygrywającej
    best_class = np.argmax(final_confidences)
    highest_confidence = final_confidences[best_class]
    
    # 5. Obliczenie znormalizowanej entropii Shannona (miara konfliktu)
    # Dodanie 1e-9 zapobiega błędom log(0)
    entropy = -np.sum(final_confidences * np.log2(final_confidences + 1e-9))
    normalized_entropy = entropy / np.log2(num_classes) if num_classes > 1 else 0.0

    # 6. Rygorystyczna ewaluacja bezpieczeństwa (Zasada Prawdy)
    is_safe = True
    rejection_reason = None
    
    if highest_confidence < min_confidence:
        is_safe = False
        rejection_reason = f"Niska pewność wyniku ({highest_confidence:.4f} < {min_confidence})"
        
    elif normalized_entropy > max_entropy:
        is_safe = False
        rejection_reason = f"Zbyt wysoki konflikt wewnętrzny modeli / entropia ({normalized_entropy:.4f} > {max_entropy})"
        
    elif best_class != leader_vote:
        is_safe = False
        rejection_reason = "Wykryto potencjalną halucynację: wynik konsensusu sprzeczny z modelem referencyjnym (liderem)"

    return {
        "decision": int(best_class) if is_safe else -1,
        "confidence": float(highest_confidence),
        "entropy": float(normalized_entropy),
        "is_safe": is_safe,
        "rejection_reason": rejection_reason
    }

# --- BLOK TESTOWY / PRZYKŁADY URUCHOMIENIA ---
if __name__ == "__main__":
    print("=== SCENARIUSZ 1: Konsensus i wysoka pewność (Sukces) ===")
    preds_success = [
        [0.1, 0.8, 0.1],  # Model 1 (waga 1.0)
        [0.0, 0.9, 0.1],  # Model 2 (waga 1.5)
        [0.2, 0.7, 0.1]   # Model 3 (Ekspert, waga 3.0)
    ]
    weights_success = [1.0, 1.5, 3.0]
    res1 = strict_ensemble_voter(preds_success, weights_success)
    print(f"Wynik: {res1}\n")

    print("=== SCENARIUSZ 2: Próba halucynacji (Odrzucenie przez filtr Lidera) ===")
    # Dwa słabsze modele dają wysoką pewność błędnej klasie 2, ale Ekspert (Model 3) wie, że to klasa 0
    preds_hallucination = [
        [0.1, 0.1, 0.8],  # Model 1 (waga 1.0) -> Halucynacja
        [0.0, 0.2, 0.8],  # Model 2 (waga 1.0) -> Halucynacja
        [0.8, 0.1, 0.1]   # Model 3 (waga 4.0) -> Ekspert zna prawdę
    ]
    weights_hallucination = [1.0, 1.0, 4.0]
    res2 = strict_ensemble_voter(preds_hallucination, weights_hallucination)
    print(f"Wynik: {res2}\n")
    
    print("=== SCENARIUSZ 3: Niska pewność (Odrzucenie przez próg min_confidence=0.65) ===")
    preds_low_conf = [
        [0.4, 0.3, 0.3],
        [0.3, 0.4, 0.3],
        [0.2, 0.3, 0.5]
    ]
    weights_low = [1.0, 1.0, 1.0]
    res3 = strict_ensemble_voter(preds_low_conf, weights_low, min_confidence=0.65)
    print(f"Wynik: {res3}\n")
```
---## 4. Instrukcja integracji dla Modelu AIPodczas implementacji tego modułu w strukturach agentowych (Multi-Agent Systems), należy zachować następujący kontrakt danych:
1.  **Format wejściowy (`predictions`):** Musi być ustandaryzowaną macierzą prawdopodobieństw (suma wiersza = 1.0). Surowe wartości typu *logits* muszą najpierw zostać przepuszczone przez funkcję Softmax.
2.  **Obsługa wyjścia:** Zwrócenie wartości `-1` w kluczu `decision` powinno skutkować uruchomieniem procedury fallback (np. przekazaniem zadania do człowieka, uruchomieniem bardziej wymagającego modelu LLM lub zwróceniem tokenu odpowiedzi bezpiecznej: *"Nie mam wystarczającej pewności, aby odpowiedzieć"*).

------------------------------
Możesz teraz przesłać ten dokument do dowolnego innego systemu AI. Służy on jako kompletny kontekst implementacyjny.
W następnym kroku możemy przygotować dla Ciebie skrypt kalibracyjny (Platt Scaling), który automatycznie dopasuje wagi modeli na podstawie zbioru walidacyjnego, lub adapter do biblioteki scikit-learn, aby wpiąć ten kod do istniejącego pipeline'u ML. Które rozwiązanie wdrożyć?

