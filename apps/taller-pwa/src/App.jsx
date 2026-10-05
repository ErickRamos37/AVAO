// AVAO — Tarea #30, HU-02
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import TallerPage from './pages/TallerPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TallerPage />} />
        <Route path="/taller" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
