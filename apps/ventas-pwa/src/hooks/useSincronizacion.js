// AVAO — Tarea #38, HU-08 / HU-01
// Hook de sincronización: dispara syncPedidosPendientes() en los eventos
// naturales (montaje con red, evento 'online') y expone estado a la UI.
import { useCallback, useEffect, useRef, useState } from 'react'
import { useLiveQuery } from 'dexie-react-hooks'
import { db } from '../db/dexieDb'
import { hayConexion, syncPedidosPendientes } from '../services/syncService'

export function useSincronizacion() {
  // Badge en vivo: cuenta pedidos pendientes y re-renderiza al cambiar estadoSync.
  const pendientes = useLiveQuery(
    () => db.pedidos.where('estadoSync').equals('pendiente').count(),
    [],
    0,
  )
  const [sincronizando, setSincronizando] = useState(false)
  const [resultado, setResultado] = useState(null)
  const enCurso = useRef(false)

  const sincronizar = useCallback(async () => {
    if (enCurso.current) return // guardia por instancia (StrictMode dev)
    enCurso.current = true
    setSincronizando(true)
    try {
      setResultado(await syncPedidosPendientes())
    } finally {
      setSincronizando(false)
      enCurso.current = false
    }
  }, [])

  useEffect(() => {
    if (hayConexion()) sincronizar() // disparador 1: montaje (solo si ya hay red)
    const alRecuperarRed = () => sincronizar()
    window.addEventListener('online', alRecuperarRed) // disparador 2: recuperó red
    return () => window.removeEventListener('online', alRecuperarRed)
  }, [sincronizar])

  return { pendientes, sincronizando, resultado, sincronizar }
}
