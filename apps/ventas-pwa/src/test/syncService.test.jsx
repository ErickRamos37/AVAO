// AVAO — Tarea #38, HU-08 / HU-01
// Pruebas de sincronización offline→API (checklist de testing de #38):
// servicio con fetch mockeado + UI con navigator.onLine sobreescrito.
// Dexie corre sobre fake-indexeddb (src/test/setup.js); la API NO se levanta.
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addPedido, db } from '../db/dexieDb'
import {
  construirPayloadPedido,
  hayConexion,
  syncPedidosPendientes,
} from '../services/syncService'
import CapturarPedidoPage from '../pages/CapturarPedidoPage'
import SyncStatus from '../components/SyncStatus'

const API_URL = 'http://localhost:8000'
const UUID_CLIENTE_LOPEZ = 'a1b2c3d4-0000-4000-8000-000000000001'
const UUID_VIDRIO_CLARO_6 = 'a1b2c3d4-0000-4000-8000-000000000011'
const UUID_VIDRIO_TEMPLADO_10 = 'a1b2c3d4-0000-4000-8000-000000000012'

/** Sobreescribe navigator.onLine (jsdom lo expone como propiedad configurable). */
function setOnline(valor) {
  Object.defineProperty(window.navigator, 'onLine', {
    value: valor,
    configurable: true,
  })
}

/** Pedido válido de ejemplo (cliente y producto con mapeo a UUID de API). */
async function agregarPedido(overrides = {}) {
  return addPedido({
    clienteNombre: 'Vidriería López',
    telefono: '555-1234',
    notas: 'Entregar en mostrador',
    fechaEntrega: '2026-10-10',
    piezas: [{ productoId: 'vidrio-claro-6', ancho_mm: '100', largo_mm: '200', cantidad: '2' }],
    ...overrides,
  })
}

/** Llena y envía el formulario de captura con una pieza válida. */
async function capturarPedidoValido(user) {
  await user.type(screen.getByLabelText(/nombre del cliente/i), 'Vidriería López')
  await user.selectOptions(screen.getByLabelText('Producto'), 'vidrio-claro-6')
  await user.type(screen.getByLabelText('Ancho pieza 1'), '100')
  await user.type(screen.getByLabelText('Largo pieza 1'), '200')
  await user.type(screen.getByLabelText('Cantidad pieza 1'), '2')
  await user.click(screen.getByRole('button', { name: /guardar pedido/i }))
}

