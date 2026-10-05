// AVAO — Tarea #28, HU-01
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import CapturarPedidoPage from './pages/CapturarPedidoPage'
import PedidosPage from './pages/PedidosPage'

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/capturar">Capturar</Link> | <Link to="/pedidos">Pedidos</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/capturar" replace />} />
        <Route path="/capturar" element={<CapturarPedidoPage />} />
        <Route path="/pedidos" element={<PedidosPage />} />
      </Routes>
    </BrowserRouter>
  )
}
