"""Comprueba guardado y reapertura sobre un archivo SQLite real."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class PersistenceTests(unittest.TestCase):
    def test_reopens_simplified_measure_in_a_new_process(self):
        with tempfile.TemporaryDirectory() as folder:
            env = dict(os.environ, AVAO_DB_PATH=str(Path(folder) / "avao.sqlite3"))

            def run(code: str) -> str:
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip()

            subprocess.run(
                [sys.executable, "-m", "apps.api.init_db"],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            order_id = int(run(
                "from apps.api.main import NewOrder, create_order; "
                "print(create_order(NewOrder(ancho='24 1/4 1/16', alto='26 1/2'))['id'])"
            ))
            opened = json.loads(run(
                "import json; from apps.api.main import get_order; "
                f"print(json.dumps(get_order({order_id})))"
            ))
            self.assertEqual(opened["ventanas"][0]["numero"], 1)
            self.assertEqual(opened["ventanas"][0]["ancho"], "24 5/16")
            self.assertEqual(opened["ventanas"][0]["alto"], "26 1/2")


if __name__ == "__main__":
    unittest.main()
