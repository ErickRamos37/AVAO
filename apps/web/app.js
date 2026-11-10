const capture = document.querySelector('#capture');
const detail = document.querySelector('#detail');
const message = document.querySelector('#message');
const errorReturn = document.querySelector('#error-return');
const rows = document.querySelector('#window-rows');
const rowTemplate = document.querySelector('#window-template');
const clientForm = document.querySelector('#client-form');
const measures = document.querySelector('#order-measures');
const discardedSection = document.querySelector('#discarded-windows');
const discardedList = document.querySelector('#discarded-window-list');
const measureEditButton = document.querySelector('#edit-measures');
const measureEditForm = document.querySelector('#measure-edit-form');
const measureEditRows = document.querySelector('#measure-edit-rows');
const areaButtons = [...document.querySelectorAll('#area-nav button')];
const areaPanels = [...document.querySelectorAll('[data-area-panel]')];
let currentOrderId = null;
let currentOrderData = null;
let nextRowId = 1;

function showArea(area) {
  if (area !== 'medidas') exitMeasureEdit();
  for (const button of areaButtons) {
    button.setAttribute('aria-pressed', String(button.dataset.area === area));
  }
  for (const panel of areaPanels) {
    panel.hidden = panel.id !== `area-${area}`;
  }
}

for (const button of areaButtons) {
  button.addEventListener('click', () => showArea(button.dataset.area));
}

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

function updateMeasureEditButton(order = currentOrderData) {
  const visible = Boolean(order?.ventanas.length);
  measureEditButton.hidden = !visible || !measureEditForm.hidden;
}

function exitMeasureEdit() {
  if (!measureEditForm) return;
  measureEditForm.hidden = true;
  measureEditForm.style.display = 'none';
  measureEditRows.replaceChildren();
  measures.hidden = false;
  updateMeasureEditButton();
}

function enterMeasureEdit() {
  if (!currentOrderData) return;
  measureEditRows.replaceChildren();
  for (const window of currentOrderData.ventanas) {
    const fieldset = document.createElement('fieldset');
    fieldset.className = 'window-measure-edit';
    fieldset.dataset.windowId = window.id;
    fieldset.dataset.originalWidth = window.ancho;
    fieldset.dataset.originalHeight = window.alto;
    const legend = document.createElement('legend');
    legend.textContent = `Ventana ${window.codigo ?? window.numero}`;
    const widthLabel = document.createElement('label');
    widthLabel.textContent = 'Ancho nuevo';
    const widthInput = document.createElement('input');
    widthInput.name = 'ancho';
    widthInput.required = true;
    widthInput.autocomplete = 'off';
    widthInput.value = window.ancho;
    widthLabel.append(widthInput);
    const heightLabel = document.createElement('label');
    heightLabel.textContent = 'Alto nuevo';
    const heightInput = document.createElement('input');
    heightInput.name = 'alto';
    heightInput.required = true;
    heightInput.autocomplete = 'off';
    heightInput.value = window.alto;
    heightLabel.append(heightInput);
    fieldset.append(legend, widthLabel, heightLabel);
    measureEditRows.append(fieldset);
  }
  measureEditForm.hidden = false;
  measureEditForm.style.display = 'grid';
  measures.hidden = true;
  measureEditButton.hidden = true;
}

measureEditButton.addEventListener('click', enterMeasureEdit);
document.querySelector('#cancel-measure-edit').addEventListener('click', exitMeasureEdit);

measureEditForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.hidden = true;
  const submit = measureEditForm.querySelector('button[type="submit"]');
  const cancel = document.querySelector('#cancel-measure-edit');
  const changes = [...measureEditRows.children].map((fieldset) => ({
    id: Number(fieldset.dataset.windowId),
    ancho: fieldset.querySelector('[name="ancho"]').value.trim(),
    alto: fieldset.querySelector('[name="alto"]').value.trim(),
    anchoAnterior: fieldset.dataset.originalWidth,
    altoAnterior: fieldset.dataset.originalHeight,
  })).filter((item) => item.ancho !== item.anchoAnterior || item.alto !== item.altoAnterior);

  if (!changes.length) {
    exitMeasureEdit();
    message.textContent = 'No hay medidas modificadas.';
    message.hidden = false;
    return;
  }

  const summaries = changes.map((item) => {
    const window = currentOrderData.ventanas.find((candidate) => candidate.id === item.id);
    const aluminumCuts = window.avance_aluminio.reduce((total, cut) => total + cut.cortadas, 0);
    const glassCuts = window.avance_vidrio?.cortadas ?? 0;
    const assembly = window.ensamblada ? '; se quitará la marca de ensamble' : '';
    return `• ${window.codigo ?? `Ventana ${window.numero}`}: ${item.anchoAnterior} × ${item.altoAnterior} → ${item.ancho} × ${item.alto} (${aluminumCuts} cortes de aluminio y ${glassCuts} de vidrio marcados${assembly})`;
  });
  const confirmed = globalThis.confirm(
    `Vas a corregir ${changes.length} ventana(s):\n\n${summaries.join('\n')}\n\n`
    + 'AVAO recalculará los planes de aluminio y vidrio. Conservará las marcas de las piezas del mismo tipo/perfil y medida, '
    + 'y quitará las marcas que ya no correspondan. Los códigos de ventana se conservan. ¿Guardar cambios?',
  );
  if (!confirmed) return;

  submit.disabled = true;
  cancel.disabled = true;
  try {
    const orderId = currentOrderData.id;
    const response = await fetch(`/api/pedidos/${orderId}/medidas`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ventanas: changes.map(({ id, ancho, alto }) => ({ id, ancho, alto })),
        confirmar_correccion: true,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudieron corregir las medidas.');
    }
    const result = await response.json();
    exitMeasureEdit();
    await openOrder(orderId);
    const keptAluminum = result.resultados.reduce((total, item) => total + item.marcas_aluminio_conservadas, 0);
    const keptGlass = result.resultados.reduce((total, item) => total + item.marcas_vidrio_conservadas, 0);
    const cleared = result.resultados.reduce((total, item) => total + item.marcas_retiradas, 0);
    message.textContent = `Se actualizaron ${result.resultados.length} ventana(s). Se conservaron ${keptAluminum} marcas de aluminio y ${keptGlass} de vidrio; se retiraron ${cleared}.`;
    message.hidden = false;
  } catch (error) {
    showError(error.message);
  } finally {
    submit.disabled = false;
    cancel.disabled = false;
  }
});

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
    const response = await fetch('/api/pedidos/avance');
    if (!response.ok) throw new Error();
    const data = await response.json();
    list.replaceChildren();
    if (!data.pedidos.length) {
      list.textContent = 'Aún no hay pedidos.';
      return;
    }
    for (const [index, order] of data.pedidos.entries()) {
      const item = document.createElement('article');
      item.className = 'order-card';
      const heading = document.createElement('h3');
      const link = document.createElement('a');
      link.href = `/pedidos/${order.id}`;
      link.textContent = order.etiqueta === null
        ? `${index + 1}. Pedido ${order.id} · sin etiqueta`
        : `${index + 1}. Pedido ${order.etiqueta}`;
      heading.append(link);
      item.append(heading);
      const summary = document.createElement('p');
      summary.textContent = order.sin_ventanas ? 'Sin ventanas activas'
        : order.sin_plan ? 'Sin plan de corte completo'
        : `Avance general: ${order.porcentaje} %`;
      item.append(summary);
      if (order.porcentaje !== null) {
        const progress = document.createElement('progress');
        progress.max = 100;
        progress.value = order.porcentaje;
        progress.setAttribute('aria-label', `Avance general del pedido ${order.etiqueta ?? order.id}`);
        item.append(progress);
      }
      if (order.listo_instalacion) {
        const ready = document.createElement('p');
        ready.textContent = 'Listo para instalación';
        item.append(ready);
      }
      if (!order.sin_ventanas) {
        const details = document.createElement('details');
        const detailsHeading = document.createElement('summary');
        detailsHeading.textContent = 'Ver avance por área';
        details.append(detailsHeading);
        for (const [name, area] of [
          ['Aluminio', order.aluminio], ['Vidrio', order.vidrio], ['Ensamble', order.ensamble],
        ]) {
          const status = document.createElement('p');
          status.textContent = `${name}: ${area.hechas} de ${area.requeridas}`
            + (area.porcentaje === null ? ' · sin plan' : ` · ${area.porcentaje} %`);
          details.append(status);
          if (area.porcentaje !== null) {
            const progress = document.createElement('progress');
            progress.max = 100;
            progress.value = area.porcentaje;
            progress.setAttribute('aria-label', `Avance de ${name.toLowerCase()} del pedido ${order.etiqueta ?? order.id}`);
            details.append(progress);
          }
        }
        item.append(details);
      }
      list.append(item);
    }
  } catch {
    list.textContent = 'No se pudo cargar la lista de pedidos.';
  }
}

