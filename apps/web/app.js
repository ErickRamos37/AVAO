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

function aluminumCutRow(window, cut, progress, label, onProgressChange) {
  const row = document.createElement('div');
  row.className = 'cut-row';
  const status = document.createElement('div');
  const actions = document.createElement('div');
  actions.className = 'cut-actions';
  const mark = document.createElement('button');
  const undo = document.createElement('button');
  mark.type = undo.type = 'button';
  mark.textContent = 'Marcar corte';
  undo.textContent = 'Deshacer marca';
  mark.setAttribute('aria-label', `Marcar corte de ${label} para ${window.codigo}`);
  undo.setAttribute('aria-label', `Deshacer marca de ${label} para ${window.codigo}`);

  function refresh() {
    status.textContent = `${label}: ${cut.longitud}″ · requerido ${cut.cantidad}, cortado ${progress.cortadas}, pendiente ${progress.pendientes}`;
    mark.disabled = progress.cortadas >= cut.cantidad;
    undo.disabled = progress.cortadas <= 0 || window.ensamblada;
  }

  async function change(action) {
    message.hidden = true;
    mark.disabled = undo.disabled = true;
    try {
      const response = await fetch(`/api/ventanas/${window.id}/aluminio/${progress.orden}/marcas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accion: action }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo guardar la marca de corte.');
      }
      const updated = await response.json();
      progress.cortadas = updated.cortadas;
      progress.pendientes = updated.pendientes;
      onProgressChange();
    } catch (error) {
      showError(error.message);
    } finally {
      refresh();
    }
  }

  mark.addEventListener('click', () => change('marcar'));
  undo.addEventListener('click', () => change('deshacer'));
  refresh();
  actions.append(mark, undo);
  row.append(status, actions);
  return row;
}

function glassCutRow(window, onProgressChange) {
  const row = document.createElement('div');
  row.className = 'cut-row';
  const status = document.createElement('div');
  const actions = document.createElement('div');
  actions.className = 'cut-actions';
  const mark = document.createElement('button');
  const undo = document.createElement('button');
  mark.type = undo.type = 'button';
  mark.textContent = 'Marcar corte';
  undo.textContent = 'Deshacer marca';
  mark.setAttribute('aria-label', `Marcar corte de vidrio para ${window.codigo}`);
  undo.setAttribute('aria-label', `Deshacer marca de vidrio para ${window.codigo}`);
  const plan = window.plan_vidrio;
  const progress = window.avance_vidrio;

  function refresh() {
    status.textContent = `Vidrio: ${plan.ancho}″ × ${plan.alto}″ · cortados: ${progress.cortadas} de ${plan.cantidad} · pendientes: ${progress.pendientes}`;
    mark.disabled = progress.cortadas >= plan.cantidad;
    undo.disabled = progress.cortadas <= 0 || window.ensamblada;
  }

  async function change(action) {
    message.hidden = true;
    mark.disabled = undo.disabled = true;
    try {
      const response = await fetch(`/api/ventanas/${window.id}/vidrio/marcas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accion: action }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo guardar la marca de corte de vidrio.');
      }
      const updated = await response.json();
      progress.cortadas = updated.cortadas;
      progress.pendientes = updated.pendientes;
      onProgressChange();
    } catch (error) {
      showError(error.message);
    } finally {
      refresh();
    }
  }

  mark.addEventListener('click', () => change('marcar'));
  undo.addEventListener('click', () => change('deshacer'));
  refresh();
  actions.append(mark, undo);
  row.append(status, actions);
  return row;
}

function assemblyRow(window, orderId) {
  const row = document.createElement('div');
  row.className = 'cut-row';
  const status = document.createElement('p');
  const note = document.createElement('p');
  note.textContent = 'Se habilita al registrar todos los cortes. Al confirmar, verificas físicamente screen, accesorios y extras aplicables.';
  const actions = document.createElement('div');
  actions.className = 'cut-actions';
  const mark = document.createElement('button');
  const undo = document.createElement('button');
  mark.type = undo.type = 'button';
  mark.textContent = 'Confirmar ensamble';
  undo.textContent = 'Deshacer ensamble';
  mark.setAttribute('aria-label', `Confirmar ensamble de ${window.codigo}`);
  undo.setAttribute('aria-label', `Deshacer ensamble de ${window.codigo}`);

  function refresh() {
    const complete = window.plan_aluminio.length === 10
      && window.avance_aluminio.length === 10
      && window.avance_aluminio.every((cut) => cut.pendientes === 0)
      && window.plan_vidrio && window.avance_vidrio
      && window.avance_vidrio.pendientes === 0;
    status.textContent = `Ensamble de ${window.codigo ?? window.numero}: ${window.ensamblada ? 'ensamblada' : 'pendiente'}`;
    mark.disabled = window.ensamblada || !complete;
    undo.disabled = !window.ensamblada;
  }

  async function change(action) {
    message.hidden = true;
    mark.disabled = undo.disabled = true;
    try {
      const response = await fetch(`/api/ventanas/${window.id}/ensamble/marcas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accion: action }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo guardar el ensamble.');
      }
      await openOrder(orderId);
    } catch (error) {
      showError(error.message);
      refresh();
    }
  }

  mark.addEventListener('click', () => change('marcar'));
  undo.addEventListener('click', () => change('deshacer'));
  refresh();
  actions.append(mark, undo);
  row.append(status, note, actions);
  return {row, refresh};
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
      const assembly = assemblyRow(window, order.id);
      content.append(assembly.row);
      if (!window.plan_aluminio.length) {
        const notice = document.createElement('p');
        notice.textContent = 'Plan de aluminio no disponible para este pedido anterior.';
        content.append(notice);
      } else if (window.plan_aluminio.length !== 10 || window.avance_aluminio.length !== 10) {
        const notice = document.createElement('p');
        notice.textContent = 'El plan de aluminio está incompleto.';
        content.append(notice);
      } else {
        const heading = document.createElement('h3');
        heading.textContent = 'Plan de aluminio';
        content.append(heading);
        const note = document.createElement('p');
        note.textContent = 'Cortado indica que el corte físico se realizó.';
        content.append(note);
        const plan = document.createElement('ul');
        const labels = [
          'Jamba', 'Mulio', 'Vertical fijo', 'Aleta', 'Horizontal fijo',
          'Horizontal corredizo', 'Guía', 'Riel', 'Screen horizontal', 'Screen vertical',
        ];
        for (const [index, label] of labels.entries()) {
          const line = document.createElement('li');
          line.append(aluminumCutRow(window, window.plan_aluminio[index], window.avance_aluminio[index], label, assembly.refresh));
          plan.append(line);
        }
        content.append(plan);
      }
      if (window.plan_vidrio && window.avance_vidrio) {
        content.append(glassCutRow(window, assembly.refresh));
      } else {
        const notice = document.createElement('p');
        notice.textContent = 'Plan de vidrio no disponible para este pedido anterior.';
        content.append(notice);
      }
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
