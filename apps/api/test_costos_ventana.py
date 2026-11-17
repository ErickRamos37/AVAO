"""Pruebas de costo exacto de materiales por ventana (HU-11)."""

from decimal import Decimal
import unittest

from apps.api.costos_insumos import INSUMOS
from apps.api.costos_ventana import calculate_window_material_cost
from apps.api.plan_aluminio import calcular_plan_aluminio
from apps.api.plan_vidrio import calcular_plan_vidrio


def example_inputs():
    aluminum = [
        {"perfil": name, "longitud_16": length, "cantidad": quantity}
        for name, length, quantity in calcular_plan_aluminio(48 * 16, 36 * 16)
    ]
    glass_width, glass_height, glass_quantity = calcular_plan_vidrio(48 * 16, 36 * 16)
    glass = {
        "ancho_16": glass_width,
        "alto_16": glass_height,
        "cantidad": glass_quantity,
    }
    costs = {item[0]: item[6] for item in INSUMOS}
    costs["tela_mosquitera"] = 1500
    costs["vinil_doble_fuerza"] = 150
    return aluminum, glass, costs


class WindowMaterialCostTests(unittest.TestCase):
    def test_missing_any_required_cost_returns_no_partial_amounts(self):
        aluminum, glass, costs = example_inputs()
        costs["tela_mosquitera"] = None
        costs["vinil_doble_fuerza"] = None
        result = calculate_window_material_cost(aluminum, glass, costs)

        self.assertFalse(result["completo"])
        self.assertIn("Tela mosquitera", result["faltantes"])
        self.assertIn("Vinil doble fuerza", result["faltantes"])
        self.assertNotIn("items", result)
        self.assertNotIn("costo_base", result)

    def test_complete_calculation_uses_purchase_costs_and_exact_quantities(self):
        aluminum, glass, costs = example_inputs()
        result = calculate_window_material_cost(aluminum, glass, costs)

        self.assertTrue(result["completo"])
        items = {item["codigo"]: item for item in result["items"]}
        jamba_items = [item for item in result["items"] if item["codigo"] == "jamba"]
        # Two 36-inch jambs use six linear feet; $428 / 21 ft is not rounded first.
        self.assertEqual(jamba_items[0]["cantidad"], "6")
        # $428 / 21 ft is kept unrounded for the calculation, then shown to cents.
        self.assertEqual(Decimal(jamba_items[0]["costo"]), Decimal("122.29"))
        self.assertEqual(items["pasta"]["cantidad"], "1.5")
        self.assertEqual(Decimal(items["pasta"]["costo"]), Decimal("70.50"))
        self.assertEqual(items["chilillos"]["cantidad"], "24")
        self.assertEqual(Decimal(items["chilillos"]["costo"]), Decimal("4.80"))
        self.assertEqual(items["vidrio_doble_fuerza"]["unidad"], "pie cuadrado")
        self.assertEqual(items["tela_mosquitera"]["unidad"], "pie cuadrado")
        self.assertEqual(items["vinil_doble_fuerza"]["unidad"], "pie lineal")
        self.assertTrue(Decimal(result["costo_base"]) > 0)

    def test_incomplete_cut_plan_does_not_attempt_costing(self):
        aluminum, glass, costs = example_inputs()
        result = calculate_window_material_cost(aluminum[:-1], glass, costs)

        self.assertFalse(result["completo"])
        self.assertEqual(result["faltantes"], ["Plan de corte completo"])
        self.assertNotIn("costo_base", result)


if __name__ == "__main__":
    unittest.main()
