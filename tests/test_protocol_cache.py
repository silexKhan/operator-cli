import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from operator_cli.core.models.context import ContextManager
from operator_cli.core.protocol.engine import ProtocolEngine


class ProtocolCompressionCacheTest(unittest.TestCase):
    def test_compressed_protocol_cache_is_bound_to_source_hash_and_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            protocols_dir = root / "protocols"
            circuits_dir = protocols_dir / "circuits"
            units_dir = protocols_dir / "units"
            circuits_dir.mkdir(parents=True)
            units_dir.mkdir()
            (protocols_dir / "global.md").write_text("# Global\nRule A", encoding="utf-8")
            (circuits_dir / "matrix.md").write_text(
                "---\ndescription: Test circuit\n---\n# Matrix\nRule B",
                encoding="utf-8",
            )

            engine = ProtocolEngine(protocols_dir)
            context_manager = ContextManager(context_path=str(root / ".operator_context.json"))
            full_context = engine.get_full_context("matrix")
            source_hash = hashlib.sha256(full_context.encode("utf-8")).hexdigest()

            context_manager.set_compressed_protocol(
                "matrix",
                "cached compressed protocol",
                metadata={
                    "source_hash": source_hash,
                    "model": context_manager.get_default_model(),
                    "created_at": "2026-06-09T00:00:00+00:00",
                },
            )

            self.assertEqual(engine.get_full_context("matrix", context_manager), "cached compressed protocol")

            (protocols_dir / "global.md").write_text("# Global\nRule changed", encoding="utf-8")

            refreshed_context = engine.get_full_context("matrix", context_manager)
            self.assertNotEqual(refreshed_context, "cached compressed protocol")
            self.assertIn("Rule changed", refreshed_context)


if __name__ == "__main__":
    unittest.main()