async function openOrder(id) {
  const requestedOrderId = Number(id);
  if (currentOrderId !== requestedOrderId) {
    exitMeasureEdit();
    currentOrderId = null;
    currentOrderData = null;
  }
  capture.hidden = true;
  detail.hidden = true;
  message.hidden = true;
  errorReturn.hidden = true;

  try {
    const response = await fetch(`/api/pedidos/${encodeURIComponent(id)}`);
    if (!response.ok) throw new Error(response.status === 404 ? 'Pedido no encontrado.' : 'No se pudo consultar el pedido.');
    const order = await response.json();
    if (currentOrderId !== order.id) {
      currentOrderId = order.id;
      showArea('medidas');
      document.querySelector('#client-details').open = false;
    }
    currentOrderData = order;
    exitMeasureEdit();
    document.querySelector('#order-title').textContent = order.etiqueta === null
      ? `Pedido ${order.id} · sin etiqueta`
      : `Pedido ${order.etiqueta}`;
    clientForm.dataset.orderId = order.id;
    for (const field of ['nombre', 'apellido_1', 'apellido_2', 'celular', 'direccion']) {
      clientForm.elements[field].value = order.cliente?.[field] ?? '';
    }
    clientForm.elements.notas.value = order.notas;
    document.querySelector('#client-status').textContent = order.cliente
      ? 'Datos del cliente guardados. Puedes corregirlos aquí.'
      : 'Faltan los datos del cliente.';
    clientForm.querySelector('button[type="submit"]').textContent = order.cliente
      ? 'Guardar correcciones' : 'Guardar datos del cliente';
    const aluminum = document.querySelector('#order-aluminum');
    const glass = document.querySelector('#order-glass');
    const assemblyList = document.querySelector('#order-assembly');
    for (const panel of [measures, discardedList, aluminum, glass, assemblyList]) panel.replaceChildren();
    discardedSection.hidden = !order.ventanas_descartadas.length;
    if (!order.ventanas.length) {
      measures.textContent = 'No hay ventanas activas en este pedido.';
      for (const panel of [aluminum, glass, assemblyList]) {
        panel.textContent = 'No hay ventanas activas en este pedido.';
      }
    }
    for (const window of order.ventanas) {
      const measureSection = document.createElement('section');
      const measureHeading = document.createElement('h3');
      measureHeading.textContent = `Ventana ${window.codigo ?? window.numero}`;
      const measureValue = document.createElement('p');
      measureValue.textContent = `${window.ancho} × ${window.alto}`;
      const discardButton = document.createElement('button');
      discardButton.type = 'button';
      discardButton.textContent = `Descartar ventana ${window.codigo ?? window.numero}`;
      discardButton.addEventListener('click', () => changeWindowDiscard(window, true, discardButton));
      measureSection.append(measureHeading, measureValue, discardButton);
      measures.append(measureSection);
      const assembly = assemblyRow(window, order.id);
      const refreshWindowProgress = () => {
        assembly.refresh();
        updateMeasureEditButton(order);
      };
      const assemblyHeading = document.createElement('h3');
      assemblyHeading.textContent = `Ventana ${window.codigo ?? window.numero}`;
      assemblyList.append(assemblyHeading, assembly.row);
      const aluminumHeading = document.createElement('h3');
      aluminumHeading.textContent = `Ventana ${window.codigo ?? window.numero}`;
      aluminum.append(aluminumHeading);
      if (!window.plan_aluminio.length) {
        const notice = document.createElement('p');
        notice.textContent = 'Plan de aluminio no disponible para este pedido anterior.';
        aluminum.append(notice);
      } else if (window.plan_aluminio.length !== 10 || window.avance_aluminio.length !== 10) {
        const notice = document.createElement('p');
        notice.textContent = 'El plan de aluminio está incompleto.';
        aluminum.append(notice);
      } else {
        const note = document.createElement('p');
        note.textContent = 'Cortado indica que el corte físico se realizó.';
        aluminum.append(note);
        const plan = document.createElement('ul');
        const labels = [
          'Jamba', 'Mulio', 'Vertical fijo', 'Aleta', 'Horizontal fijo',
          'Horizontal corredizo', 'Guía', 'Riel', 'Screen horizontal', 'Screen vertical',
        ];
        for (const [index, label] of labels.entries()) {
          const line = document.createElement('li');
          line.append(aluminumCutRow(window, window.plan_aluminio[index], window.avance_aluminio[index], label, refreshWindowProgress));
          plan.append(line);
        }
        aluminum.append(plan);
      }
      const glassHeading = document.createElement('h3');
      glassHeading.textContent = `Ventana ${window.codigo ?? window.numero}`;
      glass.append(glassHeading);
      if (window.plan_vidrio && window.avance_vidrio) {
        glass.append(glassCutRow(window, refreshWindowProgress));
      } else {
        const notice = document.createElement('p');
        notice.textContent = 'Plan de vidrio no disponible para este pedido anterior.';
        glass.append(notice);
      }
    }
    for (const window of order.ventanas_descartadas) {
      const section = document.createElement('section');
      const heading = document.createElement('h4');
      heading.textContent = `Ventana ${window.codigo ?? window.numero}`;
      const measures = document.createElement('p');
      measures.textContent = `${window.ancho} × ${window.alto}`;
      const restoreButton = document.createElement('button');
      restoreButton.type = 'button';
      restoreButton.textContent = `Reincorporar ventana ${window.codigo ?? window.numero}`;
      restoreButton.addEventListener('click', () => changeWindowDiscard(window, false, restoreButton));
      section.append(heading, measures, restoreButton);
      discardedList.append(section);
    }
    updateMeasureEditButton(order);
    detail.hidden = false;
    await loadOrders();
  } catch (error) {
    showError(error.message);
    errorReturn.hidden = false;
  }
}

