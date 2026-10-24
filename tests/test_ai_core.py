import json
import unittest
from pathlib import Path

from src.ai.prompt_engine import build_proactive_prompt
from src.core.orchestrator import load_data


DATA_PATH = Path(__file__).parents[1] / "data" / "database.json"


class AiCoreTests(unittest.TestCase):
    def test_sample_data_loads_into_domain_models(self) -> None:
        patient, events = load_data(str(DATA_PATH))

        self.assertTrue(patient.name.strip())
        self.assertEqual(patient.age, 75)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].event_type, "medicine")

    def test_proactive_prompt_contains_patient_and_event_context(self) -> None:
        patient, events = load_data(str(DATA_PATH))

        prompt = build_proactive_prompt(patient, events[0])

        self.assertIn(patient.name, prompt)
        self.assertIn(patient.profession, prompt)
        self.assertIn(events[0].description, prompt)
        self.assertIn("Maximum 2 short sentences", prompt)

    def test_fixture_has_expected_top_level_schema(self) -> None:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(set(data), {"patient", "events"})
        self.assertTrue(
            all(
                {"time", "event_type", "description"} <= set(event)
                for event in data["events"]
            )
        )
