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
const deliveryForm = document.querySelector('#delivery-form');
const deliveryAmount = document.querySelector('#delivery-amount');
const deliveryActions = document.querySelector('#delivery-actions');
const deliveryEdit = document.querySelector('#delivery-edit');
const measureEditButton = document.querySelector('#edit-measures');
const measureEditForm = document.querySelector('#measure-edit-form');
const measureEditRows = document.querySelector('#measure-edit-rows');
const areaButtons = [...document.querySelectorAll('#area-nav button')];
const areaPanels = [...document.querySelectorAll('[data-area-panel]')];
let currentOrderId = null;
let currentOrderData = null;
let nextRowId = 1;

const clientFields = ['nombre', 'apellido_1', 'apellido_2', 'celular', 'direccion', 'notas'];
const clientView = document.querySelector('#client-view');
const clientEdit = document.querySelector('#client-edit');
const orderEdit = document.querySelector('#edit-order');
const orderEditActions = document.querySelector('#order-edit-actions');
const orderEditDate = document.querySelector('#order-edit-date');
const orderEditDateValue = document.querySelector('#order-edit-date-value');
const orderEditDateReason = document.querySelector('#order-edit-date-reason');
const orderEditDateReasonValue = document.querySelector('#order-edit-date-reason-value');
const orderEditDateOther = document.querySelector('#order-edit-date-other');
const orderEditDateOtherValue = document.querySelector('#order-edit-date-other-value');
let orderEditActive = false;

function clientOriginal(field) {
  return field === 'notas' ? currentOrderData?.notas ?? '' : currentOrderData?.cliente?.[field] ?? '';
}
function dirtyBlocks(except = '') {
  if (!currentOrderData) return [];
  if (except === 'pedido') return [];
  const dirty = [];
  if (orderEditActive && except !== 'pedido') {
    if ([...measureEditRows.children].some(row => row.querySelector('[name="ancho"]').value.trim() !== row.dataset.originalWidth || row.querySelector('[name="alto"]').value.trim() !== row.dataset.originalHeight)
      || clientFields.some(field => clientForm.elements[field].value.trim() !== clientOriginal(field))
      || Number(deliveryAmount.value || 0) !== Number(currentOrderData.traslado || 0)
      || orderEditDateValue.value !== (currentOrderData.fecha_programada ?? '')
      || document.querySelector('#waste-included').checked !== Boolean(currentOrderData.merma?.incluida)) dirty.push('el pedido');
    return dirty;
  }
  if (except !== 'cliente' && !clientForm.hidden && clientFields.some(field => clientForm.elements[field].value !== clientOriginal(field))) dirty.push('cliente y notas');
  const originalDelivery = currentOrderData.traslado ?? '';
  const deliveryChanged = deliveryAmount.value === '' || originalDelivery === ''
    ? deliveryAmount.value !== originalDelivery : Number(deliveryAmount.value) !== Number(originalDelivery);
  if (except !== 'traslado' && !deliveryAmount.disabled && deliveryChanged) dirty.push('traslado');
  const date = document.querySelector('#installation-date');
  if (except !== 'fecha' && !date.disabled && (date.value !== (currentOrderData.fecha_programada ?? '') || (!document.querySelector('#reschedule-reason').hidden && (document.querySelector('#reschedule-reason-select').value || document.querySelector('#reschedule-other').value)))) dirty.push('fecha de instalación');
  return dirty;
}
function confirmPending(except = '', discard = false) {
  const dirty = dirtyBlocks(except);
  if (!dirty.length) return true;
  const warning = discard ? ' Si continúas, esos cambios se descartarán. Cancela para guardarlos primero.' : '';
  return window.confirm(`Hay cambios sin guardar en ${dirty.join(', ')}.${warning} ¿Continuar?`);
}
const originalFetch = window.fetch.bind(window);
function wholePesosFromCents(cents) { return Math.floor((Number(cents) + 50) / 100); }
function wholePesosFromAmount(amount) { return wholePesosFromCents(Math.round(Number(amount) * 100)); }
window.fetch = async (url, options = {}) => {
  if (options.method && !['GET', 'HEAD'].includes(options.method.toUpperCase())) {
    const path = String(url);
    const own = path.includes('/revision-medidas') ? 'pedido' : path.endsWith('/cliente') ? 'cliente' : path.endsWith('/traslado') ? 'traslado' : path.endsWith('/fecha-programada') ? 'fecha' : '';
    if (!confirmPending(own, true)) {
      const error = new Error('Acción cancelada.'); error.pendingCancelled = true; throw error;
    }
  }
  return originalFetch(url, options);
};
window.addEventListener('beforeunload', event => {
  if (dirtyBlocks().length || captureHasChanges()) { event.preventDefault(); event.returnValue = ''; }
});

function showClient(order) {
  clientView.replaceChildren();
  for (const [label, value] of [['Nombre', [order.cliente?.nombre, order.cliente?.apellido_1, order.cliente?.apellido_2].filter(Boolean).join(' ')], ['Celular', order.cliente?.celular], ['Dirección', order.cliente?.direccion], ['Notas del pedido', order.notas]]) {
    const line = document.createElement('p'); line.textContent = `${label}: ${value || 'Sin datos'}`; clientView.append(line);
  }
  for (const field of clientFields) clientForm.elements[field].value = clientOriginal(field);
  clientForm.hidden = true; clientEdit.hidden = true; clientView.hidden = false;
}
clientEdit.addEventListener('click', () => {
  clientView.hidden = true; clientEdit.hidden = true; clientForm.hidden = false;
  clientForm.elements.nombre.focus();
});
document.querySelector('#client-cancel').addEventListener('click', () => showClient(currentOrderData));

function showArea(area) {
  const workshop = ['aluminio', 'vidrio', 'ensamble'].includes(area);
  document.body.classList.add('order-active');
  for (const button of areaButtons) {
    button.setAttribute('aria-pressed', String(button.dataset.area === area));
  }
  for (const panel of areaPanels) {
    panel.hidden = panel.id !== `area-${workshop ? 'taller' : area}`;
  }
  for (const panel of document.querySelectorAll('[data-workshop-panel]')) {
    panel.hidden = panel.id !== `workshop-${area}`;
  }
}

for (const button of areaButtons) {
  button.addEventListener('click', () => {
    if (button.getAttribute('aria-pressed') === 'true' || confirmPending()) showArea(button.dataset.area);
  });
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
    schedulePreview();
  });
  rows.append(row);
  numberRows();
}

document.querySelector('#add-row').addEventListener('click', () => { addRow(); schedulePreview(); });
addRow();

function showError(text) {
  if (text === 'Acción cancelada.') return;
  message.textContent = text;
  message.hidden = false;
}

