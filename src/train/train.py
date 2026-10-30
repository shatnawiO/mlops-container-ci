import os
from pathlib import Path
import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]

TARGET_NAMES = ["setosa", "versicolor", "virginica"]


def build_pipeline() -> Pipeline:
    """Build a deterministic scikit-learn classification pipeline."""
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=200,
                    random_state=42,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def train_model(test_size: float = 0.2, random_state: int = 42):
    """Load data, train pipeline, and return trained model and evaluation metrics."""
    iris = load_iris()
    X = iris.data
    y = iris.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    model_artifact = {
        "pipeline": pipeline,
        "feature_names": FEATURE_NAMES,
        "target_names": TARGET_NAMES,
        "accuracy": float(acc),
        "model_type": "LogisticRegression",
        "random_state": random_state,
    }
    return model_artifact


def save_model(model_artifact: dict, output_path: str = "models/model.joblib") -> str:
    """Save model dictionary to disk."""
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, dest)
    return str(dest)


def train_and_save(output_path: str = "models/model.joblib") -> dict:
    """Complete training and save pipeline."""
    model_artifact = train_model()
    saved_path = save_model(model_artifact, output_path)
    print(f"Model successfully trained with accuracy: {model_artifact['accuracy']:.4f}")
    print(f"Saved model artifact to: {saved_path}")
    return model_artifact


if __name__ == "__main__":
    output_file = os.getenv("MODEL_PATH", "models/model.joblib")
    train_and_save(output_path=output_file)
