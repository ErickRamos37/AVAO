// AVAO — Tarea #28, HU-01
// Validación del formulario de captura de pedido antes de persistir en Dexie.
export function validarPedido({ clienteNombre, piezas }) {
  const errores = { cliente: '', piezas: [], general: '' }
  if (!clienteNombre || !clienteNombre.trim()) {
    errores.cliente = 'El nombre del cliente es obligatorio'
  }
  if (!piezas || piezas.length === 0) {
    errores.general = 'Agrega al menos una pieza'
  }
  errores.piezas = (piezas || []).map((p) => {
    let msg = ''
    if (!p.productoId) msg = 'Selecciona un producto del catálogo'
    if (!(Number(p.ancho_mm) > 0)) msg = msg || 'La medida debe ser mayor que 0'
    if (!(Number(p.largo_mm) > 0)) msg = msg || 'La medida debe ser mayor que 0'
    if (!(Number.isInteger(Number(p.cantidad)) && Number(p.cantidad) > 0))
      msg = msg || 'La cantidad debe ser mayor que 0'
    return msg
  })
  const valido = !errores.cliente && !errores.general && errores.piezas.every((e) => !e)
  return { errores, valido }
}
