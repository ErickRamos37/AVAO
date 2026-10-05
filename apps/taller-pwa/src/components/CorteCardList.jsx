// AVAO — Tarea #30, HU-02
// Lista de tarjetas de cortes pendientes.
import CorteCard from './CorteCard'

export default function CorteCardList({ tareas }) {
  return (
    <ul style={{ listStyle: 'none', padding: 0 }}>
      {tareas.map((t) => (
        <li key={t.pieza_id}>
          <CorteCard tarea={t} />
        </li>
      ))}
    </ul>
  )
}
