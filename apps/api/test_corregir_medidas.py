"""Corrección de medidas después de iniciar cortes con una SQLite temporal."""

from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (
    AluminumMark, AssemblyMark, GlassMark, NewOrder, OrderWindowCorrection, WindowCorrection,
    correct_order_window_measures, correct_window_measures, create_order, get_order, mark_aluminum,
    mark_assembly, mark_glass,
)


class CorrectWindowMeasuresTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "corrections.sqlite3"
        environment = patch.dict(os.environ, AVAO_DB_PATH=str(self.path))
        environment.start()
        self.addCleanup(environment.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)

    def create_order(self, windows=None):
        return create_order(NewOrder(ventanas=windows or [
            {"ancho": "48", "alto": "36"},
            {"ancho": "50", "alto": "38"},
        ]))["id"]

    def finish_cuts(self, window):
        for cut in window["avance_aluminio"]:
            for _ in range(cut["pendientes"]):
                mark_aluminum(window["id"], cut["orden"], AluminumMark(accion="marcar"))
        for _ in range(window["avance_vidrio"]["pendientes"]):
            mark_glass(window["id"], GlassMark(accion="marcar"))

    def test_correction_recalculates_and_preserves_only_unchanged_piece_marks(self):
        order_id = self.create_order()
        first, second = get_order(order_id)["ventanas"]
        mark_aluminum(first["id"], 1, AluminumMark(accion="marcar"))  # Jamba changes with height.
        mark_aluminum(first["id"], 5, AluminumMark(accion="marcar"))  # Horizontal fijo keeps its length.
        mark_glass(first["id"], GlassMark(accion="marcar"))

        result = correct_window_measures(
            first["id"],
            WindowCorrection(ancho="48", alto="37", confirmar_correccion=True),
        )

        self.assertEqual(result["marcas_aluminio_conservadas"], 1)
        self.assertEqual(result["marcas_vidrio_conservadas"], 0)
        self.assertEqual(result["marcas_retiradas"], 2)
        updated, unchanged = get_order(order_id)["ventanas"]
        self.assertEqual((updated["id"], updated["numero"], updated["codigo"]),
                         (first["id"], 1, "A1"))
        self.assertEqual((updated["ancho"], updated["alto"]), ("48", "37"))
        self.assertEqual(updated["plan_aluminio"][0]["longitud"], "37")
        self.assertEqual(updated["avance_aluminio"][0]["cortadas"], 0)
        self.assertEqual(updated["avance_aluminio"][4]["cortadas"], 1)
        self.assertEqual(updated["plan_vidrio"]["alto"], "35")
        self.assertEqual(updated["avance_vidrio"]["cortadas"], 0)
        self.assertEqual((unchanged["id"], unchanged["numero"], unchanged["codigo"]),
                         (second["id"], 2, "A2"))
        self.assertEqual((unchanged["ancho"], unchanged["alto"]), ("50", "38"))
        self.assertTrue(all(cut["cortadas"] == 0 for cut in unchanged["avance_aluminio"]))

    def test_correction_clears_assembly_and_keeps_valid_marks(self):
        order_id = self.create_order([{"ancho": "48", "alto": "36"}])
        window = get_order(order_id)["ventanas"][0]
        self.finish_cuts(window)
        mark_assembly(window["id"], AssemblyMark(accion="marcar"))

        result = correct_window_measures(
            window["id"],
            WindowCorrection(ancho="48", alto="37", confirmar_correccion=True),
        )

        updated = get_order(order_id)["ventanas"][0]
        self.assertTrue(result["ensamble_reiniciado"])
        self.assertFalse(updated["ensamblada"])
        self.assertEqual(updated["codigo"], "A1")
        self.assertEqual(updated["avance_aluminio"][0]["cortadas"], 0)
        self.assertEqual(updated["avance_aluminio"][4]["cortadas"], 2)
        self.assertEqual(updated["avance_vidrio"]["cortadas"], 0)

    def test_confirmation_is_required_and_rejection_keeps_database_unchanged(self):
        order_id = self.create_order([{"ancho": "48", "alto": "36"}])
        window = get_order(order_id)["ventanas"][0]
        mark_aluminum(window["id"], 1, AluminumMark(accion="marcar"))

        with self.assertRaises(HTTPException) as error:
            correct_window_measures(
                window["id"], WindowCorrection(ancho="48", alto="37"),
            )
        self.assertEqual(error.exception.status_code, 409)
        unchanged = get_order(order_id)["ventanas"][0]
        self.assertEqual((unchanged["ancho"], unchanged["alto"]), ("48", "36"))
        self.assertEqual(unchanged["avance_aluminio"][0]["cortadas"], 1)

    def test_correction_before_any_cut_recalculates_plan_and_keeps_code(self):
        order_id = self.create_order([{"ancho": "48", "alto": "36"}])
        window = get_order(order_id)["ventanas"][0]

        result = correct_window_measures(
            window["id"],
            WindowCorrection(ancho="48", alto="37", confirmar_correccion=True),
        )
        updated = get_order(order_id)["ventanas"][0]
        self.assertEqual((updated["ancho"], updated["alto"], updated["codigo"]), ("48", "37", "A1"))
        self.assertEqual(updated["plan_aluminio"][0]["longitud"], "37")
        self.assertEqual(result["marcas_retiradas"], 0)

    def test_invalid_plan_does_not_change_measurements_or_progress(self):
        order_id = self.create_order([{"ancho": "48", "alto": "36"}])
        window = get_order(order_id)["ventanas"][0]
        mark_aluminum(window["id"], 5, AluminumMark(accion="marcar"))

        with self.assertRaises(HTTPException) as error:
            correct_window_measures(
                window["id"],
                WindowCorrection(ancho="1", alto="1", confirmar_correccion=True),
            )
        self.assertEqual(error.exception.status_code, 422)
        unchanged = get_order(order_id)["ventanas"][0]
        self.assertEqual((unchanged["ancho"], unchanged["alto"]), ("48", "36"))
        self.assertEqual(unchanged["avance_aluminio"][4]["cortadas"], 1)

    def test_incomplete_saved_plan_is_rejected_without_losing_state(self):
        order_id = self.create_order([{"ancho": "48", "alto": "36"}])
        window = get_order(order_id)["ventanas"][0]
        mark_aluminum(window["id"], 5, AluminumMark(accion="marcar"))
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute(
                "DELETE FROM plan_aluminio WHERE ventana_id = ? AND orden = 10", (window["id"],)
            )
            connection.commit()

        with self.assertRaises(HTTPException) as error:
            correct_window_measures(
                window["id"],
                WindowCorrection(ancho="48", alto="37", confirmar_correccion=True),
            )
        self.assertEqual(error.exception.status_code, 409)
        with closing(sqlite3.connect(self.path)) as connection:
            persisted = connection.execute(
                "SELECT ancho_16, alto_16 FROM ventanas WHERE id = ?", (window["id"],)
            ).fetchone()
        self.assertEqual(persisted, (768, 576))

    def test_order_correction_updates_multiple_windows_in_one_operation(self):
        order_id = self.create_order()
        first, second = get_order(order_id)["ventanas"]
        mark_aluminum(first["id"], 1, AluminumMark(accion="marcar"))

        result = correct_order_window_measures(
            order_id,
            OrderWindowCorrection(ventanas=[
                {"id": first["id"], "ancho": "48", "alto": "37"},
                {"id": second["id"], "ancho": "51", "alto": "38"},
            ], confirmar_correccion=True),
        )

        self.assertEqual([item["id"] for item in result["resultados"]], [first["id"], second["id"]])
        updated = get_order(order_id)["ventanas"]
        self.assertEqual((updated[0]["ancho"], updated[0]["alto"]), ("48", "37"))
        self.assertEqual((updated[1]["ancho"], updated[1]["alto"]), ("51", "38"))
        self.assertEqual([window["codigo"] for window in updated], ["A1", "A2"])

    def test_order_correction_rolls_back_all_windows_if_one_measure_is_invalid(self):
        order_id = self.create_order()
        first, second = get_order(order_id)["ventanas"]
        mark_aluminum(first["id"], 1, AluminumMark(accion="marcar"))
        mark_aluminum(second["id"], 1, AluminumMark(accion="marcar"))

        with self.assertRaises(HTTPException) as error:
            correct_order_window_measures(
                order_id,
                OrderWindowCorrection(ventanas=[
                    {"id": first["id"], "ancho": "48", "alto": "37"},
                    {"id": second["id"], "ancho": "inválido", "alto": "38"},
                ], confirmar_correccion=True),
            )

        self.assertEqual(error.exception.status_code, 422)
        unchanged = get_order(order_id)["ventanas"]
        self.assertEqual([(window["ancho"], window["alto"]) for window in unchanged], [
            ("48", "36"), ("50", "38"),
        ])
        self.assertEqual([window["avance_aluminio"][0]["cortadas"] for window in unchanged], [1, 1])


if __name__ == "__main__":
    unittest.main()
