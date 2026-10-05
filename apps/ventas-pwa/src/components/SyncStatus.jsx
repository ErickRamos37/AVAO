// AVAO — Tarea #38, HU-08 / HU-01
// Indicador de sincronización en la barra de navegación: badge con cantidad de
// pedidos pendientes (live query), botón manual y mensaje de resultado.
import { useSincronizacion } from '../hooks/useSincronizacion'

export default function SyncStatus() {
  const { pendientes, sincronizando, resultado, sincronizar } = useSincronizacion()
  return (
    <div data-testid="sync-status" aria-label="Estado de sincronización">
      <span data-testid="sync-pendientes" data-pendientes={pendientes}>
        {pendientes > 0 ? `⏳ ${pendientes} pendiente(s) de sincronizar` : '✓ sincronizado'}
      </span>
      <button type="button" onClick={sincronizar} disabled={sincronizando || pendientes === 0}>
        {sincronizando ? 'Sincronizando…' : 'Sincronizar'}
      </button>
      {resultado?.mensaje && <p role="status">{resultado.mensaje}</p>}
    </div>
  )
}
