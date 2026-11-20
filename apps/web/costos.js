const costList = document.querySelector('#cost-list');
const costMessage = document.querySelector('#cost-message');
const form = document.querySelector('#inventory-form');
const profit = document.querySelector('#profit');
const threshold = document.querySelector('#waste-threshold');
const dialog = document.querySelector('#unsaved-dialog');
let initial = new Map();
let destination = null;
let saving = false;

function showMessage(text, isError = false) {
  costMessage.textContent = text;
  costMessage.dataset.error = String(isError);
  costMessage.hidden = false;
}
function dirty() {
  return [...form.querySelectorAll('input')].some(input => input.value !== initial.get(input.name));
}
function renderCosts(data) {
  const table = document.createElement('table');
  const head = document.createElement('thead');
  const header = document.createElement('tr');
  for (const label of ['Insumo', 'Presentación de compra', 'Costo registrado', 'Costo equivalente']) {
    const cell = document.createElement('th'); cell.scope = 'col'; cell.textContent = label; header.append(cell);
  }
  head.append(header);
  const body = document.createElement('tbody');
  for (const item of data.insumos) {
    const row = document.createElement('tr');
    const name = document.createElement('th'); name.scope = 'row'; name.textContent = item.nombre;
    const purchase = document.createElement('td'); purchase.textContent = item.presentacion_compra;
    const costCell = document.createElement('td');
    const input = document.createElement('input');
    input.type = 'number'; input.min = '0'; input.step = '0.01'; input.inputMode = 'decimal';
    input.name = item.codigo; input.value = item.costo_compra ?? '';
    input.setAttribute('aria-label', `Costo de compra de ${item.nombre}`);
    const unit = document.createElement('span'); unit.textContent = ` ${item.unidad_costo}`;
    costCell.append(input, unit);
    const equivalent = document.createElement('td');
    equivalent.textContent = item.costo_derivado === null ? (item.costo_compra === null ? 'Pendiente' : 'Tarifa directa') : `$${item.costo_derivado} ${item.unidad_derivada}`;
    row.append(name, purchase, costCell, equivalent); body.append(row);
  }
  table.append(head, body); costList.replaceChildren(table);
  profit.name = 'porcentaje_ganancia'; profit.value = data.porcentaje_ganancia;
  threshold.name = 'umbral_merma'; threshold.value = data.umbral_merma;
  initial = new Map([...form.querySelectorAll('input')].map(input => [input.name, input.value]));
}
async function loadCosts() {
  try {
    const response = await fetch('/api/costos-insumos');
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail ?? 'No se pudieron consultar los costos.');
    renderCosts(result);
  } catch (error) { costList.textContent = error.message; form.querySelector('button').disabled = true; }
}
async function saveChanges() {
  if (saving || !form.reportValidity()) return false;
  const costos = {};
  for (const input of costList.querySelectorAll('input')) {
    if (input.value !== initial.get(input.name)) {
      if (!input.value) { input.setCustomValidity('Ingresa un costo para guardar este cambio.'); input.reportValidity(); input.setCustomValidity(''); return false; }
      costos[input.name] = input.value;
    }
  }
  const payload = {costos};
  if (profit.value !== initial.get(profit.name)) payload.porcentaje_ganancia = Number(profit.value);
  if (threshold.value !== initial.get(threshold.name)) payload.umbral_merma = Number(threshold.value);
  saving = true; form.querySelectorAll('input, button').forEach(element => { element.disabled = true; });
  try {
    const response = await fetch('/api/costos-insumos', {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudieron guardar los cambios.');
    renderCosts(result); showMessage('Cambios guardados.'); return true;
  } catch (error) { showMessage(error.message, true); return false; }
  finally { saving = false; form.querySelectorAll('input, button').forEach(element => { element.disabled = false; }); }
}
form.addEventListener('submit', async event => { event.preventDefault(); await saveChanges(); });
window.addEventListener('beforeunload', event => { if (dirty()) { event.preventDefault(); event.returnValue = ''; } });
document.addEventListener('click', event => {
  const link = event.target.closest('a[href]');
  if (link && saving) { event.preventDefault(); return; }
  if (!link || !dirty() || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || link.target) return;
  const url = new URL(link.href, location.href);
  if (url.origin !== location.origin) return;
  event.preventDefault(); destination = url.href; dialog.showModal();
});
dialog.addEventListener('click', async event => {
  const action = event.target.dataset.action;
  if (!action) return;
  if (action === 'stay') { dialog.close(); return; }
  if (action === 'save') { dialog.close(); if (!await saveChanges()) return; }
  if (action === 'discard') initial = new Map([...form.querySelectorAll('input')].map(input => [input.name, input.value]));
  location.href = destination;
});
loadCosts();
