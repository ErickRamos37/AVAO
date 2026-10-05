// AVAO — Tarea #28, HU-01; Tarea #38, HU-08 (disparador post-guardado)
// Página /capturar con el formulario de pedido.
import PedidoForm from '../components/PedidoForm'
import { useSincronizacion } from '../hooks/useSincronizacion'

export default function CapturarPedidoPage() {
  const { sincronizar } = useSincronizacion()
  return (
    <main>
      <h1>Capturar pedido</h1>
      <PedidoForm onGuardado={sincronizar} />
    </main>
  )
}
