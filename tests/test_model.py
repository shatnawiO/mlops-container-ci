from pathlib import Path
from src.app.main import load_model_from_disk
from src.train.train import FEATURE_NAMES, TARGET_NAMES, train_and_save


def test_model_loads_and_has_required_attributes(tmp_path: Path):
    """
    PROTECTS AGAINST: Corrupted or missing model artifacts in production.
    Ensures that the model artifact file can be loaded by joblib, contains
    the trained scikit-learn pipeline, correct input feature names, target classes,
    and achieves the expected minimum accuracy benchmark.
    """
    test_model_file = str(tmp_path / "test_model.joblib")
    train_and_save(output_path=test_model_file)

    assert Path(test_model_file).exists(), "Model file was not created"
    loaded = load_model_from_disk(test_model_file)

    assert loaded is not None, "Failed to load model artifact from disk"
    assert "pipeline" in loaded, "Artifact missing pipeline object"
    assert "feature_names" in loaded, "Artifact missing feature_names"
    assert "target_names" in loaded, "Artifact missing target_names"
    assert loaded["feature_names"] == FEATURE_NAMES
    assert loaded["target_names"] == TARGET_NAMES
    assert loaded["accuracy"] >= 0.85, "Trained model accuracy is below threshold"
