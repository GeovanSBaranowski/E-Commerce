import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INCOMING_DIR = PROJECT_ROOT / "data" / "incoming"

def main():
    csv_files = sorted(INCOMING_DIR.glob("orders_*.csv"))

    if not csv_files:
        print("Nenhum lote incremental encontrado")
        return

    for csv_path in csv_files:
        print(f"Carregando lote: {csv_path.name}", flush=True)

        subprocess.run(
            [sys.executable, "src/load_incoming_orders.py", str(csv_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )

        subprocess.run(
            [sys.executable, "src/validate_incoming_loaded.py", str(csv_path)],
            cwd=PROJECT_ROOT,
            check=True
        )

if __name__ == "__main__":
    main()