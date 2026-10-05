-- AVAO — Seed de desarrollo para la API local (Tarea #38, HU-01/HU-08).
-- Ejecutar una sola vez con la BD levantada y migraciones aplicadas
-- (`alembic upgrade head`). Los UUIDs deben coincidir con
-- apps/ventas-pwa/src/constants/mapeoApi.js.
--
-- Nota de corrección vs PLAN-#38 §5.4:
--   * tipo 'espejo' NO es válido (ck_productos_tipo_valido solo admite
--     vidrio/aluminio/otro) → Espejo usa tipo 'otro'.
--   * espesor 0 viola ck_productos_espesor_positivo → Perfil aluminio
--     usa NULL (sin espesor de vidrio).

INSERT INTO clientes (id, nombre, telefono) VALUES
  ('a1b2c3d4-0000-4000-8000-000000000001', 'Vidriería López', '555-1234')
ON CONFLICT (id) DO NOTHING;

INSERT INTO productos (id, nombre, tipo, espesor_mm) VALUES
  ('a1b2c3d4-0000-4000-8000-000000000011', 'Vidrio claro 6mm', 'vidrio', 6),
  ('a1b2c3d4-0000-4000-8000-000000000012', 'Vidrio templado 10mm', 'vidrio', 10),
  ('a1b2c3d4-0000-4000-8000-000000000013', 'Vidrio esmerilado 4mm', 'vidrio', 4),
  ('a1b2c3d4-0000-4000-8000-000000000014', 'Perfil aluminio 2x1', 'aluminio', NULL),
  ('a1b2c3d4-0000-4000-8000-000000000015', 'Espejo 4mm', 'otro', 4)
ON CONFLICT (id) DO NOTHING;
