import os, subprocess, sys, tempfile, unittest
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
from fastapi import HTTPException
from apps.api.main import (NewOrder, InventoryUpdate, WasteSelection, CostUpdate, create_order, get_order, calculate_window_cost, calculate_combined_waste, select_combined_waste, update_inventory, update_cost)

class CombinedWasteTests(unittest.TestCase):
 def setUp(self):
  self.folder=tempfile.TemporaryDirectory(); self.env=patch.dict(os.environ, AVAO_DB_PATH=str(Path(self.folder.name)/'db.sqlite3')); self.env.start(); subprocess.run([sys.executable,'-m','apps.api.init_db'],check=True,capture_output=True)
  self.order=create_order(NewOrder(ventanas=[{'ancho':'48','alto':'36'}]))['id']; self.window=get_order(self.order)['ventanas'][0]['id']
 def tearDown(self): self.env.stop(); self.folder.cleanup()
 def test_total_selection_persistence_and_zero(self):
  update_inventory(InventoryUpdate(umbral_merma=1,umbral_merma_vidrio=1)); base=Decimal(calculate_window_cost(self.window)['precio']); order=calculate_combined_waste(self.order)
  charge=Decimal(order['merma']['cargo'])+Decimal(order['merma_vidrio']['cargo']); self.assertGreater(charge,0); self.assertEqual(Decimal(order['total_pedido']),base+charge)
  order=select_combined_waste(self.order,WasteSelection(incluida=False)); self.assertEqual(Decimal(order['total_pedido']),base); self.assertFalse(order['merma']['incluida']); self.assertFalse(order['merma_vidrio']['incluida'])
  order=calculate_combined_waste(self.order); self.assertFalse(order['merma']['incluida']); self.assertFalse(order['merma_vidrio']['incluida']); self.assertEqual(get_order(self.order)['merma'],order['merma'])
  order=select_combined_waste(self.order,WasteSelection(incluida=True)); self.assertEqual(Decimal(order['total_pedido']),base+charge)
  update_inventory(InventoryUpdate(umbral_merma=0,umbral_merma_vidrio=0)); order=calculate_combined_waste(self.order); self.assertEqual(order['merma']['cargo'],'0.00'); self.assertEqual(order['merma_vidrio']['cargo'],'0.00'); self.assertEqual(Decimal(order['total_pedido']),base)
 def test_rollback_calculation_and_selection(self):
  update_inventory(InventoryUpdate(umbral_merma=1,umbral_merma_vidrio=1)); before=calculate_combined_waste(self.order)
  with patch('apps.api.main.calcular_merma_vidrio', side_effect=HTTPException(status_code=422)), self.assertRaises(HTTPException): calculate_combined_waste(self.order)
  after=get_order(self.order); self.assertEqual(after['merma'],before['merma']); self.assertEqual(after['merma_vidrio'],before['merma_vidrio'])
  import sqlite3
  with sqlite3.connect(os.environ['AVAO_DB_PATH']) as db: db.execute('DELETE FROM merma_vidrio_pedido WHERE pedido_id=?',(self.order,))
  with self.assertRaises(HTTPException): select_combined_waste(self.order,WasteSelection(incluida=False))
  self.assertTrue(get_order(self.order)['merma']['incluida'])
if __name__=='__main__': unittest.main()