function updateMeasureEditButton(order = currentOrderData) {
  measureEditButton.hidden = true;
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

orderEdit.addEventListener('click', () => {
  if (!currentOrderData || currentOrderData.instalado) return;
  orderEditActive = true;
  orderEdit.hidden = true;
  orderEditActions.hidden = false;
  enterMeasureEdit();
  clientView.hidden = true;
  clientForm.hidden = false;
  deliveryAmount.disabled = false;
  document.querySelector('#waste-included').disabled = !(currentOrderData.merma && currentOrderData.merma_vidrio);
  orderEditDate.hidden = !currentOrderData.aceptado;
  orderEditDateValue.value = currentOrderData.fecha_programada ?? '';
  orderEditDateValue.required = currentOrderData.aceptado;
  orderEditDateReasonValue.value = '';
  orderEditDateOtherValue.value = '';
  orderEditDateReason.hidden = true;
  orderEditDateOther.hidden = true;
});
document.querySelector('#cancel-order-edit').addEventListener('click', () => {
  orderEditActive = false;
  openOrder(currentOrderId);
});
orderEditDateValue.addEventListener('input', () => {
  orderEditDateReason.hidden = !currentOrderData.fecha_programada || orderEditDateValue.value === currentOrderData.fecha_programada;
  orderEditDateOther.hidden = orderEditDateReason.hidden || orderEditDateReasonValue.value !== 'Otros';
});
orderEditDateReasonValue.addEventListener('change', () => {
  orderEditDateOther.hidden = orderEditDateReasonValue.value !== 'Otros';
});

document.querySelector('#save-order-edit').addEventListener('click', async event => {
  if (!orderEditActive || !currentOrderData) return;
  if (!clientForm.reportValidity() || !deliveryForm.reportValidity()) return;
  const changes = [...measureEditRows.children].map(row => ({
    id: Number(row.dataset.windowId), ancho: row.querySelector('[name="ancho"]').value.trim(),
    alto: row.querySelector('[name="alto"]').value.trim(),
    oldWidth: row.dataset.originalWidth, oldHeight: row.dataset.originalHeight,
  })).filter(row => row.ancho !== row.oldWidth || row.alto !== row.oldHeight);
  if (changes.some(row => !row.ancho || !row.alto)) { showError('Completa ambas medidas de cada ventana modificada.'); return; }
  const payload = {ventanas: changes.map(({id, ancho, alto}) => ({id, ancho, alto}))};
  if (currentOrderData.aceptado && !orderEditDateValue.value) { showError('Ingresa la fecha programada de instalación.'); orderEditDateValue.focus(); return; }
  const client = Object.fromEntries(clientFields.map(field => [field, clientForm.elements[field].value.trim()]));
  if (clientFields.some(field => client[field] !== clientOriginal(field))) payload.cliente = client;
  if (Number(deliveryAmount.value || 0) !== Number(currentOrderData.traslado || 0))
    payload.traslado = deliveryAmount.value === '' ? null : deliveryAmount.value;
  const wasteIncluded = document.querySelector('#waste-included').checked;
  if (wasteIncluded !== Boolean(currentOrderData.merma?.incluida)) payload.incluir_merma = wasteIncluded;
  if (currentOrderData.aceptado && orderEditDateValue.value !== (currentOrderData.fecha_programada ?? '')) {
    if (!orderEditDateValue.value || !orderEditDateValue.validity.valid) { showError('Ingresa una fecha programada válida.'); return; }
    payload.fecha_programada = orderEditDateValue.value;
    if (currentOrderData.fecha_programada) {
      if (!orderEditDateReasonValue.value || (orderEditDateReasonValue.value === 'Otros' && !orderEditDateOtherValue.value.trim())) {
        showError('Selecciona y completa el motivo de reprogramación.'); return;
      }
      payload.motivo = orderEditDateReasonValue.value;
      payload.motivo_otro = orderEditDateOtherValue.value.trim();
    }
  }
  const pendingPrice = currentOrderData.ventanas.some(item => item.costo_materiales?.precio == null);
  const changedPendingMeasure = changes.some(row => currentOrderData.ventanas.find(item => item.id === row.id)?.costo_materiales?.precio == null);
  if (pendingPrice && (Object.keys(payload).length === 1 || changedPendingMeasure)) payload.actualizar_precios = true;
  if (Object.keys(payload).length === 1 && !payload.ventanas.length) { message.textContent = 'No hay cambios que guardar.'; message.hidden = false; return; }
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const orderId = currentOrderData.id;
    const previewResponse = await fetch(`/api/pedidos/${orderId}/revision-medidas/previa`, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload),
    });
    const preview = await previewResponse.json().catch(() => ({}));
    if (!previewResponse.ok) throw new Error(typeof preview.detail === 'string' ? preview.detail : 'No se pudo revisar el pedido.');
    const priceAffected = payload.ventanas.length || payload.actualizar_precios || 'traslado' in payload || 'incluir_merma' in payload;
    const decision = await reviewMeasurePrices(preview, priceAffected);
    if (decision === 'cancelar') return;
    const response = await fetch(`/api/pedidos/${orderId}/revision-medidas`, {
      method: 'PUT', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({...payload, version: preview.version, decision}),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo guardar el pedido.');
    orderEditActive = false;
    await openOrder(orderId);
    message.textContent = 'Cambios del pedido guardados.';
    message.hidden = false;
  } catch (error) { showError(error.message); }
  finally { button.disabled = false; }
});

function reviewMeasurePrices(preview, priceAffected = true) {
  const dialog = document.querySelector('#measure-price-review');
  const details = document.querySelector('#measure-price-review-details');
  document.querySelector('#measure-price-review-title').textContent = priceAffected ? 'Revisar cambio de precio' : 'Confirmar cambios del pedido';
  const conserve = dialog.querySelector('[value="conservar"]');
  conserve.hidden = preview.ventanas.some(item => item.anterior.precio == null);
  conserve.textContent = priceAffected ? 'Conservar precio y guardar' : 'Guardar cambios';
  dialog.querySelector('[value="actualizar"]').hidden = !priceAffected;
  const money = value => value == null ? 'Pendiente' : `$${value}`;
  details.replaceChildren();
  for (const item of preview.ventanas) {
    const line = document.createElement('p');
    line.textContent = `${item.codigo ?? `Ventana ${item.id}`}: ${item.anterior.ancho} × ${item.anterior.alto} (${money(item.anterior.precio)}) → ${item.nueva.ancho} × ${item.nueva.alto} (${money(item.nueva.precio)})`;
    details.append(line);
  }
  const summary = document.createElement('p');
  const difference = preview.total_anterior == null || preview.total_nuevo == null ? ''
    : ` (diferencia: ${preview.total_nuevo - preview.total_anterior >= 0 ? '+' : ''}$${preview.total_nuevo - preview.total_anterior})`;
  const transfer = preview.traslado_anterior !== preview.traslado_nuevo
    ? `Traslado: ${preview.traslado_anterior == null ? 'Sin cargo' : money(wholePesosFromAmount(preview.traslado_anterior))} → ${preview.traslado_nuevo == null ? 'Sin cargo' : money(wholePesosFromAmount(preview.traslado_nuevo))}. ` : '';
  summary.textContent = `${transfer}Merma: ${money(wholePesosFromAmount(preview.merma_anterior))} → ${money(wholePesosFromAmount(preview.merma_nueva))}. Total del pedido: ${money(preview.total_anterior)} → ${money(preview.total_nuevo)}${difference}.`;
  details.append(summary);
  return new Promise(resolve => {
    const select = event => {
      const button = event.target.closest('button[value]');
      if (button) { dialog.close(button.value); resolve(button.value); }
    };
    const cancel = () => resolve('cancelar');
    dialog.addEventListener('click', select);
    dialog.addEventListener('cancel', cancel, {once: true});
    dialog.addEventListener('close', () => {
      dialog.removeEventListener('click', select);
      dialog.removeEventListener('cancel', cancel);
      resolve('cancelar');
    }, {once: true});
    dialog.showModal();
  });
}

measureEditForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (orderEditActive) { document.querySelector('#save-order-edit').click(); return; }
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
    + 'y quitará las marcas que ya no correspondan. Los códigos de ventana se conservan. ¿Revisar el precio antes de guardar?',
  );
  if (!confirmed) return;

  submit.disabled = true;
  cancel.disabled = true;
  try {
    const orderId = currentOrderData.id;
    const windows = changes.map(({ id, ancho, alto }) => ({ id, ancho, alto }));
    const previewResponse = await fetch(`/api/pedidos/${orderId}/revision-medidas/previa`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ventanas: windows}),
    });
    if (!previewResponse.ok) {
      const error = await previewResponse.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo revisar el cambio de precio.');
    }
    const preview = await previewResponse.json();
    const decision = await reviewMeasurePrices(preview);
    if (decision === 'cancelar') return;
    const response = await fetch(`/api/pedidos/${orderId}/revision-medidas`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ventanas: windows, version: preview.version, decision,
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
  mark.setAttribute('aria-label', `Marcar corte de ${label} para ${window.codigo ?? window.numero}`);
  undo.setAttribute('aria-label', `Deshacer marca de ${label} para ${window.codigo ?? window.numero}`);

  function refresh() {
    status.textContent = `${label}: ${cut.longitud}″ · requerido ${cut.cantidad}, cortado ${progress.cortadas}, pendiente ${progress.pendientes}`;
    mark.disabled = currentOrderData.instalado || !currentOrderData.aceptado || progress.cortadas >= cut.cantidad;
    undo.disabled = currentOrderData.instalado || !currentOrderData.aceptado || progress.cortadas <= 0 || window.ensamblada;
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
      await openOrder(currentOrderId);
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
  mark.setAttribute('aria-label', `Marcar corte de vidrio para ${window.codigo ?? window.numero}`);
  undo.setAttribute('aria-label', `Deshacer marca de vidrio para ${window.codigo ?? window.numero}`);
  const plan = window.plan_vidrio;
  const progress = window.avance_vidrio;

  function refresh() {
    status.textContent = `Vidrio: ${plan.ancho}″ × ${plan.alto}″ · cortados: ${progress.cortadas} de ${plan.cantidad} · pendientes: ${progress.pendientes}`;
    mark.disabled = currentOrderData.instalado || !currentOrderData.aceptado || progress.cortadas >= plan.cantidad;
    undo.disabled = currentOrderData.instalado || !currentOrderData.aceptado || progress.cortadas <= 0 || window.ensamblada;
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
      await openOrder(currentOrderId);
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
  mark.setAttribute('aria-label', `Confirmar ensamble de ${window.codigo ?? window.numero}`);
  undo.setAttribute('aria-label', `Deshacer ensamble de ${window.codigo ?? window.numero}`);

  function refresh() {
    const complete = window.plan_aluminio.length === 10
      && window.avance_aluminio.length === 10
      && window.avance_aluminio.every((cut) => cut.pendientes === 0)
      && window.plan_vidrio && window.avance_vidrio
      && window.avance_vidrio.pendientes === 0;
    status.textContent = `Ensamble de ${window.codigo ?? window.numero}: ${window.ensamblada ? 'ensamblada' : 'pendiente'}`;
    mark.disabled = currentOrderData.instalado || !currentOrderData.aceptado || window.ensamblada || !complete;
    undo.disabled = currentOrderData.instalado || !currentOrderData.aceptado || !window.ensamblada;
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
    const historyResponse = await fetch('/api/pedidos/historico');
    if (!historyResponse.ok) throw new Error();
    const history = await historyResponse.json();
    const historyList = document.querySelector('#history-list');
    historyList.replaceChildren();
    if (!history.pedidos.length) historyList.textContent = 'No hay pedidos finalizados.';
    for (const order of history.pedidos) {
      const line = document.createElement('p');
      const link = document.createElement('a'); link.href = `/pedidos/${order.id}?origen=historico`;
      link.textContent = `Pedido ${order.id} · cerrado el ${order.fecha_cierre}`;
      line.append(link); historyList.append(line);
    }
    const response = await fetch('/api/pedidos/avance');
    if (!response.ok) throw new Error();
    const data = await response.json();
    list.replaceChildren();
    const budgetsResponse = await fetch('/api/pedidos');
    if (!budgetsResponse.ok) throw new Error();
    const allOrders = await budgetsResponse.json();
    const budgetList = document.querySelector('#budget-list'); budgetList.replaceChildren();
    const budgets = allOrders.pedidos.filter(order => !order.aceptado).sort((a, b) => (b.fecha_creacion ?? '').localeCompare(a.fecha_creacion ?? '') || b.id - a.id);
    if (!budgets.length) budgetList.textContent = 'No hay presupuestos pendientes.';
    for (const order of budgets) {
      const line = document.createElement('p');
      const link = document.createElement('a'); link.href = `/pedidos/${order.id}?origen=presupuestos`;
      link.textContent = `Presupuesto ${order.id} · ${order.fecha_creacion ? new Date(order.fecha_creacion).toLocaleDateString('es-MX', {timeZone: 'America/Tijuana'}) : 'Fecha de creación no disponible'}`; line.append(link); budgetList.append(line);
    }
    if (!data.pedidos.length) {
      list.textContent = 'Aún no hay pedidos.';
      return;
    }
    for (const [index, order] of data.pedidos.entries()) {
      const item = document.createElement('article');
      item.className = 'order-card';
      const heading = document.createElement('h3');
      const link = document.createElement('a');
      link.href = `/pedidos/${order.id}?origen=pedidos`;
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
      if (order.instalacion_atrasada) {
        const late = document.createElement('p'); late.textContent = 'Instalación atrasada'; item.append(late);
      }
      if (order.instalado) {
        const installed = document.createElement('p'); installed.textContent = 'Instalado ✓'; item.append(installed);
      } else if (order.listo_instalacion) {
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

function formatMaterialConsumption(item) {
  if (item.codigo !== 'pasta' || item.unidad !== 'pulgada lineal') {
    return `${item.cantidad} ${item.unidad}`;
  }
  // Each tube covers 312 inches; round up only the displayed supply quantity.
  const quarters = Math.ceil(Number(item.cantidad) / 78);
  const whole = Math.floor(quarters / 4);
  const fraction = ['', '1/4', '1/2', '3/4'][quarters % 4];
  const quantity = [whole || '', fraction].filter(Boolean).join(' ') || '0';
  return `≈ ${quantity} ${quarters === 4 ? 'tubo' : 'tubos'}`;
}

function renderWindowCost(window, container) {
  const panel = document.createElement('section');
  panel.className = 'window-cost';
  const heading = document.createElement('h4');
  heading.textContent = 'Costo base de materiales';
  const explanation = document.createElement('p');
  explanation.textContent = 'No incluye servicios.';
  panel.append(heading, explanation);

  const cost = window.costo_materiales;
  if (cost) {
    const total = document.createElement('p');
    total.textContent = `Precio de la ventana: $${cost.costo_base}`;
    panel.append(total);
    if (cost.porcentaje_ganancia !== undefined) {
      const profit = document.createElement('p');
      profit.textContent = `Ganancia (${cost.porcentaje_ganancia}%): $${cost.ganancia}`;
      const price = document.createElement('p');
      price.textContent = `Total: $${cost.precio}`;
      panel.append(profit, price);
    } else {
      const notice = document.createElement('p');
      notice.textContent = 'Este cálculo anterior no incluye ganancia. Edita el pedido para revisar el precio.';
      panel.append(notice);
    }
    if (!cost.vigente) {
      const stale = document.createElement('p');
      stale.textContent = 'Las medidas o el plan cambiaron después de este cálculo. Edita el pedido para revisar el precio.';
      panel.append(stale);
    }
    const breakdown = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Ver desglose de materiales';
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const header = document.createElement('tr');
    for (const label of ['Material', 'Consumo', 'Costo']) {
      const cell = document.createElement('th');
      cell.scope = 'col';
      cell.textContent = label;
      header.append(cell);
    }
    thead.append(header);
    const tbody = document.createElement('tbody');
    for (const item of cost.items) {
      const row = document.createElement('tr');
      for (const value of [item.nombre, formatMaterialConsumption(item), `$${item.costo}`]) {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.append(cell);
      }
      tbody.append(row);
    }
    table.append(thead, tbody);
    breakdown.append(summary, table);
    panel.append(breakdown);
  } else {
    const notice = document.createElement('p');
    notice.textContent = 'Aún no se ha calculado.';
    panel.append(notice);
  }

  container.append(panel);
}

async function openOrder(id) {
  const origins = {dashboard: ['Dashboard', '/'], pedidos: ['Pedidos', '/?vista=pedidos'], presupuestos: ['Presupuestos', '/?vista=presupuestos'], historico: ['Histórico', '/?vista=historico']};
  const [originLabel, originUrl] = origins[new URLSearchParams(location.search).get('origen')] ?? origins.dashboard;
  const back = document.querySelector('#order-back');
  back.href = originUrl;
  back.textContent = `Volver a ${originLabel}`;
  const requestedOrderId = Number(id);
  if (currentOrderId !== requestedOrderId) {
    document.body.classList.remove('order-active');
    for (const id of ['budgets', 'orders', 'history']) document.querySelector(`#${id}`).hidden = true;
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
    document.querySelector('#history-detail')?.remove();
    const eventsView = () => {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = 'Hitos del pedido'; details.append(summary);
      const names = {presupuesto_creado: 'Presupuesto creado', aceptado: 'Anticipo mínimo alcanzado', aceptacion_revocada: 'Aceptación revocada', liquidado: 'Liquidado', liquidacion_perdida: 'Liquidación perdida', instalado: 'Instalado', instalacion_desmarcada: 'Instalación desmarcada', cierre: 'Pedido cerrado'};
      if (!order.eventos.some(event => event.tipo === 'presupuesto_creado')) {
        const line = document.createElement('p'); line.textContent = 'No hay fecha y hora de creación disponibles; los hitos anteriores al registro pueden faltar.'; details.append(line);
      }
      {
        for (const event of order.eventos) {
          const line = document.createElement('p');
          line.textContent = `${names[event.tipo] ?? event.tipo}: ${new Date(event.fecha_hora).toLocaleString('es-MX', {timeZone: 'America/Tijuana'})} (Tijuana)`;
          details.append(line);
        }
      }
      return details;
    };
    const productionView = () => {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = 'Fabricación registrada'; details.append(summary);
      const note = document.createElement('p'); note.textContent = 'Las fechas indican cuándo se registró el trabajo, posiblemente por tandas. Las marcas anteriores a este registro pueden faltar.'; details.append(note);
      const first = order.eventos_fabricacion.find(event => event.accion === 'marcar' && !event.corregido && event.area !== 'ensamble');
      const firstLine = document.createElement('p'); firstLine.textContent = first ? `Primer corte registrado: ${new Date(first.fecha_hora).toLocaleString('es-MX', {timeZone: 'America/Tijuana'})} (Tijuana)` : 'Primer corte registrado: no disponible'; details.append(firstLine);
      const log = document.createElement('details'); const logTitle = document.createElement('summary'); logTitle.textContent = 'Ver registros y correcciones'; log.append(logTitle);
      for (const event of order.eventos_fabricacion) {
        const line = document.createElement('p');
        line.textContent = `${new Date(event.fecha_hora).toLocaleString('es-MX', {timeZone: 'America/Tijuana'})} · Ventana ${event.ventana} · ${event.area} · ${event.accion === 'marcar' ? 'registrado' : 'corrección manual'}${event.corregido ? ' (corregido)' : ''}${event.accion === 'deshacer' && !event.original_id ? ' (marca anterior sin fecha disponible)' : ''}`;
        log.append(line);
      }
      details.append(log);
      const controls = document.createElement('p');
      const dateLabel = document.createElement('label'); dateLabel.textContent = 'Fecha de referencia ';
      const day = document.createElement('input'); day.type = 'date'; day.value = new Intl.DateTimeFormat('en-CA', {timeZone: 'America/Tijuana'}).format(new Date()); dateLabel.append(day);
      const periodLabel = document.createElement('label'); periodLabel.textContent = ' Periodo ';
      const period = document.createElement('select');
      for (const [value, name] of [['dia', 'Día'], ['semana', 'Semana'], ['mes', 'Mes'], ['ano', 'Año']]) { const option = document.createElement('option'); option.value = value; option.textContent = name; period.append(option); }
      periodLabel.append(period); controls.append(dateLabel, periodLabel); details.append(controls);
      const results = document.createElement('div'); details.append(results);
      function showCounts() {
        results.replaceChildren();
        if (!day.value) return;
        const start = new Date(`${day.value}T00:00:00Z`);
        if (period.value === 'semana') start.setUTCDate(start.getUTCDate() - (start.getUTCDay() + 6) % 7);
        if (period.value === 'mes' || period.value === 'ano') start.setUTCDate(1);
        if (period.value === 'ano') start.setUTCMonth(0);
        const end = new Date(start);
        if (period.value === 'dia') end.setUTCDate(end.getUTCDate() + 1);
        if (period.value === 'semana') end.setUTCDate(end.getUTCDate() + 7);
        if (period.value === 'mes') end.setUTCMonth(end.getUTCMonth() + 1);
        if (period.value === 'ano') end.setUTCFullYear(end.getUTCFullYear() + 1);
        const counts = {};
        for (const event of order.eventos_fabricacion) {
          if (event.accion !== 'marcar' || event.corregido) continue;
          const key = event.fecha_hora.slice(0, 10);
          counts[key] ??= {aluminio: 0, vidrio: 0, ensamble: 0}; counts[key][event.area]++;
        }
        const list = document.createElement('ul'); const total = {aluminio: 0, vidrio: 0, ensamble: 0};
        for (let date = new Date(start); date < end; date.setUTCDate(date.getUTCDate() + 1)) {
          const key = date.toISOString().slice(0, 10); const c = counts[key] ?? {aluminio: 0, vidrio: 0, ensamble: 0};
          for (const area of Object.keys(total)) total[area] += c[area];
          const item = document.createElement('li'); item.textContent = `${key}: aluminio ${c.aluminio}, vidrio ${c.vidrio}, ventanas ensambladas ${c.ensamble}`; list.append(item);
        }
        const heading = document.createElement('p'); heading.textContent = `Total: aluminio ${total.aluminio}, vidrio ${total.vidrio}, ventanas ensambladas ${total.ensamble}`; results.append(heading, list);
      }
      day.addEventListener('change', showCounts); period.addEventListener('change', showCounts); showCounts();
      return details;
    };
    const changesView = () => {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = 'Cambios de medidas y piezas afectadas'; details.append(summary);
      if (!order.cambios_medidas.length) {
        const line = document.createElement('p'); line.textContent = 'No hay cambios registrados después de la aceptación.'; details.append(line);
      }
      for (const change of order.cambios_medidas) {
        const section = document.createElement('section');
        const heading = document.createElement('p');
        heading.textContent = `${new Date(change.fecha_hora).toLocaleString('es-MX', {timeZone: 'America/Tijuana'})} (Tijuana) · Ventana ${change.ventana}: ${change.anterior.ancho} × ${change.anterior.alto} → ${change.nueva.ancho} × ${change.nueva.alto} pulgadas`;
        section.append(heading);
        if (!change.afectadas.length) {
          const line = document.createElement('p'); line.textContent = 'Sin piezas cortadas afectadas.'; section.append(line);
        } else {
          const list = document.createElement('ul');
          for (const piece of change.afectadas) {
            const item = document.createElement('li');
            item.textContent = `${piece.tipo === 'vidrio' ? 'Vidrio' : piece.perfil}: ${piece.cantidad} pieza(s), ${piece.anterior} → ${piece.nueva} pulgadas${piece.clasificacion ? ` · ${piece.clasificacion}` : ''}`;
            list.append(item);
          }
          section.append(list);
        }
        details.append(section);
      }
      return details;
    };
    const scheduleView = () => {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = 'Historial de programación'; details.append(summary);
      if (!order.programaciones.some(item => item.anterior === null)) {
        const line = document.createElement('p'); line.textContent = 'Fecha original de programación no disponible.'; details.append(line);
      }
      for (const item of order.programaciones) {
        const line = document.createElement('p');
        const when = new Date(item.fecha_hora).toLocaleString('es-MX', {timeZone: 'America/Tijuana'});
        line.textContent = item.anterior === null
          ? `Fecha original: ${item.nueva} · registrada ${when} (Tijuana)`
          : `${item.anterior} → ${item.nueva} · ${when} (Tijuana) · ${item.motivo}${item.motivo_otro ? `: ${item.motivo_otro}` : ''}`;
        details.append(line);
      }
      return details;
    };
    if (order.fecha_cierre) {
      document.body.classList.remove('order-active');
      document.querySelector('#history').hidden = true;
      document.querySelector('#budgets').hidden = true;
      document.querySelector('#orders').hidden = true;
      const view = document.createElement('section'); view.id = 'history-detail';
      const title = document.createElement('h1'); title.textContent = `Pedido ${order.id} · finalizado y liquidado`;
      view.append(title, eventsView(), productionView(), changesView(), scheduleView());
      const add = (label, value) => { const p = document.createElement('p'); p.textContent = `${label}: ${value ?? 'Sin dato'}`; view.append(p); };
      add('Fecha de cierre', order.fecha_cierre); add('Fecha de instalación', order.fecha_real); add('Fecha programada', order.fecha_programada);
      const c = order.cliente; add('Cliente', c ? [c.nombre, c.apellido_1, c.apellido_2].filter(Boolean).join(' ') : null);
      if (c) { add('Celular', c.celular); add('Dirección', c.direccion || null); }
      add('Notas', order.notas || null);
      const windowsTitle = document.createElement('p'); windowsTitle.textContent = 'Ventanas:'; view.append(windowsTitle);
      const windows = document.createElement('ol');
      for (const w of [...order.ventanas, ...order.ventanas_descartadas].sort((a, b) => a.numero - b.numero)) {
        const item = document.createElement('li');
        item.append(document.createTextNode(`${w.ancho} × ${w.alto}${w.descartada ? ' (descartada)' : ''}`));
        const cost = document.createElement('p');
        cost.textContent = w.costo_materiales?.costo_base == null ? 'Costo de materiales: Sin dato' : `Costo de materiales: $${w.costo_materiales.costo_base}`;
        item.append(cost); windows.append(item);
      }
      view.append(windows);
      const wastes = [order.merma, order.merma_vidrio].filter(Boolean);
      if (wastes.length) {
        const included = wastes.reduce((sum, waste) => sum + (waste.incluida ? Math.round(Number(waste.cargo) * 100) : 0), 0);
        const total = wastes.reduce((sum, waste) => sum + Math.round(Number(waste.cargo) * 100), 0);
        add('Merma', `$${wholePesosFromCents(total)} · aplicada: $${wholePesosFromCents(included)}`);
      }
      add('Traslado', order.traslado === null ? null : `$${wholePesosFromAmount(order.traslado)}`);
      add('Total del pedido', order.total_pedido === null ? null : `$${order.total_pedido}`);
      const payments = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = `Total pagado neto: $${order.pagado_neto}`; payments.append(summary);
      for (const m of order.movimientos) {
        const line = document.createElement('p');
        line.textContent = `${m.tipo === 'pago' ? 'Pago' : 'Devolución'}: $${m.importe} · ${m.fecha}${m.anulado ? ` · anulado el ${m.fecha_anulacion}` : ''}`;
        payments.append(line);
      }
      view.append(payments);
      const back = document.createElement('a'); back.href = originUrl; back.textContent = `Volver a ${originLabel}`; view.append(back);
      document.querySelector('main').append(view);
      return;
    }
    if (currentOrderId !== order.id) {
      currentOrderId = order.id;
      showArea('resumen');
      document.querySelector('#client-details').open = true;
    }
    currentOrderData = order;
    orderEditActive = false;
    orderEditActions.hidden = true;
    orderEditDate.hidden = true;
    orderEdit.hidden = Boolean(order.instalado);
    document.querySelector('#installation-state').textContent = order.instalado ? `Instalado el ${order.fecha_real}` : 'Aún no instalado.';
    document.querySelector('#installation-toggle').textContent = order.instalado ? 'Desmarcar instalación' : 'Marcar instalado';
    exitMeasureEdit();
    document.querySelector('#order-title').textContent = !order.aceptado
      ? `Presupuesto ${order.id}`
      : order.etiqueta === null ? `Pedido ${order.id} · sin etiqueta`
      : `Pedido ${order.etiqueta}`;
    clientForm.dataset.orderId = order.id;
    showClient(order);
    document.querySelector('#installation-notes').textContent = order.notas || 'Sin notas para la instalación.';
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
    const orderTotal = document.querySelector('#order-total');
    orderTotal.replaceChildren();
    const totalMessage = document.createElement('p');
    if (!order.ventanas.length) {
      totalMessage.textContent = 'No hay total: el pedido no tiene ventanas activas.';
    } else if (order.total_ventanas.importe === null) {
      totalMessage.textContent = 'No hay precios calculados para las ventanas activas.';
    } else if (order.total_ventanas.sin_precio) {
      totalMessage.textContent = `Total parcial de ventanas con precio: $${order.total_ventanas.importe}. Faltan precios de ventanas activas.`;
    } else {
      totalMessage.textContent = `Total de ventanas activas: $${order.total_ventanas.importe}`;
    }
    orderTotal.append(totalMessage);
    document.querySelector('#delivery-value').textContent = order.traslado === null ? 'Sin cargo de traslado.' : `Traslado: $${wholePesosFromAmount(order.traslado)}`;
    deliveryAmount.value = order.traslado ?? '';
    deliveryAmount.disabled = true;
    deliveryActions.hidden = true;
    deliveryEdit.hidden = true;
    const combinedWaste = order.merma && order.merma_vidrio;
    const sameSelection = combinedWaste && order.merma.incluida === order.merma_vidrio.incluida;
    const combinedCents = combinedWaste ? Math.round(Number(order.merma.cargo) * 100) + Math.round(Number(order.merma_vidrio.cargo) * 100) : 0;
    document.querySelector('#waste-value').textContent = !combinedWaste ? 'Calcula la merma de aluminio y vidrio.' : !sameSelection ? 'Las selecciones de merma son distintas; revisa el pedido.' : `Cargo por merma: $${wholePesosFromCents(combinedCents)}${order.merma.incluida ? '' : ' (no aplicado)'}`;
    document.querySelector('#aluminum-waste-value').textContent = order.merma ? `Aluminio: $${wholePesosFromAmount(order.merma.cargo)}` : 'Sin cálculo de aluminio.';
    const wasteDetails = document.querySelector('#waste-details');
    wasteDetails.replaceChildren();
    if (order.merma?.detalle === null) {
      wasteDetails.textContent = 'El desglose de este cálculo anterior no está disponible.';
    } else if (order.merma?.detalle?.length === 0) {
      wasteDetails.textContent = 'No hay sobrantes que generen cargo en este cálculo.';
    } else if (order.merma?.detalle?.length) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = 'Ver desglose de merma';
      const table = document.createElement('table');
      const head = document.createElement('thead');
      const header = document.createElement('tr');
      for (const label of ['Perfil', 'Consumo (pulgadas)', 'Tramo (pies)', 'Sobrante (pulgadas)', 'Importe aproximado']) {
        const cell = document.createElement('th'); cell.scope = 'col'; cell.textContent = label; header.append(cell);
      }
      head.append(header);
      const body = document.createElement('tbody');
      for (const item of order.merma.detalle) {
        const row = document.createElement('tr');
        for (const value of [item.perfil.replace(/\s+(?:de\s+)?aluminio\b/gi, ""), item.consumo, item.tramo_pies, item.sobrante, `$${wholePesosFromAmount(item.importe)}`]) {
          const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
        }
        body.append(row);
      }
      table.append(head, body);
      const note = document.createElement('p');
      note.textContent = 'Los importes por perfil son aproximados; el cargo total se redondea al centavo.';
      details.append(summary, table, note); wasteDetails.append(details);
    }
    const wasteCheck = document.querySelector('#waste-included');
    wasteCheck.disabled = true;
    wasteCheck.checked = order.merma?.incluida ?? false;
    const glassWaste = order.merma_vidrio;
    document.querySelector('#glass-waste-value').textContent = glassWaste === null ? 'La merma de vidrio aún no se ha calculado.' : `Cargo por merma de vidrio: $${wholePesosFromAmount(glassWaste.cargo)}${glassWaste.incluida ? '' : ' (no aplicado)'}`;
    const glassDetails = document.querySelector('#glass-waste-details');
    glassDetails.replaceChildren();
    if (glassWaste?.detalle?.length === 0) {
      glassDetails.textContent = 'No hay sobrantes que generen cargo en este cálculo.';
    } else if (glassWaste?.detalle?.length) {
      const details = document.createElement('details');
      const summary = document.createElement('summary'); summary.textContent = 'Ver desglose de merma de vidrio';
      const table = document.createElement('table'); const head = document.createElement('thead'); const header = document.createElement('tr');
      for (const label of ['Vidrio', 'Consumo (pulgadas²)', 'Hoja (pulgadas)', 'Sobrante (pulgadas²)', 'Importe aproximado']) {
        const cell = document.createElement('th'); cell.scope = 'col'; cell.textContent = label; header.append(cell);
      }
      head.append(header); const body = document.createElement('tbody');
      for (const item of glassWaste.detalle) {
        const row = document.createElement('tr');
      for (const value of [item.vidrio, Math.trunc(Number(item.consumo)), item.hoja, Math.trunc(Number(item.sobrante)), `$${wholePesosFromAmount(item.importe)}`]) {
          const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
        }
        body.append(row);
      }
      table.append(head, body); details.append(summary, table); glassDetails.append(details);
    }
    document.querySelector('#installation-date-error').hidden = true;
    document.querySelector('#reschedule-reason').hidden = true;
    document.querySelector('#reschedule-reason-select').value = '';
    document.querySelector('#reschedule-other').value = '';
    document.querySelector('#installation-date').value = order.fecha_programada ?? '';
    const needsDate = order.aceptado && !order.fecha_programada;
    document.querySelector('#installation-date').disabled = true;
    document.querySelector('#installation-date-actions').hidden = true;
    document.querySelector('#installation-date-edit').hidden = true;
    document.querySelector('#installation-date-status').textContent = order.fecha_programada
      ? `Fecha programada: ${order.fecha_programada}${order.instalacion_atrasada ? ' · Instalación atrasada' : ''}`
      : (order.aceptado ? 'Fecha obligatoria pendiente: registra la fecha programada de instalación.' : 'Sin fecha programada.');
    const paymentStatus = document.querySelector('#payment-status');
    paymentStatus.replaceChildren();
    const statusLines = [order.aceptado ? 'Pedido aceptado' : 'Presupuesto'];
    if (order.anticipo_requerido === null) {
      statusLines.push(order.merma_pendiente ? 'Calcula la merma pendiente y completa los precios antes de registrar movimientos.' : 'Calcula todos los precios para consultar el anticipo y registrar movimientos.');
    } else {
      statusLines.push(`Anticipo requerido (${order.anticipo_minimo}%): $${order.anticipo_requerido}`,
        `Saldo: $${order.saldo}`, `Excedente: $${order.excedente}`);
      if (order.liquidado) statusLines.push('Liquidado');
    }
    if (order.aceptado && !order.fecha_programada) statusLines.push('Fecha de instalación pendiente de registrar.');
    document.querySelector('#pending-installation').hidden = !(order.aceptado && !order.fecha_programada);
    for (const line of statusLines) {
      const paragraph = document.createElement('p'); paragraph.textContent = line; paymentStatus.append(paragraph);
    }
    const paymentList = document.querySelector('#payment-list'); paymentList.replaceChildren();
    for (const movement of order.movimientos) {
      const row = document.createElement('p');
      row.textContent = `${movement.fecha} · ${movement.tipo === 'pago' ? 'Pago' : 'Devolución'}: $${movement.importe}${movement.anulado ? ` · Anulado${movement.fecha_anulacion ? ` el ${movement.fecha_anulacion}` : ''}` : ''}`;
      if (!movement.anulado) {
        const button = document.createElement('button'); button.type = 'button'; button.textContent = 'Anular';
        button.addEventListener('click', async () => {
          if (!window.confirm('¿Anular este movimiento?')) return;
          button.disabled = true;
          try {
            const response = await fetch(`/api/pedidos/${currentOrderId}/movimientos/${movement.id}/anular`, {method: 'POST'});
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(result.detail ?? 'No se pudo anular el movimiento.');
            await openOrder(currentOrderId);
          } catch (error) { showError(error.message); button.disabled = false; }
        });
        row.append(' ', button);
      }
      paymentList.append(row);
    }
    const grandTotal = document.querySelector('#order-grand-total');
    if (order.total_pedido === null) {
      grandTotal.textContent = '';
    } else {
      grandTotal.textContent = `${order.total_ventanas.sin_precio || order.merma_pendiente ? 'Total parcial del pedido' : 'Total del pedido'}: $${order.total_pedido}`;
    }
    if (order.merma_pendiente) grandTotal.textContent += ' Falta calcular la merma incluida.';
    if (order.total_ventanas.desactualizado) {
      const warning = document.createElement('p');
      warning.textContent = 'Hay precios desactualizados por cambios de medidas o planes. Edita el pedido para revisarlos.';
      orderTotal.append(warning);
    }
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
      discardButton.disabled = order.instalado;
      discardButton.textContent = `Descartar ventana ${window.codigo ?? window.numero}`;
      discardButton.addEventListener('click', () => changeWindowDiscard(window, true, discardButton));
      measureSection.append(measureHeading, measureValue, discardButton);
      if (window.costo_materiales?.precio == null) {
        measureSection.classList.add('window-missing-price');
        const warning = document.createElement('p');
        warning.textContent = 'Precio pendiente: esta ventana no está incluida en el total.';
        measureSection.append(warning);
      }
      renderWindowCost(window, measureSection);
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
      restoreButton.disabled = order.instalado;
      restoreButton.textContent = `Reincorporar ventana ${window.codigo ?? window.numero}`;
      restoreButton.addEventListener('click', () => changeWindowDiscard(window, false, restoreButton));
      section.append(heading, measures, restoreButton);
      renderWindowCost(window, section);
      discardedList.append(section);
    }
    updateMeasureEditButton(order);
    clientEdit.hidden = true;
    deliveryEdit.hidden = true;
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

document.querySelector('#waste-recalculate').addEventListener('click', async event => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/merma-conjunta`, {method: 'POST'});
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail ?? 'No se pudo calcular la merma.');
    message.hidden = true;
    await openOrder(currentOrderId);
  } catch (error) { showError(error.message); }
  finally { button.disabled = false; }
});
document.querySelector('#waste-included').addEventListener('change', async event => {
  if (orderEditActive) return;
  const checkbox = event.currentTarget;
  checkbox.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/merma-conjunta`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({incluida: checkbox.checked})});
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail ?? 'No se pudo guardar la selección.');
    message.hidden = true;
    await openOrder(currentOrderId);
  } catch (error) { checkbox.checked = !checkbox.checked; showError(error.message); }
  finally { checkbox.disabled = false; }
});

document.querySelector('#installation-toggle').addEventListener('click', async event => {
  const button = event.currentTarget;
  const installed = !currentOrderData.instalado;
  if (!installed && !window.confirm('¿Desmarcar la instalación? Podrás modificar nuevamente las ventanas y la fabricación.')) return;
  button.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/instalacion`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({instalado: installed, confirmar_desmarcado: !installed})});
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail ?? 'No se pudo actualizar la instalación.');
    message.hidden = true; await openOrder(currentOrderId);
  } catch (error) { showError(error.message); } finally { button.disabled = false; }
});

document.querySelector('#payment-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const button = form.querySelector('button'); button.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/movimientos`, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tipo: form.elements.tipo.value, importe: form.elements.importe.value}),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo registrar el movimiento.');
    form.reset(); message.hidden = true; await openOrder(currentOrderId);
    if (result.aceptado && !result.fecha_programada) {
      showArea('resumen');
      orderEdit.click();
      orderEditDateValue.scrollIntoView({block: 'center'}); orderEditDateValue.focus();
    }
  } catch (error) { showError(error.message); } finally { button.disabled = false; }
});

