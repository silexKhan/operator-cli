import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from operator_cli.core.models.context import ContextManager


class ContextManagerTest(unittest.TestCase):
    def test_corrupt_context_is_backed_up_and_replaced_with_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            context_path = Path(temp_dir) / ".operator_context.json"
            context_path.write_text("{broken json", encoding="utf-8")

            manager = ContextManager(context_path=str(context_path))

            self.assertIsNone(manager.get_active_circuit())
            self.assertEqual(manager.get_history(), [])
            backups = list(Path(temp_dir).glob(".operator_context.json.bak.*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "{broken json")

    def test_save_context_writes_schema_and_history_atomically(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            context_path = Path(temp_dir) / ".operator_context.json"
            manager = ContextManager(context_path=str(context_path))

            manager.save_context(
                active_circuit="matrix",
                history=[{"role": "user", "content": "hello"}],
            )

            data = json.loads(context_path.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 1)
            self.assertEqual(data["active_circuit"], "matrix")
            self.assertEqual(data["history"], [{"role": "user", "content": "hello"}])
            self.assertEqual(list(Path(temp_dir).glob("*.tmp")), [])

    def test_mutable_defaults_are_independent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = ContextManager(context_path=str(Path(temp_dir) / "first.json"))
            second = ContextManager(context_path=str(Path(temp_dir) / "second.json"))

            first.context.history.append({"role": "user", "content": "first"})
            first.context.compressed_protocols["matrix"] = "compressed"

            self.assertEqual(second.context.history, [])
            self.assertEqual(second.context.compressed_protocols, {})


if __name__ == "__main__":
    unittest.main()
