import logging
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)

def log_process_output(process):
    stderr_logger = logger.info if process.returncode == 0 else logger.error

    if process.stdout:
        for line in process.stdout.splitlines():
            if line.strip():
                logger.info("%s", line)

    if process.stderr:
        for line in process.stderr.splitlines():
            if line.strip():
                stderr_logger("%s", line)

def run_command(command):
    logger.info("Executando: %s", " ".join(command))

    result = subprocess.run(
        command,
        check=False,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    log_process_output(result)
    result.check_returncode()

def run_sql_file(sql_file_path):
    logger.info("Executando script SQL: %s", sql_file_path)

    with (PROJECT_ROOT / sql_file_path).open(encoding="utf-8") as sql_file:
        result = subprocess.run([
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
        stdin=sql_file,
        capture_output=True,
        text=True
        )

    log_process_output(result)
    result.check_returncode()

def main():
    logger.info("Pipeline iniciada")

    try:
        run_command([sys.executable, "src/generate_raw_data.py"])
        run_command([sys.executable, "src/validate_raw_data.py"])
        run_command(["docker", "compose", "up", "-d"])
        run_sql_file("sql/01_create_tables.sql")
        run_command([sys.executable, "src/load_raw_data.py"])
        run_sql_file("sql/03_create_analytics_layer.sql")

    except subprocess.CalledProcessError:
        logger.exception("Pipeline falhou")
        raise
    else:
        logger.info("Pipeline concluida com sucesso")

if __name__ == "__main__":
    main()