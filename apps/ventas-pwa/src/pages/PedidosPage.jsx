// AVAO — Tarea #28, HU-01
// Página /pedidos: lista pedidos guardados localmente con badge de estadoSync.
import { useLiveQuery } from 'dexie-react-hooks'
import { db } from '../db/dexieDb'

export default function PedidosPage() {
  const pedidos = useLiveQuery(() => db.pedidos.toArray(), [])

  return (
    <main>
      <h1>Pedidos</h1>
      {(!pedidos || pedidos.length === 0) && <p>No hay pedidos guardados.</p>}
      <ul>
        {pedidos?.map((p) => (
          <li key={p.idLocal}>
            <strong>{p.clienteNombre}</strong> — {p.fechaEntrega || 'sin fecha'}{' '}
            <span
              style={{
                background: p.estadoSync === 'pendiente' ? '#f5c542' : '#4caf50',
                padding: '2px 6px',
                borderRadius: '4px',
              }}
            >
              {p.estadoSync === 'pendiente' ? 'pendiente de sincronizar' : 'sincronizado'}
            </span>
          </li>
        ))}
      </ul>
    </main>
  )
}
