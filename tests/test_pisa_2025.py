import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PISA2025ConfigurationTests(unittest.TestCase):
    def test_oecd_downloads_are_configured(self):
        downloader = load_module(
            "pisa_download_from_oecd",
            "Global/pisa/pipelines/download_from_oecd.py",
        )
        config = downloader.PISA_CONFIG[2025]

        self.assertEqual(config["format"], "compressed")
        self.assertEqual(
            config["url_pattern"],
            "https://webfs.oecd.org/pisa2022/2025/{filename}",
        )
        self.assertEqual(
            set(config["files"]),
            {
                "student_questionnaire",
                "school_questionnaire",
                "teacher_questionnaire",
                "cognitive_item",
                "cognitive_process",
                "questionnaire_timing",
            },
        )

    def test_harmonizer_detects_2025_student_and_cognitive_files(self):
        harmonizer = load_module(
            "pisa_harmonize_trends",
            "Global/pisa/pipelines/harmonize_trends.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            year = raw / "2025"
            (year / "student_questionnaire").mkdir(parents=True)
            (year / "cognitive_item").mkdir()
            student = year / "student_questionnaire" / "CY09_MS_STU_PUF.sav"
            cognitive = year / "cognitive_item" / "CY09_MS_COG_PUF.sav"
            student.touch()
            cognitive.touch()

            converter = harmonizer.PISATrendConverter(
                raw_dir=str(raw), processed_dir=str(Path(tmp) / "processed")
            )
            found = converter.find_year_files(2025)

            self.assertEqual(found["student"], student)
            self.assertEqual(found["cognitive"], cognitive)

    def test_default_data_paths_do_not_depend_on_current_directory(self):
        downloader = load_module(
            "pisa_download_paths",
            "Global/pisa/pipelines/download_from_oecd.py",
        )
        harmonizer = load_module(
            "pisa_harmonize_paths",
            "Global/pisa/pipelines/harmonize_trends.py",
        )

        self.assertEqual(
            downloader.DEFAULT_PISA_DATA_DIR,
            REPO_ROOT / "data" / "Global" / "pisa",
        )
        converter = harmonizer.PISATrendConverter()
        self.assertEqual(
            converter.raw_dir,
            REPO_ROOT / "data" / "Global" / "pisa" / "raw",
        )

    def test_cycle_merge_uses_country_school_and_student_identity(self):
        import polars as pl

        merger = load_module(
            "pisa_merge_trend_cycles",
            "Global/pisa/pipelines/merge_trend_cycles.py",
        )
        frame = pl.DataFrame(
            {
                "pisa_year": [2009, 2009, 2009],
                "country": ["ESP", "ESP", "ESP"],
                "school_id": ["A", "A", "B"],
                "student_id": ["1", "1", "1"],
                "math_score": [500.0, 500.0, 475.0],
            }
        )

        result, removed = merger.deduplicate_students(frame)

        self.assertEqual(result.height, 2)
        self.assertEqual(removed, 1)


if __name__ == "__main__":
    unittest.main()
