"""Create a minimal dummy model pickle for quick testing.

This script writes `LinearRegressionModel.pkl` containing an object
with a `predict(X)` method that returns a constant value. Run this
inside your virtualenv to create a model compatible with the current
scikit-learn / Python environment. The dummy model ignores input and
is only for UI/flow testing.
"""
import pickle


class DummyModel:
    def predict(self, X):
        # return a 1-D numpy-like array with one prediction
        try:
            import numpy as _np
            return _np.array([50000.0])
        except Exception:
            return [50000.0]


if __name__ == '__main__':
    with open('LinearRegressionModel.pkl', 'wb') as f:
        pickle.dump(DummyModel(), f)
    print('Wrote LinearRegressionModel.pkl (dummy model)')
