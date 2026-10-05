// AVAO — Tarea #30, HU-02
// Tarjeta de una pieza pendiente de corte (HU-02).

export default function CorteCard({ tarea }) {
  const { pieza_id, ancho_mm, largo_mm, cantidad, estado, operario_asignado, fecha } = tarea
  const fechaTexto = Number.isNaN(new Date(fecha).getTime())
    ? String(fecha)
    : new Date(fecha).toLocaleString()

  return (
    <article className="corte-card" data-testid="corte-card">
      <h2>Pieza {String(pieza_id).slice(0, 8)}…</h2>
      <p data-testid="corte-medidas">{`${ancho_mm} x ${largo_mm} mm`}</p>
      <p>Cantidad: {cantidad}</p>
      <p>
        Estado: <span data-testid="corte-estado">{estado}</span>
      </p>
      <p>Operario: {operario_asignado ?? 'Sin asignar'}</p>
      <p>Fecha: {fechaTexto}</p>
      {/* TODO #31: habilitar PATCH para marcar pieza como completada */}
      <button type="button" disabled>
        Marcar completado
      </button>
    </article>
  )
}
