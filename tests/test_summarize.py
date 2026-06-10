import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import typer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from operator_cli.commands.ops import summarize as summarize_module


class FakeLLM:
    generated_from = None

    def __init__(self, model):
        self.model = model

    def generate_summary(self, history):
        FakeLLM.generated_from = history
        return "## Goal\nUse real history."


class SummarizeCommandTest(unittest.TestCase):
    def test_summarize_uses_context_history_and_compacts_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            history = [
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "second"},
                {"role": "user", "content": "third"},
                {"role": "assistant", "content": "fourth"},
                {"role": "user", "content": "fifth"},
            ]
            (root / ".operator_context.json").write_text(
                json.dumps(
                    {
                        "active_circuit": "matrix",
                        "default_model": "test-model",
                        "history": history,
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(summarize_module, "get_project_root", return_value=root):
                with patch.object(summarize_module, "LocalLLM", FakeLLM):
                    summarize_module.summarize()

            self.assertEqual(FakeLLM.generated_from, history)
            memory_text = (root / "MEMORY.md").read_text(encoding="utf-8")
            self.assertIn("Use real history.", memory_text)
            self.assertIn("circuit=matrix", memory_text)

            context = json.loads((root / ".operator_context.json").read_text(encoding="utf-8"))
            self.assertEqual(context["history"][0]["role"], "system")
            self.assertIn("Use real history.", context["history"][0]["content"])
            self.assertEqual(context["history"][1:], history[-4:])

    def test_summarize_exits_cleanly_when_history_is_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".operator_context.json").write_text("{}", encoding="utf-8")

            with patch.object(summarize_module, "get_project_root", return_value=root):
                with self.assertRaises(typer.Exit) as raised:
                    summarize_module.summarize()

            self.assertEqual(raised.exception.exit_code, 0)
            self.assertFalse((root / "MEMORY.md").exists())


if __name__ == "__main__":
    unittest.main()
