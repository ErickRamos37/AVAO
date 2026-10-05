// AVAO — Tarea #28, HU-01
// Campos del cliente y datos del pedido.
import ValidationMessage from './ValidationMessage'

export default function ClienteFields({ clienteNombre, telefono, notas, fechaEntrega, error, onChange }) {
  return (
    <fieldset>
      <legend>Datos del cliente</legend>
      <label>
        Nombre del cliente *
        <input
          type="text"
          name="clienteNombre"
          value={clienteNombre}
          onChange={onChange}
        />
      </label>
      <ValidationMessage message={error} />
      <label>
        Teléfono
        <input type="tel" name="telefono" value={telefono} onChange={onChange} />
      </label>
      <label>
        Notas
        <textarea name="notas" value={notas} onChange={onChange} />
      </label>
      <label>
        Fecha de entrega
        <input type="date" name="fechaEntrega" value={fechaEntrega} onChange={onChange} />
      </label>
    </fieldset>
  )
}
