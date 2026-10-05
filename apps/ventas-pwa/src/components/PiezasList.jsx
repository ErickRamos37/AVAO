// AVAO — Tarea #28, HU-01
// Lista dinámica de piezas con botón agregar y mínimo 1 pieza.
import PiezaRow from './PiezaRow'
import ValidationMessage from './ValidationMessage'

export default function PiezasList({ piezas, errores, onPiezaChange, onAdd, onRemove, errorGeneral }) {
  return (
    <section>
      <h3>Piezas</h3>
      {piezas.map((pieza, index) => (
        <PiezaRow
          key={pieza._key}
          pieza={pieza}
          index={index}
          error={errores?.[index]}
          onChange={onPiezaChange}
          onRemove={onRemove}
          canRemove={piezas.length > 1}
        />
      ))}
      <button type="button" onClick={onAdd}>
        Agregar pieza
      </button>
      <ValidationMessage message={errorGeneral} />
    </section>
  )
}
