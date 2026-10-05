// AVAO — Tarea #28, Subtarea 3, HU-01
// Base de datos local Dexie (IndexedDB), estrategia offline-first.
import Dexie from 'dexie'

export const db = new Dexie('avao-ventas')

db.version(1).stores({
  pedidos: '++idLocal, clienteNombre, fechaEntrega, estadoSync, createdAt',
  piezas: '++idLocal, pedidoIdLocal, productoId, ancho_mm, largo_mm, cantidad',
})

/**
 * Guarda un pedido con sus piezas en una transacción atómica.
 * Siempre persiste primero en local con estadoSync 'pendiente' (offline-first).
 */
export async function addPedido({ clienteNombre, telefono, notas, fechaEntrega, piezas }) {
  return db.transaction('rw', db.pedidos, db.piezas, async () => {
    const idLocal = await db.pedidos.add({
      clienteNombre,
      telefono: telefono || null,
      notas: notas || null,
      fechaEntrega: fechaEntrega || null,
      estadoSync: 'pendiente',
      createdAt: new Date().toISOString(),
    })
    await db.piezas.bulkAdd(
      piezas.map((p) => ({
        pedidoIdLocal: idLocal,
        productoId: p.productoId,
        ancho_mm: Number(p.ancho_mm),
        largo_mm: Number(p.largo_mm),
        cantidad: Number(p.cantidad),
      })),
    )
    return idLocal
  })
}

export async function getPiezasDePedido(pedidoIdLocal) {
  return db.piezas.where('pedidoIdLocal').equals(pedidoIdLocal).toArray()
}