document.querySelector('#pending-installation').addEventListener('click', () => {
  if (!confirmPending()) return;
  showArea('resumen');
  orderEdit.click();
  orderEditDateValue.focus();
});

const installationDateForm = document.querySelector('#installation-date-form');
const installationDate = document.querySelector('#installation-date');
const installationDateActions = document.querySelector('#installation-date-actions');
const installationDateError = document.querySelector('#installation-date-error');
const installationDateEdit = document.querySelector('#installation-date-edit');
const rescheduleReason = document.querySelector('#reschedule-reason');
const rescheduleSelect = document.querySelector('#reschedule-reason-select');
const rescheduleOtherRow = document.querySelector('#reschedule-other-row');
const rescheduleOther = document.querySelector('#reschedule-other');
function refreshRescheduleReason() {
  rescheduleReason.hidden = !currentOrderData.fecha_programada || installationDate.value === currentOrderData.fecha_programada || !installationDate.value;
  rescheduleOtherRow.hidden = rescheduleReason.hidden || rescheduleSelect.value !== 'Otros';
}

installationDateEdit.addEventListener('click', () => {
  installationDateError.hidden = true;
  installationDate.value = currentOrderData.fecha_programada ?? '';
  installationDate.disabled = false; installationDateActions.hidden = false; installationDateEdit.hidden = true;
  rescheduleSelect.value = ''; rescheduleOther.value = ''; refreshRescheduleReason();
  installationDate.focus();
});
document.querySelector('#installation-date-cancel').addEventListener('click', () => {
  installationDateError.hidden = true;
  installationDate.value = currentOrderData.fecha_programada ?? '';
  installationDate.disabled = true; installationDateActions.hidden = true; installationDateEdit.hidden = false;
  rescheduleReason.hidden = true; rescheduleSelect.value = ''; rescheduleOther.value = '';
});
installationDate.addEventListener('input', () => { installationDateError.hidden = true; refreshRescheduleReason(); });
rescheduleSelect.addEventListener('change', refreshRescheduleReason);
installationDateForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (orderEditActive) return;
  if (!installationDate.value || !installationDate.validity.valid) {
    installationDateError.textContent = 'Ingresa una fecha programada válida para guardar.';
    installationDateError.hidden = false; installationDate.focus(); return;
  }
  if (!rescheduleReason.hidden && (!rescheduleSelect.value || (rescheduleSelect.value === 'Otros' && !rescheduleOther.value.trim()))) {
    installationDateError.textContent = 'Selecciona y completa el motivo de reprogramación.';
    installationDateError.hidden = false; return;
  }
  installationDateError.hidden = true;
  const button = installationDateForm.querySelector('button[type="submit"]'); button.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/fecha-programada`, {
      method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({fecha: installationDate.value, motivo: rescheduleReason.hidden ? null : rescheduleSelect.value, motivo_otro: rescheduleOther.value}),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo guardar la fecha.');
    message.hidden = true; await openOrder(currentOrderId);
  } catch (error) { showError(error.message); } finally { button.disabled = false; }
});

deliveryEdit.addEventListener('click', () => {
  deliveryAmount.value = currentOrderData.traslado ?? '';
  deliveryEdit.hidden = true;
  deliveryActions.hidden = false;
  deliveryAmount.disabled = false;
  deliveryAmount.focus();
});
document.querySelector('#delivery-cancel').addEventListener('click', () => {
  deliveryAmount.value = currentOrderData.traslado ?? '';
  deliveryAmount.disabled = true;
  deliveryActions.hidden = true;
  deliveryEdit.hidden = false;
});
deliveryForm.addEventListener('submit', async event => {
  event.preventDefault();
  if (orderEditActive) { document.querySelector('#save-order-edit').click(); return; }
  if (!deliveryForm.reportValidity()) return;
  const button = deliveryForm.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const response = await fetch(`/api/pedidos/${currentOrderId}/traslado`, {
      method: 'PUT', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({importe: deliveryAmount.value === '' ? null : deliveryAmount.value}),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo guardar el traslado.');
    await openOrder(currentOrderId);
  } catch (error) { showError(error.message); }
  finally { button.disabled = false; }
});

clientForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (orderEditActive) { document.querySelector('#save-order-edit').click(); return; }
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

const captureForm = document.querySelector('#order-form');
function captureHasChanges() {
  if (capture.hidden) return false;
  return [...rows.children].some(row => row.querySelector('.width').value.trim() || row.querySelector('.height').value.trim())
    || clientFields.some(field => captureForm.elements[field].value.trim())
    || Boolean(document.querySelector('#capture-delivery').value) || Boolean(document.querySelector('#capture-payment').value) || !document.querySelector('#capture-waste').checked;
}
let previewVersion = null;
let previewSequence = 0;
let previewTimer;
function captureInput() {
  return {
    ventanas: [...rows.children].map(row => ({ancho: row.querySelector('.width').value.trim(), alto: row.querySelector('.height').value.trim()})),
    traslado: document.querySelector('#capture-delivery').value || null,
    incluir_merma: document.querySelector('#capture-waste').checked,
  };
}
function schedulePreview() {
  previewVersion = null;
  const sequence = ++previewSequence;
  clearTimeout(previewTimer);
  document.querySelector('#capture-preview').textContent = 'Actualizando precios estimados…';
  for (const row of rows.children) row.querySelector('.window-estimate').textContent = 'Actualizando precio estimado…';
  document.querySelector('#capture-estimated-total').textContent = 'Actualizando total estimado…';
  document.querySelector('#capture-payment-summary').textContent = 'Actualizando resumen de la cuenta y anticipo mínimo…';
  document.querySelector('#capture-waste-status').textContent = 'Actualizando merma…';
  previewTimer = setTimeout(() => updatePreview(sequence), 250);
}
async function updatePreview(sequence) {
  try {
    const response = await originalFetch('/api/presupuestos/vista-previa', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(captureInput())});
    const result = await response.json();
    if (sequence !== previewSequence) return;
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo calcular la estimación.');
    previewVersion = result.version;
    const preview = document.querySelector('#capture-preview');
    preview.textContent = '';
    for (const row of rows.children) row.querySelector('.window-estimate').textContent = 'Precio estimado pendiente de medidas completas.';
    let subtotal = 0, priced = 0;
    for (const item of result.ventanas) {
      const row = rows.children[item.fila - 1];
      if (!row) continue;
      if (item.costo.completo) {
        subtotal += Number(item.costo.precio) * 100; priced++;
        row.querySelector('.window-estimate').textContent = `Precio estimado: $${item.costo.precio}`;
      } else {
        row.querySelector('.window-estimate').textContent = `Precio pendiente. Faltan costos de ${item.costo.faltantes.join(', ')}.`;
      }
    }
    for (const error of result.errores) {
      const match = /^Ventana (\d+):\s*(.*)$/.exec(error);
      const row = match && rows.children[Number(match[1]) - 1];
      if (row) row.querySelector('.window-estimate').textContent = match[2];
      else preview.textContent = error;
    }
    const waste = result.merma;
    const wasteDetails = document.querySelector('#capture-waste-details'); wasteDetails.replaceChildren();
    if (waste) {
      for (const [label, amount, details] of [['Aluminio', waste.aluminio, waste.detalle_aluminio], ['Vidrio', waste.vidrio, waste.detalle_vidrio]]) {
        const line = document.createElement('p'); line.textContent = `${label}: $${wholePesosFromCents(amount)}`; wasteDetails.append(line);
        for (const item of details) { const itemLine = document.createElement('p'); itemLine.textContent = `${item.perfil ?? item.vidrio}: sobrante ${item.sobrante}, importe aproximado $${wholePesosFromAmount(item.importe)}`; wasteDetails.append(itemLine); }
      }
    } else wasteDetails.textContent = 'Desglose pendiente.';
    document.querySelector('#capture-waste-status').textContent = waste ? `Merma de aluminio y vidrio: $${wholePesosFromCents(waste.aluminio + waste.vidrio)}${result.incluir_merma ? '' : ' (no incluida)'}` : result.merma_error ? `Merma pendiente: ${result.merma_error}` : 'Merma pendiente de medidas completas.';
    const complete = result.total_completo;
    const transport = result.traslado_centavos || 0;
    const wasteCents = result.incluir_merma && waste ? waste.aluminio + waste.vidrio : 0;
    const totalLabel = complete ? 'Total estimado' : priced ? 'Total estimado parcial' : 'Total estimado no disponible';
    const totalText = result.total_estimado_pesos !== null
      ? `${totalLabel}: $${result.total_estimado_pesos}`
      : `${totalLabel}: faltan precios o medidas completas.`;
    document.querySelector('#capture-estimated-total').textContent = totalText;

    const summary = document.querySelector('#capture-payment-summary');
    const summaryLines = ['Resumen de la cuenta'];
    summaryLines.push(priced === result.ventanas.length && priced > 0
      ? `Ventanas: $${subtotal / 100}`
      : priced > 0 ? `Ventanas con precio disponible: $${subtotal / 100}`
        : 'Ventanas: precio pendiente');
    if (!result.incluir_merma) summaryLines.push(`Traslado: $${wholePesosFromCents(transport)}`, 'Merma: no incluida');
    else if (waste) summaryLines.push(`Traslado y merma: $${wholePesosFromCents(transport + wasteCents)}`);
    else summaryLines.push(`Traslado: $${wholePesosFromCents(transport)}`, 'Merma: pendiente de cálculo');
    summaryLines.push(totalText);
    if (complete) {
      summaryLines.push(`Anticipo mínimo (${result.anticipo_minimo}%): $${result.anticipo_requerido_pesos}`);
    } else summaryLines.push('Anticipo mínimo: disponible cuando el total esté completo.');
    summary.textContent = summaryLines.join('\n');
  } catch (error) {
    if (sequence !== previewSequence) return;
    previewVersion = null; document.querySelector('#capture-preview').textContent = error.message;
    for (const row of rows.children) row.querySelector('.window-estimate').textContent = 'Precio estimado no disponible.';
    document.querySelector('#capture-estimated-total').textContent = 'Total estimado no disponible.';
    document.querySelector('#capture-payment-summary').textContent = 'No se pudo calcular el resumen de la cuenta ni el anticipo mínimo.';
  }
}
captureForm.addEventListener('keydown', event => {
  if (event.key === 'Enter' && event.target.tagName === 'INPUT') event.preventDefault();
});
captureForm.addEventListener('input', event => {
  if (event.target.closest('#window-rows') || event.target.id === 'capture-delivery') schedulePreview();
});
document.querySelector('#capture-waste').addEventListener('change', schedulePreview);
for (const button of document.querySelectorAll('#capture-nav button')) {
  button.addEventListener('click', () => {
    for (const item of document.querySelectorAll('#capture-nav button')) item.setAttribute('aria-pressed', String(item === button));
    for (const panel of document.querySelectorAll('[data-capture-panel]')) panel.hidden = panel.id !== `capture-${button.dataset.capture}`;
  });
}
captureForm.addEventListener('submit', async event => {
  event.preventDefault(); message.hidden = true;
  if (!previewVersion) { showError('Espera a que termine la estimación antes de guardar.'); return; }
  const withPayment = event.submitter?.dataset.payment === 'true';
  const payment = document.querySelector('#capture-payment');
  const tokenKey = 'avao-captura-anticipo';
  if (!withPayment && sessionStorage.getItem(tokenKey)) { showError('Hay un intento de anticipo pendiente de confirmar. Reinténtalo o consulta los pedidos antes de guardar otro.'); return; }
  if (withPayment && (!payment.value || !payment.validity.valid || Number(payment.value) <= 0)) { showError('Ingresa un anticipo válido mayor a cero.'); payment.focus(); return; }
  const client = Object.fromEntries(clientFields.map(field => [field, captureForm.elements[field].value.trim()]));
  if (!client.nombre || !client.apellido_1 || !/^[0-9]{10}$/.test(client.celular)) {
    showError('Completa nombre, primer apellido y celular de diez dígitos.');
    document.querySelector('[data-capture="cliente"]').click(); return;
  }
  const controls = [...captureForm.querySelectorAll('input, textarea, button')];
  const disabled = controls.map(control => control.disabled);
  controls.forEach(control => { control.disabled = true; });
  try {
    let token = sessionStorage.getItem(tokenKey);
    if (withPayment && !token) { token = crypto.randomUUID(); sessionStorage.setItem(tokenKey, token); }
    const body = {...captureInput(), cliente: client, version: previewVersion};
    if (withPayment) { body.importe = payment.value; body.token = token; }
    const response = await originalFetch(withPayment ? '/api/presupuestos/con-anticipo' : '/api/pedidos', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (withPayment && (response.status === 422 || (response.status === 409 && result.detail !== 'Este intento ya corresponde a otros datos. Consulta los pedidos antes de volver a cobrar.'))) sessionStorage.removeItem(tokenKey);
      if (response.status === 409 && result.detail === 'Cambió la estimación. Revísala de nuevo antes de guardar.') schedulePreview();
      throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo guardar el presupuesto.');
    }
    if (withPayment) sessionStorage.removeItem(tokenKey);
    captureForm.reset(); rows.replaceChildren(); addRow(); previewVersion = null;
    document.querySelector('#capture-preview').textContent = '';
    document.querySelector('#capture-estimated-total').textContent = '';
    document.querySelector('#capture-payment-summary').textContent = 'Ingresa medidas para consultar el resumen de la cuenta y el anticipo mínimo.';
    document.querySelector('#capture-waste-status').textContent = '';
    history.pushState({}, '', `/pedidos/${result.id}`); loadOrders(); await openOrder(result.id);
    if (withPayment && currentOrderData?.aceptado && !currentOrderData.fecha_programada) {
      showArea('instalacion'); const field = document.querySelector('#installation-date'); field.scrollIntoView({block: 'center'}); field.focus();
    }
  } catch (error) { showError(error.message); } finally { controls.forEach((control, index) => { control.disabled = disabled[index]; }); }
});

function showStartView() {
  exitMeasureEdit();
  currentOrderId = null; currentOrderData = null;
  document.body.classList.remove('order-active');
  document.querySelector('#history-detail')?.remove();
  detail.hidden = true; message.hidden = true; errorReturn.hidden = true;
  const view = new URLSearchParams(location.search).get('vista');
  const sections = {presupuestos: 'budgets', pedidos: 'orders', historico: 'history'};
  const selected = Object.hasOwn(sections, view) ? sections[view] : undefined;
  if (!selected && view !== 'nuevo') { location.assign('/'); return; }
  capture.hidden = Boolean(selected);
  for (const id of Object.values(sections)) document.querySelector(`#${id}`).hidden = id !== selected;
}
window.addEventListener('popstate', () => {
  if ((captureHasChanges() && !window.confirm('Hay datos provisionales sin guardar. Si continúas se perderán. ¿Continuar?')) || !confirmPending('', true)) {
    history.pushState({}, '', currentOrderId ? `/pedidos/${currentOrderId}` : '/?vista=nuevo');
    return;
  }
  const match = location.pathname.match(/^\/pedidos\/(\d+)$/);
  if (match) openOrder(match[1]);
  else showStartView();
});

const match = location.pathname.match(/^\/pedidos\/(\d+)$/);
loadOrders();
if (match) openOrder(match[1]);
else showStartView();
