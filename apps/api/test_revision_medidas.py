"""HU-38: revisar precios sin escribir y aplicar una sola decisión atómica."""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from apps.api.main import (BudgetPreview, BudgetSave, MeasureReview, MeasureReviewDecision,
                           get_order, preview_budget, save_budget, preview_measure_review,
                           confirm_measure_review, update_cost, CostUpdate)


class MeasureReviewTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, AVAO_DB_PATH=str(Path(folder.name) / "db.sqlite3"))
        env.start()
        self.addCleanup(env.stop)
        subprocess.run([sys.executable, "-m", "apps.api.init_db"], check=True, capture_output=True)
        data = {"ventanas": [{"ancho": "48", "alto": "36"}, {"ancho": "50", "alto": "38"}], "incluir_merma": True}
        preview = preview_budget(BudgetPreview(**data))
        self.order_id = save_budget(BudgetSave(**data, version=preview["version"],
                                          cliente={"nombre": "Ana", "apellido_1": "Pérez", "celular": "1234567890"}))["id"]

    def changes(self):
        return [{"id": get_order(self.order_id)["ventanas"][0]["id"], "ancho": "48", "alto": "37"}]

    def test_preview_is_pure_and_update_only_changes_edited_price(self):
        before = get_order(self.order_id)
        review = preview_measure_review(self.order_id, MeasureReview(ventanas=self.changes()))
        self.assertEqual(get_order(self.order_id), before)
        self.assertEqual(review["ventanas"][0]["anterior"]["precio"], int(before["ventanas"][0]["costo_materiales"]["precio"]))
        result = confirm_measure_review(self.order_id, MeasureReviewDecision(
            ventanas=self.changes(), version=review["version"], decision="actualizar"))
        after = get_order(self.order_id)
        self.assertEqual(result["resultados"][0]["alto"], "37")
        self.assertEqual(after["ventanas"][0]["costo_materiales"]["precio"], str(review["ventanas"][0]["nueva"]["precio"]))
        self.assertEqual(after["ventanas"][1], before["ventanas"][1])

    def test_conserve_price_and_reject_stale_preview(self):
        before = get_order(self.order_id)
        review = preview_measure_review(self.order_id, MeasureReview(ventanas=self.changes()))
        update_cost("jamba", CostUpdate(costo="600.00"))
        with self.assertRaises(HTTPException) as error:
            confirm_measure_review(self.order_id, MeasureReviewDecision(
                ventanas=self.changes(), version=review["version"], decision="actualizar"))
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(get_order(self.order_id), before)
        refreshed = preview_measure_review(self.order_id, MeasureReview(ventanas=self.changes()))
        confirm_measure_review(self.order_id, MeasureReviewDecision(
            ventanas=self.changes(), version=refreshed["version"], decision="conservar"))
        after = get_order(self.order_id)
        self.assertEqual(after["ventanas"][0]["costo_materiales"]["precio"], before["ventanas"][0]["costo_materiales"]["precio"])
        self.assertEqual(after["merma"]["cargo"], before["merma"]["cargo"])
        self.assertEqual(after["merma_vidrio"]["cargo"], before["merma_vidrio"]["cargo"])
        self.assertEqual(after["ventanas"][0]["costo_materiales"]["vigente"], True)

    def test_missing_current_cost_never_changes_measures(self):
        before = get_order(self.order_id)
        with sqlite3.connect(os.environ["AVAO_DB_PATH"]) as db:
            db.execute("UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo = 'jamba'")
        with self.assertRaises(HTTPException) as error:
            preview_measure_review(self.order_id, MeasureReview(ventanas=self.changes()))
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(get_order(self.order_id), before)

    def test_unified_preview_and_commit_update_client_transfer_and_date_atomically(self):
        before = get_order(self.order_id)
        change = MeasureReview(ventanas=[], cliente={"nombre": "Eva", "apellido_1": "López", "celular": "1234567890"},
                               traslado="25.00", fecha_programada="2026-12-01")
        preview = preview_measure_review(self.order_id, change)
        self.assertEqual(get_order(self.order_id), before)
        self.assertEqual(preview["total_nuevo"], int(before["total_pedido"]) + 25)
        saved = confirm_measure_review(self.order_id, MeasureReviewDecision(
            **change.model_dump(exclude_unset=True), version=preview["version"], decision="conservar"))
        after = get_order(self.order_id)
        self.assertEqual(saved["resultados"], [])
        self.assertEqual(after["cliente"]["nombre"], "Eva")
        self.assertEqual(after["traslado"], "25.00")
        self.assertEqual(after["fecha_programada"], "2026-12-01")

    def test_unified_change_rejects_invalid_client_without_partial_measure_update(self):
        before = get_order(self.order_id)
        with self.assertRaises(HTTPException):
            preview_measure_review(self.order_id, MeasureReview(
                ventanas=self.changes(), cliente={"nombre": "Ana1", "apellido_1": "Pérez", "celular": "1234567890"}))
        self.assertEqual(get_order(self.order_id), before)

    def test_unified_save_assigns_first_price_after_missing_cost_is_configured(self):
        with sqlite3.connect(os.environ["AVAO_DB_PATH"]) as db:
            db.execute("UPDATE costos_insumos SET costo_centavos = NULL WHERE codigo = 'jamba'")
        data = {"ventanas": [{"ancho": "48", "alto": "36"}], "incluir_merma": False}
        initial = preview_budget(BudgetPreview(**data))
        budget_id = save_budget(BudgetSave(**data, version=initial["version"],
            cliente={"nombre": "Luis", "apellido_1": "Pérez", "celular": "1234567890"}))["id"]
        self.assertIsNone(get_order(budget_id)["ventanas"][0]["costo_materiales"])
        update_cost("jamba", CostUpdate(costo="600.00"))
        review = MeasureReview(ventanas=[], actualizar_precios=True)
        preview = preview_measure_review(budget_id, review)
        self.assertIsNone(preview["ventanas"][0]["anterior"]["precio"])
        self.assertIsNone(get_order(budget_id)["total_pedido"])
        confirm_measure_review(budget_id, MeasureReviewDecision(
            ventanas=[], actualizar_precios=True, version=preview["version"], decision="actualizar"))
        self.assertIsNotNone(get_order(budget_id)["ventanas"][0]["costo_materiales"]["precio"])


if __name__ == "__main__":
    unittest.main()