describe('syncService (HU-08)', () => {
  let fetchMock

  beforeEach(async () => {
    await db.pedidos.clear()
    await db.piezas.clear()
    setOnline(true)
    fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    setOnline(true)
  })

  it('hayConexion refleja navigator.onLine', () => {
    setOnline(true)
    expect(hayConexion()).toBe(true)
    setOnline(false)
    expect(hayConexion()).toBe(false)
  })

  // Caso 1 — guardar offline: sin fetch, todo sigue 'pendiente'.
  it('1. sin conexión: sync no llama a fetch y el pedido sigue pendiente', async () => {
    setOnline(false)
    const idLocal = await agregarPedido()
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')

    const resumen = await syncPedidosPendientes()

    expect(fetchMock).not.toHaveBeenCalled()
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')
    expect(resumen.sincronizados).toBe(0)
    expect(resumen.mensaje).toBe('Sin conexión: los pedidos siguen guardados localmente')
  })

  // Caso 2 — central: recuperar red → POST /pedidos → 'sincronizado'.
  it('2. al recuperar red, envía POST /pedidos con el payload mapeado y marca sincronizado', async () => {
    const idLocal = await agregarPedido()
    fetchMock.mockResolvedValue({ ok: true, status: 201 })

    const resumen = await syncPedidosPendientes()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe(`${API_URL}/pedidos`)
    expect(init.method).toBe('POST')
    expect(init.headers['Content-Type']).toBe('application/json')
    expect(JSON.parse(init.body)).toEqual({
      cliente_id: UUID_CLIENTE_LOPEZ,
      fecha_entrega: '2026-10-10',
      notas: 'Tel: 555-1234 — Entregar en mostrador',
      piezas: [
        { producto_id: UUID_VIDRIO_CLARO_6, ancho_mm: 100, largo_mm: 200, cantidad: 2 },
      ],
    })
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('sincronizado')
    expect(resumen.sincronizados).toBe(1)
    expect(resumen.mensaje).toBe('1 pedido(s) sincronizado(s) con la API')
  })

  // Caso 3 — fallo de red (fetch rechaza).
  it('3. fallo de red (TypeError) mantiene pendiente y escribe ultimoError', async () => {
    const idLocal = await agregarPedido()
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))

    const resumen = await syncPedidosPendientes()

    const fila = await db.pedidos.get(idLocal)
    expect(fila.estadoSync).toBe('pendiente')
    expect(fila.ultimoError).toBe('Failed to fetch')
    expect(resumen.errores).toBe(1)
    expect(resumen.erroresDetalle[0]).toEqual({ idLocal, mensaje: 'Failed to fetch' })
  })

  // Caso 4 — error HTTP 5xx.
  it('4. HTTP 500 mantiene pendiente y cuenta el error', async () => {
    const idLocal = await agregarPedido()
    fetchMock.mockResolvedValue({ ok: false, status: 500 })

    const resumen = await syncPedidosPendientes()

    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')
    expect(resumen.errores).toBe(1)
    expect(resumen.erroresDetalle[0].mensaje).toBe('API respondió 500')
  })

  // Caso 5 — error HTTP 404 (cliente/producto no existe en la API).
  it('5. HTTP 404 mantiene pendiente con mensaje "API respondió 404"', async () => {
    const idLocal = await agregarPedido()
    fetchMock.mockResolvedValue({ ok: false, status: 404 })

    const resumen = await syncPedidosPendientes()

    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')
    expect(resumen.errores).toBe(1)
    expect(resumen.erroresDetalle[0].mensaje).toContain('API respondió 404')
  })

  it.each([200, 204])('5b. HTTP %i no confirma el alta y mantiene el pedido pendiente', async (status) => {
    const idLocal = await agregarPedido()
    fetchMock.mockResolvedValue({ ok: true, status })

    const resumen = await syncPedidosPendientes()

    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')
    expect(resumen.errores).toBe(1)
    expect(resumen.erroresDetalle[0].mensaje).toBe(`API respondió ${status}; se esperaba 201`)
  })

  // Caso 6 — cola con éxito parcial.
  it('6. cola de 2 pedidos: el que resuelve mapeo se sincroniza; el otro queda pendiente', async () => {
    const idOk = await agregarPedido()
    const idFail = await agregarPedido({ clienteNombre: 'Cliente Desconocido' })
    fetchMock.mockResolvedValue({ ok: true, status: 201 })

    const resumen = await syncPedidosPendientes()

    expect(fetchMock).toHaveBeenCalledTimes(1) // solo el pedimento con mapeo llega a fetch
    expect(resumen.sincronizados).toBe(1)
    expect(resumen.errores).toBe(1)
    expect((await db.pedidos.get(idOk)).estadoSync).toBe('sincronizado')
    const fallido = await db.pedidos.get(idFail)
    expect(fallido.estadoSync).toBe('pendiente')
    expect(fallido.ultimoError).toContain('Cliente sin UUID de API')
  })

  // Caso 7 — mapeo de payload (§5).
  it('7. construye el payload: fechas, notas con teléfono plegado, números y UUIDs', async () => {
    // Con datos completos y medidas como strings (del formulario).
    const pedidoA = {
      clienteNombre: 'Vidriería López',
      telefono: '555-1234',
      notas: 'Entregar en mostrador',
      fechaEntrega: '2026-10-10',
      piezas: [{ productoId: 'vidrio-claro-6', ancho_mm: '100', largo_mm: '200', cantidad: '2' }],
    }
    expect(construirPayloadPedido(pedidoA, pedidoA.piezas)).toEqual({
      cliente_id: UUID_CLIENTE_LOPEZ,
      fecha_entrega: '2026-10-10',
      notas: 'Tel: 555-1234 — Entregar en mostrador',
      piezas: [
        { producto_id: UUID_VIDRIO_CLARO_6, ancho_mm: 100, largo_mm: 200, cantidad: 2 },
      ],
    })

    // Con campos vacíos: nulls, decimales y otro producto del catálogo.
    const pedidoB = {
      clienteNombre: '  Vidriería López  ',
      telefono: '',
      notas: '   ',
      fechaEntrega: '',
      piezas: [{ productoId: 'vidrio-templado-10', ancho_mm: '10.5', largo_mm: '20.25', cantidad: '3' }],
    }
    expect(construirPayloadPedido(pedidoB, pedidoB.piezas)).toEqual({
      cliente_id: UUID_CLIENTE_LOPEZ,
      fecha_entrega: null,
      notas: null,
      piezas: [
        { producto_id: UUID_VIDRIO_TEMPLADO_10, ancho_mm: 10.5, largo_mm: 20.25, cantidad: 3 },
      ],
    })
  })

  // Caso 8 — cliente sin mapeo: lanza y el pedido queda en cola.
  it('8. cliente sin mapeo: construirPayloadPedido lanza y el pedido queda pendiente', async () => {
    const idLocal = await agregarPedido({ clienteNombre: 'Cliente Nuevo' })

    expect(() =>
      construirPayloadPedido({ clienteNombre: 'Cliente Nuevo' }, []),
    ).toThrow(/Cliente sin UUID de API/)

    fetchMock.mockResolvedValue({ ok: true, status: 201 })
    const resumen = await syncPedidosPendientes()

    expect(fetchMock).not.toHaveBeenCalled() // nunca se envía basura a la API
    expect((await db.pedidos.get(idLocal)).estadoSync).toBe('pendiente')
    expect(resumen.errores).toBe(1)
  })

  // Caso 9 — UI: guardar offline → evento online → se envía y cambia el badge.
  it('9. UI: guardar offline y, al evento online, sincroniza y el badge pasa a "✓ sincronizado"', async () => {
    setOnline(false)
    const user = userEvent.setup()
    // SyncStatus primero: su instancia del hook escucha 'online' primero y
    // es la que muestra el mensaje de resultado (cerrojo del servicio evita
    // el doble envío entre las dos instancias del hook).
    render(
      <>
        <SyncStatus />
        <CapturarPedidoPage />
      </>,
    )
    await capturarPedidoValido(user)

    // Offline: badge con pendiente, mensaje de guardado local, sin fetch.
    expect(await screen.findByTestId('sync-pendientes')).toHaveTextContent(
      /1 pendiente\(s\) de sincronizar/,
    )
    expect(await screen.findByText('Pedido guardado localmente')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()

    // Simular recuperación de red.
    setOnline(true)
    fetchMock.mockResolvedValue({ ok: true, status: 201 })
    window.dispatchEvent(new Event('online'))

    await waitFor(() => {
      expect(screen.getByTestId('sync-pendientes')).toHaveTextContent('✓ sincronizado')
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
    await waitFor(() => {
      expect(screen.getByText(/1 pedido\(s\) sincronizado\(s\) con la API/)).toBeInTheDocument()
    })
    expect((await db.pedidos.toArray())[0].estadoSync).toBe('sincronizado')
  })

  // Caso 10 — UI offline: guardado local sin intento de envío.
  it('10. UI offline: guardar muestra "guardado localmente", badge pendiente y sin fetch', async () => {
    setOnline(false)
    const user = userEvent.setup()
    render(
      <>
        <SyncStatus />
        <CapturarPedidoPage />
      </>,
    )
    await capturarPedidoValido(user)

    expect(await screen.findByText('Pedido guardado localmente')).toBeInTheDocument()
    expect(await screen.findByTestId('sync-pendientes')).toHaveTextContent(
      /1 pendiente\(s\) de sincronizar/,
    )
    expect(fetchMock).not.toHaveBeenCalled()
    const pedidos = await db.pedidos.toArray()
    expect(pedidos).toHaveLength(1)
    expect(pedidos[0].estadoSync).toBe('pendiente')
  })
})
