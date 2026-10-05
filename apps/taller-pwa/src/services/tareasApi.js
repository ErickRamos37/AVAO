// AVAO — Tarea #30, HU-02
// Cliente HTTP del endpoint GET /tareas/pendientes (contrato fijado en #29).
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function getTareasPendientes() {
  const res = await fetch(`${API_URL}/tareas/pendientes`)
  if (!res.ok) {
    throw new Error(`Error al obtener tareas: ${res.status}`)
  }
  return res.json()
}
