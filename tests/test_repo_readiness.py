from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TestRepoReadiness(unittest.TestCase):
    def test_readme_exists(self):
        self.assertTrue((ROOT / 'README.md').exists() or (ROOT / 'README.MD').exists())

    def test_no_invalid_workflow_extension(self):
        workflows = ROOT / '.github' / 'workflows'
        if workflows.exists():
            self.assertEqual(sorted(p.name for p in workflows.glob('*.ym')), [])

if __name__ == '__main__':
    unittest.main()
