import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_command(command):
    print(f"\nExecutando: {' '.join(command)}")

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True
    )

def run_sql_file(sql_file_path):
    print(f"\nExecutando script SQL: {sql_file_path}")

    with (PROJECT_ROOT / sql_file_path).open(encoding="utf-8") as sql_file:
        subprocess.run([
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "dataforge",
            "-d",
            "ecommerce"
        ],
        cwd=PROJECT_ROOT,
        check=True,
        stdin=sql_file
        )

def main():
    run_command([sys.executable, "src/generate_raw_data.py"])
    run_command([sys.executable, "src/validate_raw_data.py"])
    run_command(["docker", "compose", "up", "-d"])
    run_sql_file("sql/01_create_tables.sql")
    run_command([sys.executable, "src/load_raw_data.py"])
    run_sql_file("sql/03_create_analytics_layer.sql")

if __name__ == "__main__":
    main()