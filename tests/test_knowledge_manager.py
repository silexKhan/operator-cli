import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from operator_cli.core.knowledge.manager import KnowledgeManager, KnowledgeMetadata


class KnowledgeManagerTest(unittest.TestCase):
    def test_search_knowledge_uses_weighted_title_tags_and_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = KnowledgeManager(base_path=Path(temp_dir) / "knowledge")
            title_match = KnowledgeMetadata(
                id="K-TITLE",
                title="Matrix Routing",
                category="proposals",
                tags=["backend"],
            )
            tag_match = KnowledgeMetadata(
                id="K-TAG",
                title="Backend Notes",
                category="proposals",
                tags=["matrix"],
            )
            content_match = KnowledgeMetadata(
                id="K-CONTENT",
                title="General Notes",
                category="proposals",
                tags=["misc"],
            )

            manager.save_knowledge(title_match, "General backend note.")
            manager.save_knowledge(tag_match, "General backend note.")
            manager.save_knowledge(content_match, "This content mentions matrix once.")

            results = manager.search_knowledge("matrix")

            self.assertEqual([item["metadata"].id for item in results], ["K-TITLE", "K-TAG", "K-CONTENT"])
            self.assertGreater(results[0]["score"], results[1]["score"])
            self.assertGreater(results[1]["score"], results[2]["score"])

    def test_query_knowledge_keeps_legacy_tuple_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = KnowledgeManager(base_path=Path(temp_dir) / "knowledge")
            metadata = KnowledgeMetadata(
                id="K-LEGACY",
                title="Legacy Shape",
                category="proposals",
                tags=["shape"],
            )
            manager.save_knowledge(metadata, "Shape compatibility marker.")

            results = manager.query_knowledge("shape")

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][0].id, "K-LEGACY")
            self.assertIsInstance(results[0][1], str)

    def test_diagnose_can_run_without_creating_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "knowledge"
            manager = KnowledgeManager(base_path=base_path, ensure_directories=False)

            diagnostics = manager.diagnose()

            self.assertFalse(base_path.exists())
            self.assertTrue(any(item["status"] == "FAIL" for item in diagnostics))


if __name__ == "__main__":
    unittest.main()
