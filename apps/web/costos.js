const costList = document.querySelector('#cost-list');
const costMessage = document.querySelector('#cost-message');

function showMessage(text, isError = false) {
  costMessage.textContent = text;
  costMessage.dataset.error = String(isError);
  costMessage.hidden = false;
}

function formatMoney(value) {
  return value === null ? 'Pendiente' : `$${value}`;
}

function renderCosts(items) {
  const table = document.createElement('table');
  const head = document.createElement('thead');
  const headerRow = document.createElement('tr');
  for (const label of ['Insumo', 'Presentación de compra', 'Costo registrado', 'Costo equivalente', 'Acción']) {
    const cell = document.createElement('th');
    cell.scope = 'col';
    cell.textContent = label;
    headerRow.append(cell);
  }
  head.append(headerRow);
  const body = document.createElement('tbody');
  for (const item of items) {
    const row = document.createElement('tr');
    const name = document.createElement('th');
    name.scope = 'row';
    name.textContent = item.nombre;
    const purchase = document.createElement('td');
    purchase.textContent = item.presentacion_compra;
    const costCell = document.createElement('td');
    const input = document.createElement('input');
    input.type = 'number';
    input.min = '0';
    input.step = '0.01';
    input.inputMode = 'decimal';
    input.required = true;
    input.setAttribute('aria-label', `Costo de compra de ${item.nombre}`);
    input.value = item.costo_compra ?? '';
    costCell.append(input);
    const unit = document.createElement('span');
    unit.textContent = ` ${item.unidad_costo}`;
    costCell.append(unit);
    const equivalent = document.createElement('td');
    equivalent.textContent = item.costo_derivado === null
      ? (item.costo_compra === null ? 'Pendiente' : 'Tarifa directa')
      : `$${item.costo_derivado} ${item.unidad_derivada}`;
    const action = document.createElement('td');
    const save = document.createElement('button');
    save.type = 'button';
    save.textContent = 'Guardar';
    action.append(save);
    row.append(name, purchase, costCell, equivalent, action);
    save.addEventListener('click', async () => {
      if (!input.reportValidity()) return;
      save.disabled = true;
      costMessage.hidden = true;
      try {
        const response = await fetch(`/api/costos-insumos/${encodeURIComponent(item.codigo)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ costo: input.value }),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(result.detail ?? 'No se pudo guardar el costo.');
        showMessage(`Costo de ${result.nombre} guardado: ${formatMoney(result.costo_compra)} ${result.unidad_costo}.`);
        await loadCosts();
      } catch (error) {
        showMessage(error.message, true);
      } finally {
        save.disabled = false;
      }
    });
    body.append(row);
  }
  table.append(head, body);
  costList.replaceChildren(table);
}

async function loadCosts() {
  try {
    const response = await fetch('/api/costos-insumos');
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail ?? 'No se pudieron consultar los costos.');
    renderCosts(result.insumos);
  } catch (error) {
    costList.textContent = error.message;
  }
}

loadCosts();
