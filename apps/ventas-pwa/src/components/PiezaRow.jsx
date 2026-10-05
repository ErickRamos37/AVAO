// AVAO — Tarea #28, HU-01
// Fila editable de una pieza: producto, medidas en mm y cantidad.
import ProductoSelect from './ProductoSelect'
import ValidationMessage from './ValidationMessage'

export default function PiezaRow({ pieza, index, error, onChange, onRemove, canRemove }) {
  return (
    <div className="pieza-row" data-testid={`pieza-row-${index}`}>
      <ProductoSelect
        value={pieza.productoId}
        onChange={(e) => onChange(index, 'productoId', e.target.value)}
      />
      <input
        type="number"
        aria-label={`Ancho pieza ${index + 1}`}
        placeholder="ancho_mm"
        value={pieza.ancho_mm}
        onChange={(e) => onChange(index, 'ancho_mm', e.target.value)}
      />
      <input
        type="number"
        aria-label={`Largo pieza ${index + 1}`}
        placeholder="largo_mm"
        value={pieza.largo_mm}
        onChange={(e) => onChange(index, 'largo_mm', e.target.value)}
      />
      <input
        type="number"
        aria-label={`Cantidad pieza ${index + 1}`}
        placeholder="cantidad"
        value={pieza.cantidad}
        onChange={(e) => onChange(index, 'cantidad', e.target.value)}
      />
      <button type="button" onClick={() => onRemove(index)} disabled={!canRemove}>
        Eliminar
      </button>
      <ValidationMessage message={error} />
    </div>
  )
}
