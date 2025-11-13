# Car Resale Value Prediction — run instructions (Windows PowerShell)

This tiny README explains how to set up a Python virtual environment, install dependencies, and run `application.py` on Windows PowerShell.

1) Open PowerShell and change to the project directory:

```powershell
Set-Location 'C:\Users\gosai\OneDrive\projects\car_resale_value_prediction'
Get-ChildItem
```

2) Create and activate a virtual environment:

```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution you can either run the batch activator from cmd.exe:

```powershell
.\venv\Scripts\activate.bat
```

or temporarily allow script execution for this process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

3) Install dependencies from `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

4) Run the application:

```powershell
python .\application.py
```

5) Open a browser to http://127.0.0.1:5000/ and test the app.

Troubleshooting
- If you see `ModuleNotFoundError: No module named 'flask'`, ensure the virtualenv is activated and `pip install -r requirements.txt` completed without errors.
- If the server raises a `FileNotFoundError` about CSV files, ensure your CSV is in the project root and named one of the expected files (the app checks multiple candidates). The workspace shows `Cleaned Car.csv`, which is acceptable.
- If `/predict` returns an error text stating the model is missing, ensure a model pickle exists in the project root with one of these names: `LinearRegressionModel.pkl`, `linear_regression_model.pkl`, or `model.pkl`.

If you want, I can also create a minimal placeholder model (so you can test the UI without a trained model). Say "create placeholder model" and I'll add it.
