const capture = document.querySelector('#capture');
const detail = document.querySelector('#detail');
const message = document.querySelector('#message');
const errorReturn = document.querySelector('#error-return');
const rows = document.querySelector('#window-rows');
const rowTemplate = document.querySelector('#window-template');
let nextRowId = 1;

function numberRows() {
  for (const [index, row] of [...rows.children].entries()) {
    row.querySelector('legend').textContent = `Ventana ${index + 1}`;
    row.querySelector('.discard-row').textContent = `Descartar ventana ${index + 1}`;
  }
}

function addRow() {
  const row = rowTemplate.content.firstElementChild.cloneNode(true);
  const width = row.querySelector('.width');
  const height = row.querySelector('.height');
  width.id = `width-${nextRowId}`;
  height.id = `height-${nextRowId}`;
  nextRowId += 1;
  row.querySelectorAll('label')[0].htmlFor = width.id;
  row.querySelectorAll('label')[1].htmlFor = height.id;
  row.querySelector('.discard-row').addEventListener('click', () => {
    row.remove();
    if (!rows.children.length) addRow();
    else numberRows();
  });
  rows.append(row);
  numberRows();
}

document.querySelector('#add-row').addEventListener('click', addRow);
addRow();

function showError(text) {
  message.textContent = text;
  message.hidden = false;
}

async function loadOrders() {
  const list = document.querySelector('#order-list');
  try {
    const response = await fetch('/api/pedidos');
    if (!response.ok) throw new Error();
    const data = await response.json();
    list.replaceChildren();
    if (!data.pedidos.length) {
      list.textContent = 'Aún no hay pedidos.';
      return;
    }
    for (const order of data.pedidos) {
      const item = document.createElement('p');
      const link = document.createElement('a');
      link.href = `/pedidos/${order.id}`;
      link.textContent = order.etiqueta === null
        ? `Pedido ${order.id} · sin etiqueta`
        : `Pedido ${order.id} · ${order.codigos.join(', ')}`;
      item.append(link);
      list.append(item);
    }
  } catch {
    list.textContent = 'No se pudo cargar la lista de pedidos.';
  }
}

async function openOrder(id) {
  capture.hidden = true;
  detail.hidden = true;
  message.hidden = true;
  errorReturn.hidden = true;

  try {
    const response = await fetch(`/api/pedidos/${encodeURIComponent(id)}`);
    if (!response.ok) throw new Error(response.status === 404 ? 'Pedido no encontrado.' : 'No se pudo consultar el pedido.');
    const order = await response.json();
    document.querySelector('#order-title').textContent = order.etiqueta === null
      ? `Pedido ${order.id} · sin etiqueta`
      : `Pedido ${order.id} · ${order.etiqueta}`;
    const content = document.querySelector('#order-content');
    content.replaceChildren();
    for (const window of order.ventanas) {
      const item = document.createElement('p');
      item.textContent = `Ventana ${window.codigo ?? window.numero}: ${window.ancho} × ${window.alto}`;
      content.append(item);
      if (!window.plan_aluminio.length) {
        const notice = document.createElement('p');
        notice.textContent = 'Plan de aluminio no disponible para este pedido anterior.';
        content.append(notice);
      } else {
        const heading = document.createElement('h3');
        heading.textContent = 'Plan de aluminio';
        content.append(heading);
        const plan = document.createElement('ul');
        for (const cut of window.plan_aluminio) {
          const line = document.createElement('li');
          line.textContent = `${cut.perfil}: ${cut.longitud}″ × ${cut.cantidad}`;
          plan.append(line);
        }
        content.append(plan);
      }
      const glass = document.createElement('p');
      glass.textContent = window.plan_vidrio
        ? `Vidrio: ${window.plan_vidrio.ancho}″ × ${window.plan_vidrio.alto}″ · ${window.plan_vidrio.cantidad} piezas iguales`
        : 'Plan de vidrio no disponible para este pedido anterior.';
      content.append(glass);
    }
    detail.hidden = false;
  } catch (error) {
    showError(error.message);
    errorReturn.hidden = false;
  }
}

document.querySelector('#order-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  message.hidden = true;
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const windows = [...rows.children].map((row) => ({
      ancho: row.querySelector('.width').value.trim(),
      alto: row.querySelector('.height').value.trim(),
    }));
    const partialIndex = windows.findIndex((window) => Boolean(window.ancho) !== Boolean(window.alto));
    if (partialIndex !== -1) {
      showError(`Ventana ${partialIndex + 1}: completa ancho y alto o descarta la fila.`);
      return;
    }
    if (!windows.some((window) => window.ancho && window.alto)) {
      showError('Agrega al menos una ventana con ancho y alto completos.');
      return;
    }
    const response = await fetch('/api/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ventanas: windows }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo guardar el pedido.');
    }
    const order = await response.json();
    history.pushState({}, '', `/pedidos/${order.id}`);
    loadOrders();
    await openOrder(order.id);
  } catch (error) {
    showError(error.message);
  } finally {
    button.disabled = false;
  }
});

window.addEventListener('popstate', () => {
  const match = location.pathname.match(/^\/pedidos\/(\d+)$/);
  if (match) openOrder(match[1]);
  else {
    detail.hidden = true;
    capture.hidden = false;
    message.hidden = true;
    errorReturn.hidden = true;
  }
});

const match = location.pathname.match(/^\/pedidos\/(\d+)$/);
loadOrders();
if (match) openOrder(match[1]);