async function changeWindowDiscard(item, discard, button) {
  message.hidden = true;
  if (discard) {
    const aluminumCuts = item.avance_aluminio.reduce((total, cut) => total + cut.cortadas, 0);
    const glassCuts = item.avance_vidrio?.cortadas ?? 0;
    const assembly = item.ensamblada ? ' Sí está marcada como ensamblada.' : ' No está marcada como ensamblada.';
    if (!window.confirm(`¿Descartar la ventana ${item.codigo ?? item.numero}? Tiene ${aluminumCuts} cortes de aluminio y ${glassCuts} cortes de vidrio marcados.${assembly} Se conservarán sus datos y marcas.`)) return;
  }
  button.disabled = true;
  try {
    const response = await fetch(`/api/ventanas/${item.id}/descarte`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ descartada: discard, confirmar_descarte: discard }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo actualizar la ventana.');
    }
    await openOrder(currentOrderId);
  } catch (error) {
    showError(error.message);
    button.disabled = false;
  }
}

clientForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  message.hidden = true;
  const button = clientForm.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const details = Object.fromEntries(
      ['nombre', 'apellido_1', 'apellido_2', 'celular', 'direccion', 'notas']
        .map((field) => [field, clientForm.elements[field].value.trim()]),
    );
    for (const [field, label] of [
      ['nombre', 'nombre'], ['apellido_1', 'primer apellido'], ['apellido_2', 'segundo apellido'],
    ]) {
      if (/\p{N}/u.test(details[field])) {
        clientForm.elements[field].focus();
        showError(`El ${label} no puede contener números.`);
        return;
      }
    }
    const response = await fetch(`/api/pedidos/${clientForm.dataset.orderId}/cliente`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(details),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudieron guardar los datos del cliente.');
    }
    await openOrder(clientForm.dataset.orderId);
  } catch (error) {
    showError(error.message);
  } finally {
    button.disabled = false;
  }
});

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
    exitMeasureEdit();
    currentOrderId = null;
    currentOrderData = null;
    detail.hidden = true;
    capture.hidden = false;
    message.hidden = true;
    errorReturn.hidden = true;
  }
});

const match = location.pathname.match(/^\/pedidos\/(\d+)$/);
loadOrders();
if (match) openOrder(match[1]);
else exitMeasureEdit();
