"""The English and German blueprints must match the Polish source and the catalog."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import blueprint_i18n  # noqa: E402

BLUEPRINT = ROOT / "blueprints" / "automation" / "worx_vision_cloud_plus" / "smart_mowing_schedule.yaml"
CATALOG = ROOT / "i18n" / "smart_mowing_schedule.yaml"

SAMPLE = """\
blueprint:
  name: Harmonogram
  source_url: https://example.com/blueprints/sample.yaml
triggers:
  - trigger: time
    id: start
    at: "08:00:00"
actions:
  - alias: Zapisz termin
  - variables:
      label: >-
        {% if days == 1 %}jutro{% else %}{{ {0: 'dziś'}.get(days, 'później') }}{% endif %}
      code: "{{ 'docked' if x else 'mowing' }}"
"""


class TranslationsTests(unittest.TestCase):
    def test_generated_blueprints_match_source_and_catalog(self) -> None:
        problems = blueprint_i18n.check(BLUEPRINT, CATALOG)
        self.assertEqual(problems, [], "\n".join(problems[:30]))

    def test_every_translation_keeps_the_source_url_per_language(self) -> None:
        for lang in blueprint_i18n.LANGUAGES:
            text = blueprint_i18n.output_path(BLUEPRINT, lang).read_text(encoding="utf-8")
            self.assertIn(f"/smart_mowing_schedule_{lang}.yaml", text)


class CheckerTests(unittest.TestCase):
    """The checker itself must catch changes other than text."""

    def setUp(self) -> None:
        self.source = blueprint_i18n.load_yaml(SAMPLE)

    def _differences(self, translated: str) -> list[str]:
        return blueprint_i18n.structure_differences(self.source, blueprint_i18n.load_yaml(translated))

    def test_text_only_translation_passes(self) -> None:
        translated = (
            SAMPLE.replace("Harmonogram", "Schedule")
            .replace("Zapisz termin", "Save the time")
            .replace("jutro", "tomorrow")
            .replace("'dziś'", "'today'")
            .replace("'później'", "'later'")
        )
        self.assertEqual(self._differences(translated), [])

    def test_changed_trigger_id_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("id: start", "id: begin")))

    def test_changed_template_logic_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("days == 1", "days == 2")))

    def test_changed_state_literal_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("'docked'", "'angedockt'")))

    def test_segments_skip_logic_and_codes(self) -> None:
        texts = [segment.text for segment in blueprint_i18n.segments(SAMPLE)]
        self.assertIn("Zapisz termin", texts)
        self.assertTrue(any("jutro" in text for text in texts))
        self.assertFalse(any("docked" in text for text in texts))
        self.assertFalse(any(text.startswith("id:") for text in texts))


if __name__ == "__main__":
    unittest.main()
