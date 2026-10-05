// AVAO — Tarea #30, HU-02
// Página principal del Taller: lista de piezas pendientes de corte.
import { useEffect, useState } from 'react'
import { getTareasPendientes } from '../services/tareasApi'
import CorteCardList from '../components/CorteCardList'

export default function TallerPage() {
  const [tareas, setTareas] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let activo = true
    getTareasPendientes()
      .then((data) => {
        if (activo) {
          setTareas(Array.isArray(data) ? data : [])
          setLoading(false)
        }
      })
      .catch((err) => {
        if (activo) {
          setError(err?.message || 'Error de red')
          setLoading(false)
        }
      })
    return () => {
      activo = false
    }
  }, [])

  return (
    <main>
      <h1>Cortes pendientes</h1>
      {loading && <p>Cargando...</p>}
      {error && <p role="alert">Error al cargar cortes: {error}</p>}
      {!loading && !error && tareas.length === 0 && (
        <p>No hay cortes pendientes hoy</p>
      )}
      {!loading && !error && tareas.length > 0 && <CorteCardList tareas={tareas} />}
    </main>
  )
}
