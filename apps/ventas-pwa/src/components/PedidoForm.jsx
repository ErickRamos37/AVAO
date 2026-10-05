// AVAO — Tarea #28, HU-01
// Orquestador del formulario de captura de pedido; valida y persiste en Dexie.
import { useState } from 'react'
import ClienteFields from './ClienteFields'
import PiezasList from './PiezasList'
import { addPedido } from '../db/dexieDb'
import { validarPedido } from '../utils/validarPedido'

let nextKey = 1
const piezaVacia = () => ({ _key: nextKey++, productoId: '', ancho_mm: '', largo_mm: '', cantidad: '' })

export default function PedidoForm({ onGuardado }) {
  const [clienteNombre, setClienteNombre] = useState('')
  const [telefono, setTelefono] = useState('')
  const [notas, setNotas] = useState('')
  const [fechaEntrega, setFechaEntrega] = useState('')
  const [piezas, setPiezas] = useState([piezaVacia()])
  const [errores, setErrores] = useState({ cliente: '', piezas: [], general: '' })
  const [mensaje, setMensaje] = useState('')

  const onClienteChange = (e) => {
    const { name, value } = e.target
    if (name === 'clienteNombre') setClienteNombre(value)
    else if (name === 'telefono') setTelefono(value)
    else if (name === 'notas') setNotas(value)
    else if (name === 'fechaEntrega') setFechaEntrega(value)
  }

  const onPiezaChange = (index, campo, valor) => {
    setPiezas((prev) => prev.map((p, i) => (i === index ? { ...p, [campo]: valor } : p)))
  }

  const agregarPieza = () => setPiezas((prev) => [...prev, piezaVacia()])

  const eliminarPieza = (index) =>
    setPiezas((prev) => (prev.length > 1 ? prev.filter((_, i) => i !== index) : prev))

  const onSubmit = async (e) => {
    e.preventDefault()
    const { errores: errs, valido } = validarPedido({ clienteNombre, piezas })
    setErrores(errs)
    if (!valido) {
      setMensaje('')
      return
    }
    await addPedido({ clienteNombre: clienteNombre.trim(), telefono, notas, fechaEntrega, piezas })
    setMensaje('Pedido guardado localmente')
    setClienteNombre('')
    setTelefono('')
    setNotas('')
    setFechaEntrega('')
    setPiezas([piezaVacia()])
    setErrores({ cliente: '', piezas: [], general: '' })
    onGuardado?.()
  }

  return (
    <form onSubmit={onSubmit}>
      <ClienteFields
        clienteNombre={clienteNombre}
        telefono={telefono}
        notas={notas}
        fechaEntrega={fechaEntrega}
        error={errores.cliente}
        onChange={onClienteChange}
      />
      <PiezasList
        piezas={piezas}
        errores={errores.piezas}
        onPiezaChange={onPiezaChange}
        onAdd={agregarPieza}
        onRemove={eliminarPieza}
        errorGeneral={errores.general}
      />
      <button type="submit">Guardar pedido</button>
      {mensaje && <p role="status">{mensaje}</p>}
    </form>
  )
}
