import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from docx import Document
from streamlit.testing.v1 import AppTest
import dokumenty
import eksport
from portfolio_data import new_state, save_document, KINDS

ROOT = Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def test_nested_state_is_independent(self):
        first, second = new_state(), new_state()
        first[0]["status"] = "wysłana"
        first[0]["documents"][KINDS[0]].append("moja korekta")
        self.assertEqual(second[0]["status"], "do wysłania")
        self.assertEqual(len(second[0]["documents"][KINDS[0]]), 1)

    def test_document_history_and_limits(self):
        offer = new_state()[0]
        original = offer["documents"][KINDS[0]][0]
        self.assertTrue(save_document(offer, KINDS[0], "Nowa treść"))
        self.assertEqual(offer["documents"][KINDS[0]][0], original)
        self.assertFalse(save_document(offer, KINDS[0], "Nowa treść"))
        for content in (" ", "x" * 20001):
            with self.assertRaises(ValueError):
                save_document(offer, KINDS[0], content)

    def test_docx_omits_notes_and_keeps_polish(self):
        content = "Zażółć gęślą jaźń\n" + dokumenty.NOTES_MARKER + "\nSEKRETNA NOTATKA"
        result = eksport.to_docx(content)
        text = "\n".join(p.text for p in Document(io.BytesIO(result)).paragraphs)
        self.assertIn("Zażółć gęślą jaźń", text)
        self.assertNotIn("SEKRETNA", text)

    def test_pdf_export(self):
        result = eksport.to_pdf("# Przykład\nZażółć gęślą jaźń", "Przykład")
        self.assertTrue(result.startswith(b"%PDF"))
        self.assertGreater(len(result), 1000)

    def test_imports_do_not_load_private_configuration(self):
        code = "import portfolio_data, portfolio_ui; import sys; assert not {'config','agent','db','dotenv','anthropic'} & set(sys.modules)"
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class InterfaceTests(unittest.TestCase):
    def app(self):
        at = AppTest.from_file(str(ROOT / "portfolio_app.py"), default_timeout=20).run()
        self.assertFalse(at.exception)
        return at

    def open_offer(self, at):
        at.button(key="open_1").click().run()
        self.assertFalse(at.exception)

    def test_filter_and_empty_state(self):
        at = self.app()
        at.text_input(key="search").set_value("nieistniejąca oferta").run()
        self.assertFalse(any(b.key == "open_1" for b in at.button))
        self.assertTrue(any("Brak ofert" in x.value for x in at.info))
        at.text_input(key="search").set_value("obsługi").run()
        self.assertEqual(len([b for b in at.button if b.label == "Zobacz ofertę"]), 1)

    def test_status_and_session_isolation(self):
        first, second = self.app(), self.app()
        self.open_offer(first)
        first.selectbox(key="stage_1").select("wysłana").run()
        self.assertEqual(first.session_state["offers"][0]["status"], "wysłana")
        self.assertEqual(second.session_state["offers"][0]["status"], "do wysłania")
        first.button(key="reset").click().run()
        self.assertEqual(first.session_state["offers"][0]["status"], "do wysłania")
        self.assertIsNone(first.session_state["selected_offer"])
        self.assertFalse(first.exception)

    def test_edit_document_and_notes(self):
        at = self.app()
        self.open_offer(at)
        at.segmented_control(key="section_1").set_value("Dokumenty").run()
        at.segmented_control(key="mode_1_CV pod ofertę").set_value("Edycja").run()
        at.text_area[0].set_value("# Anna Nowak\nPoprawiona treść przykładowa.")
        at.form_submit_button[0].click().run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.session_state["offers"][0]["documents"][KINDS[0]]), 2)
        at.segmented_control(key="section_1").set_value("Notatki").run()
        at.text_area(key="notes_text_1").set_value("Zapytaj o wdrożenie")
        at.form_submit_button[0].click().run()
        self.assertEqual(at.session_state["offers"][0]["notes"], "Zapytaj o wdrożenie")

    def test_all_pages_and_ai_environment(self):
        with patch.dict(os.environ, {"AI_WLACZONE": "1", "ANTHROPIC_API_KEY": "fake-test-value"}):
            at = self.app()
            for page in ("aplikacje", "profil", "poradnik"):
                at.switch_page(f"app_pages/{page}.py").run()
                self.assertFalse(at.exception)
            self.assertTrue(any("Poradnik" in t.value for t in at.title))


if __name__ == "__main__":
    unittest.main()
