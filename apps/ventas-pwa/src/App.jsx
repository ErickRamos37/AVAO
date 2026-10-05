// AVAO — Tarea #28, HU-01; Tarea #38, HU-08 (SyncStatus)
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import CapturarPedidoPage from './pages/CapturarPedidoPage'
import PedidosPage from './pages/PedidosPage'
import SyncStatus from './components/SyncStatus'

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/capturar">Capturar</Link> | <Link to="/pedidos">Pedidos</Link>
        <SyncStatus />
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/capturar" replace />} />
        <Route path="/capturar" element={<CapturarPedidoPage />} />
        <Route path="/pedidos" element={<PedidosPage />} />
      </Routes>
    </BrowserRouter>
  )
}
