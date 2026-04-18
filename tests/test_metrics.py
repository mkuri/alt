from alt_body.metrics import calculate_metrics


def test_ffmi_calculation():
    result = calculate_metrics(
        weight_kg=70.0,
        body_fat_percent=20.0,
        skeletal_muscle_mass_kg=30.0,
        height_m=1.75,
    )
    # LBM = 70.0 * (1 - 20.0/100) = 56.0
    # FFMI raw = 56.0 / (1.75^2) = 18.2857
    # FFMI normalized = 18.2857 + 6.1 * (1.8 - 1.75) = 18.2857 + 0.305 = 18.591 -> 18.59
    assert result["ffmi"] == 18.59
    # SMR = 30.0 / 70.0 * 100 = 42.86
    assert result["skeletal_muscle_ratio"] == 42.86


def test_ffmi_without_body_fat():
    result = calculate_metrics(
        weight_kg=70.0,
        body_fat_percent=None,
        skeletal_muscle_mass_kg=30.0,
        height_m=1.75,
    )
    assert result["ffmi"] is None
    assert result["skeletal_muscle_ratio"] == 42.86


def test_skeletal_muscle_ratio_without_smm():
    result = calculate_metrics(
        weight_kg=70.0,
        body_fat_percent=20.0,
        skeletal_muscle_mass_kg=None,
        height_m=1.75,
    )
    assert result["ffmi"] == 18.59
    assert result["skeletal_muscle_ratio"] is None
