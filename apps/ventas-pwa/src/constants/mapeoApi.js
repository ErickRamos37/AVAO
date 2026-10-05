// AVAO — Tarea #38, HU-08 / HU-01
// Mapeo local (nombres/ids semánticos) → UUIDs de la API.
// Los UUID corresponden al seed manual de PLAN-#38 §5.4 (clientes/productos).
// Es un directorio manual provisional hasta que existan GET /clientes y
// GET /productos (HU de catálogo): entonces este archivo se reemplaza por un
// caché poblado desde la API.
export const CLIENTES_POR_NOMBRE = {
  // clave = nombre.trim().toLowerCase() → UUID de clientes.id
  'vidriería lópez': 'a1b2c3d4-0000-4000-8000-000000000001',
}

export const PRODUCTOS_POR_ID_LOCAL = {
  // id local (catalogoProductos.js) → UUID de productos.id
  'vidrio-claro-6': 'a1b2c3d4-0000-4000-8000-000000000011',
  'vidrio-templado-10': 'a1b2c3d4-0000-4000-8000-000000000012',
  'vidrio-esmerilado-4': 'a1b2c3d4-0000-4000-8000-000000000013',
  'aluminio-perfil-2x1': 'a1b2c3d4-0000-4000-8000-000000000014',
  'otro-espejo-4': 'a1b2c3d4-0000-4000-8000-000000000015',
}

/** Resuelve UUID de cliente por nombre (normalizado). Lanza si no existe mapeo. */
export function resolverClienteId(clienteNombre) {
  const clave = (clienteNombre || '').trim().toLowerCase()
  const id = CLIENTES_POR_NOMBRE[clave]
  if (!id) {
    throw new Error(`Cliente sin UUID de API: "${clienteNombre}" (registrar cliente primero)`)
  }
  return id
}

/** Resuelve UUID de producto por id local. Lanza si no existe mapeo. */
export function resolverProductoId(idLocal) {
  const id = PRODUCTOS_POR_ID_LOCAL[idLocal]
  if (!id) {
    throw new Error(`Producto sin UUID de API: "${idLocal}"`)
  }
  return id
}
