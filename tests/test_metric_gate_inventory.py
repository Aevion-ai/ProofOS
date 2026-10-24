import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "metric_gate", Path(__file__).parents[1] / "scripts" / "metric_gate.py"
)
metric_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metric_gate)


class LeanInventoryTests(unittest.TestCase):
    def make_repo(self, root):
        (root / "lean").mkdir()
        (root / "lakefile.toml").write_text(
            'roots = ["LeishmanBerger", "CapabilityAccessSeparation"]\n',
            encoding="utf-8",
        )

    def add_lean(self, root, rel, body):
        path = root / "lean" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")

    def test_recursive_inventory_classifies_nested_sbir_scaffolding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            self.add_lean(root, "LeishmanBerger.lean", "theorem proved : True := by\n  trivial\n")
            self.add_lean(root, "CapabilityAccessSeparation.lean", "theorem access : True := by\n  sorry\n")
            self.add_lean(root, "Aevion/SBIR/SafetyTheorems.lean", "theorem nested : True := by\n  sorry\n")
            self.add_lean(root, "Aevion/SBIR/ProofCertificate.lean", "def certificate := 1\n")
            inv = metric_gate.lean_inventory(root)
            self.assertEqual(4, inv["files"])
            self.assertEqual(3, inv["theorems"])
            self.assertEqual(2, inv["sorries"])
            self.assertEqual(2, inv["research_scaffolding_files"])
            classes = {e["path"]: e["classification"] for e in inv["entries"]}
            self.assertEqual("research_scaffolding", classes["Aevion/SBIR/SafetyTheorems.lean"])
            self.assertEqual("default_target", classes["LeishmanBerger.lean"])

    def test_more_specific_sbir_classification_precedes_aevion_default_root(self):
        self.assertEqual(
            "research_scaffolding",
            metric_gate.classify_lean_file("Aevion/SBIR/SafetyTheorems.lean", ["Aevion"]),
        )

    def test_non_default_nested_source_is_not_mislabeled(self):
        self.assertEqual(
            "non_default_source",
            metric_gate.classify_lean_file("Research/Other.lean", ["ProofOS"]),
        )


if __name__ == "__main__":
    unittest.main()
