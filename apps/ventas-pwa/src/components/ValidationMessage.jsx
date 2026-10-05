// AVAO — Tarea #28, HU-01
// Mensaje de error inline para validaciones de formulario.
export default function ValidationMessage({ message }) {
  if (!message) return null
  return (
    <p role="alert" style={{ color: '#c00', margin: '4px 0' }}>
      {message}
    </p>
  )
}
