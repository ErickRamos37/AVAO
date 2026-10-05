// AVAO — Tarea #30, HU-02
// Pruebas Vitest de la vista de Taller.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import TallerPage from '../pages/TallerPage'
import { getTareasPendientes } from '../services/tareasApi'

vi.mock('../services/tareasApi', () => ({
  getTareasPendientes: vi.fn(),
}))

const t1 = {
  pieza_id: '11111111-1111-1111-1111-111111111111',
  pedido_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  product_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  ancho_mm: '1200.00',
  largo_mm: '2400.00',
  cantidad: 2,
  estado: 'pendiente',
  operario_asignado: 'Ana',
  fecha: '2026-10-04T10:15:30Z',
}

const t2 = {
  pieza_id: '22222222-2222-2222-2222-222222222222',
  pedido_id: 'cccccccc-cccc-cccc-cccc-cccccccccccc',
  product_id: 'dddddddd-dddd-dddd-dddd-dddddddddddd',
  ancho_mm: '600.00',
  largo_mm: '900.00',
  cantidad: 1,
  estado: 'pendiente',
  operario_asignado: null,
  fecha: '2026-10-04T11:00:00Z',
}

describe('TallerPage (HU-02)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('muestra estado vacío cuando no hay tareas', async () => {
    getTareasPendientes.mockResolvedValue([])
    render(<TallerPage />)
    expect(await screen.findByText(/No hay cortes pendientes hoy/i)).toBeInTheDocument()
    expect(screen.queryAllByTestId('corte-card')).toHaveLength(0)
  })

  it('renderiza una card por tarea con datos válidos', async () => {
    getTareasPendientes.mockResolvedValue([t1, t2])
    render(<TallerPage />)
    const cards = await screen.findAllByTestId('corte-card')
    expect(cards).toHaveLength(2)
    expect(screen.getByText(/11111111/)).toBeInTheDocument()
    expect(screen.getByText(/22222222/)).toBeInTheDocument()
    expect(screen.getByText('Cantidad: 2')).toBeInTheDocument()
    expect(screen.getByText('Cantidad: 1')).toBeInTheDocument()
    expect(screen.getAllByText('pendiente')).toHaveLength(2)
    expect(screen.getByText('Operario: Ana')).toBeInTheDocument()
    expect(screen.getByText('Operario: Sin asignar')).toBeInTheDocument()
    expect(
      screen.getByText(`Fecha: ${new Date(t1.fecha).toLocaleString()}`),
    ).toBeInTheDocument()
  })

  it('muestra las medidas ancho x largo en cada card', async () => {
    getTareasPendientes.mockResolvedValue([t1, t2])
    render(<TallerPage />)
    expect(await screen.findByText(/1200\.00 x 2400\.00 mm/)).toBeInTheDocument()
    expect(screen.getByText(/600\.00 x 900\.00 mm/)).toBeInTheDocument()
  })

  it('muestra indicador de carga mientras espera', () => {
    getTareasPendientes.mockReturnValue(new Promise(() => {}))
    render(<TallerPage />)
    expect(screen.getByText(/Cargando/i)).toBeInTheDocument()
  })

  it('muestra mensaje de error si la petición falla', async () => {
    getTareasPendientes.mockRejectedValue(new Error('Network down'))
    render(<TallerPage />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/Error al cargar cortes/i)
  })
})
