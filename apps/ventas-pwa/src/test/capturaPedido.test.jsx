// AVAO — Tarea #28, HU-01
// Pruebas Vitest del formulario de captura con Dexie offline simulado.
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CapturarPedidoPage from '../pages/CapturarPedidoPage'
import PedidosPage from '../pages/PedidosPage'
import { db } from '../db/dexieDb'

async function llenarFilaValida(user, index, { ancho = '100', largo = '200', cantidad = '2' } = {}) {
  await user.selectOptions(screen.getAllByLabelText('Producto')[index], 'vidrio-claro-6')
  await user.type(screen.getByLabelText(`Ancho pieza ${index + 1}`), ancho)
  await user.type(screen.getByLabelText(`Largo pieza ${index + 1}`), largo)
  await user.type(screen.getByLabelText(`Cantidad pieza ${index + 1}`), cantidad)
}

describe('Captura de pedido (HU-01)', () => {
  beforeEach(async () => {
    await db.pedidos.clear()
    await db.piezas.clear()
    // #38: el disparador post-guardado puede lanzar fetch a la API real;
    // se aísla con stub para que las pruebas no dependan de la red (PLAN-#38 §6).
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renderiza el formulario con campos de cliente y al menos 1 fila de pieza', () => {
    render(<CapturarPedidoPage />)
    expect(screen.getByLabelText(/nombre del cliente/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/teléfono/i)).toBeInTheDocument()
    expect(screen.getAllByTestId(/pieza-row-/)).toHaveLength(1)
    expect(screen.getByRole('button', { name: /agregar pieza/i })).toBeInTheDocument()
  })

  it('agrega N piezas dinámicamente y elimina filas', async () => {
    const user = userEvent.setup()
    render(<CapturarPedidoPage />)
    const btn = screen.getByRole('button', { name: /agregar pieza/i })
    await user.click(btn)
    await user.click(btn)
    expect(screen.getAllByTestId(/pieza-row-/)).toHaveLength(3)
    const eliminarBtns = screen.getAllByRole('button', { name: /eliminar/i })
    await user.click(eliminarBtns[0])
    expect(screen.getAllByTestId(/pieza-row-/)).toHaveLength(2)
  })

  it('guarda en Dexie con estadoSync pendiente (offline simulado)', async () => {
    const user = userEvent.setup()
    render(<CapturarPedidoPage />)
    await user.type(screen.getByLabelText(/nombre del cliente/i), 'Vidriería López')
    await llenarFilaValida(user, 0)
    await user.click(screen.getByRole('button', { name: /agregar pieza/i }))
    await llenarFilaValida(user, 1)
    await user.click(screen.getByRole('button', { name: /guardar pedido/i }))

    await waitFor(async () => {
      expect(await db.pedidos.count()).toBe(1)
    })
    const pedido = (await db.pedidos.toArray())[0]
    expect(pedido.clienteNombre).toBe('Vidriería López')
    expect(pedido.estadoSync).toBe('pendiente')
    const piezas = await db.piezas.where('pedidoIdLocal').equals(pedido.idLocal).toArray()
    expect(piezas).toHaveLength(2)
    expect(screen.getByRole('status')).toHaveTextContent(/guardado localmente/i)
  })

  it('rechaza medidas negativas y no persiste', async () => {
    const user = userEvent.setup()
    render(<CapturarPedidoPage />)
    await user.type(screen.getByLabelText(/nombre del cliente/i), 'Cliente X')
    await llenarFilaValida(user, 0, { ancho: '-5' })
    await user.click(screen.getByRole('button', { name: /guardar pedido/i }))
    expect(await screen.findAllByRole('alert')).not.toHaveLength(0)
    expect(screen.getAllByText(/mayor que 0/i).length).toBeGreaterThan(0)
    expect(await db.pedidos.count()).toBe(0)
  })

  it('rechaza cantidad 0, nombre vacío y producto no seleccionado', async () => {
    const user = userEvent.setup()
    render(<CapturarPedidoPage />)
    await user.type(screen.getByLabelText(`Ancho pieza 1`), '100')
    await user.type(screen.getByLabelText(`Largo pieza 1`), '200')
    await user.type(screen.getByLabelText(`Cantidad pieza 1`), '0')
    await user.click(screen.getByRole('button', { name: /guardar pedido/i }))
    const alerts = await screen.findAllByRole('alert')
    expect(alerts.length).toBeGreaterThan(0)
    expect(await db.pedidos.count()).toBe(0)
  })

  it('lista pedidos con badge pendiente de sincronizar', async () => {
    const user = userEvent.setup()
    render(<CapturarPedidoPage />)
    await user.type(screen.getByLabelText(/nombre del cliente/i), 'Vidriería López')
    await llenarFilaValida(user, 0)
    await user.click(screen.getByRole('button', { name: /guardar pedido/i }))
    await waitFor(async () => expect(await db.pedidos.count()).toBe(1))

    render(<PedidosPage />)
    expect(await screen.findByText('Vidriería López')).toBeInTheDocument()
    expect(await screen.findByText(/pendiente de sincronizar/i)).toBeInTheDocument()
  })
})
