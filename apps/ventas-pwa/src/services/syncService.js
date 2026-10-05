// AVAO — Tarea #38, HU-08 / HU-01
// Servicio de sincronización offline→API: envía pedidos 'pendientes' a POST /pedidos.
// Módulo puro (sin React), testeable en aislamiento (patrón tareasApi.js del Taller).
import { db, getPiezasDePedido } from '../db/dexieDb'
import { resolverClienteId, resolverProductoId } from '../constants/mapeoApi'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/** Detecta conectividad. En tests se pisa via Object.defineProperty(navigator, 'onLine'). */
export function hayConexion() {
  return typeof navigator === 'undefined' || navigator.onLine !== false
}

/**
 * Mapea fila Dexie + piezas → body de PedidoCreate (apps/api/schemas.py).
 * Lanza si no resuelve cliente/producto (GAP A/B, §5.3 de PLAN-#38): el pedido
 * queda 'pendiente' con ultimoError y nunca se envía basura a la API.
 */
export function construirPayloadPedido(pedido, piezas) {
  return {
    cliente_id: resolverClienteId(pedido.clienteNombre), // UUID string
    fecha_entrega: pedido.fechaEntrega || null, // 'YYYY-MM-DD' del <input type=date>
    notas: combinarNotas(pedido), // notas + teléfono (GAP C, §5.2)
    piezas: piezas.map((p) => ({
      producto_id: resolverProductoId(p.productoId), // UUID string
      ancho_mm: Number(p.ancho_mm),
      largo_mm: Number(p.largo_mm),
      cantidad: Number(p.cantidad),
    })),
  }
}

/** GAP C (§5.2): PedidoCreate no tiene campo telefono → se pliega en notas. */
function combinarNotas(pedido) {
  const partes = []
  if (pedido.telefono) partes.push(`Tel: ${pedido.telefono}`)
  if (pedido.notas && pedido.notas.trim()) partes.push(pedido.notas.trim())
  return partes.length ? partes.join(' — ') : null
}

/** Marca un pedido como sincronizado (patch parcial de Dexie, §3.2). */
export async function marcarSincronizado(pedidoIdLocal) {
  await db.pedidos.update(pedidoIdLocal, { estadoSync: 'sincronizado', ultimoError: null })
}

let syncEnCurso = null // cerrojo a nivel de módulo (§3.3): evita doble envío

/**
 * Envía secuencialmente los pedidos con estadoSync 'pendiente' a POST /pedidos.
 * Al éxito (201) marca 'sincronizado'; al error mantiene 'pendiente' y escribe
 * ultimoError (la cola es a la vez el rollback, §2).
 * Retorna resumen { sincronizados, errores, erroresDetalle, mensaje } para la UI.
 */
export function syncPedidosPendientes() {
  if (!hayConexion()) {
    return Promise.resolve({
      sincronizados: 0,
      errores: 0,
      erroresDetalle: [],
      mensaje: 'Sin conexión: los pedidos siguen guardados localmente',
    })
  }
  if (syncEnCurso) return syncEnCurso.then(() => syncPedidosPendientes())
  syncEnCurso = ejecutarSync().finally(() => {
    syncEnCurso = null
  })
  return syncEnCurso
}

async function ejecutarSync() {
  const resumen = { sincronizados: 0, errores: 0, erroresDetalle: [], mensaje: '' }
  const pendientes = await db.pedidos.where('estadoSync').equals('pendiente').toArray()
  // SECUENCIAL (for..of con await, NO Promise.all): orden determinista, sin carreras.
  for (const pedido of pendientes) {
    try {
      const piezas = await getPiezasDePedido(pedido.idLocal)
      const payload = construirPayloadPedido(pedido, piezas)
      const resp = await fetch(`${API_URL}/pedidos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!resp.ok) throw new Error(`API respondió ${resp.status}`)
      await marcarSincronizado(pedido.idLocal)
      resumen.sincronizados++
    } catch (err) {
      // Mantiene 'pendiente' (checklist #38) y registra el mensaje.
      resumen.errores++
      resumen.erroresDetalle.push({ idLocal: pedido.idLocal, mensaje: err.message })
      await db.pedidos.update(pedido.idLocal, { ultimoError: err.message }).catch(() => {})
      console.warn(`[sync] pedido local ${pedido.idLocal} sigue pendiente:`, err.message)
    }
  }
  resumen.mensaje =
    resumen.sincronizados > 0
      ? `${resumen.sincronizados} pedido(s) sincronizado(s) con la API`
      : resumen.errores > 0
        ? `Error al sincronizar ${resumen.errores} pedido(s); se reintentará al recuperar la red`
        : 'No hay pedidos pendientes'
  return resumen
}
