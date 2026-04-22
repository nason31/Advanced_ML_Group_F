"""Download the M5 Forecasting dataset from Kaggle to data/raw/."""
import subprocess
from pathlib import Path

DEST = Path("data/raw")
DEST.mkdir(parents=True, exist_ok=True)

subprocess.run(
    ["kaggle", "competitions", "download", "-c", "m5-forecasting-accuracy", "-p", str(DEST)],
    check=True,
)
subprocess.run(
    ["unzip", "-o", str(DEST / "m5-forecasting-accuracy.zip"), "-d", str(DEST)],
    check=True,
)
print(f"M5 data downloaded to {DEST}/")
