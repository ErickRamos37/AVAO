// AVAO — Tarea #28, HU-01
// Select controlado desde el catálogo local de productos.
import { catalogoProductos } from '../constants/catalogoProductos'

export default function ProductoSelect({ value, onChange }) {
  return (
    <select aria-label="Producto" name="productoId" value={value} onChange={onChange}>
      <option value="">Selecciona un producto</option>
      {catalogoProductos.map((p) => (
        <option key={p.id} value={p.id}>
          {p.nombre}
        </option>
      ))}
    </select>
  )
}
