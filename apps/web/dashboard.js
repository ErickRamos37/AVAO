const productionForm = document.querySelector('#production-report-form');
const productionDate = document.querySelector('#production-report-date');
const productionPeriod = document.querySelector('#production-report-period');
const productionResults = document.querySelector('#production-report-results');
const dateParts = new Intl.DateTimeFormat('en-US', {timeZone: 'America/Tijuana', year: 'numeric', month: '2-digit', day: '2-digit'}).formatToParts(new Date());
const localPart = type => dateParts.find(part => part.type === type).value;
productionDate.value = productionDate.max = `${localPart('year')}-${localPart('month')}-${localPart('day')}`;
function productionChart(days, key, label) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 800 230');
  svg.setAttribute('width', '100%');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', `Gráfica de ${label} por fecha. Los valores también están en la tabla.`);
  const element = (tag, attributes, text) => {
    const item = document.createElementNS(ns, tag);
    for (const [name, value] of Object.entries(attributes)) item.setAttribute(name, value);
    if (text !== undefined) item.textContent = text;
    svg.append(item); return item;
  };
  element('title', {}, `${label} por fecha`);
  element('desc', {}, 'Eje horizontal: fecha de registro. Eje vertical: cantidad registrada. La tabla muestra los valores exactos.');
  const left = 54, right = 780, top = 15, bottom = 185;
  const step = Math.max(1, Math.ceil(Math.max(0, ...days.map(day => day[key])) / 4));
  const ceiling = step * 4;
  for (let n = 0; n <= 4; n++) {
    const y = bottom - (bottom - top) * n / 4;
    element('line', {x1: left, x2: right, y1: y, y2: y, stroke: n === 0 ? '#333' : '#ddd'});
    element('text', {x: left - 8, y: y + 4, 'text-anchor': 'end', 'font-size': 12}, String(n * step));
  }
  element('line', {x1: left, x2: left, y1: top, y2: bottom, stroke: '#333'});
  const x = index => days.length === 1 ? (left + right) / 2 : left + (right - left) * index / (days.length - 1);
  const y = value => bottom - (bottom - top) * value / ceiling;
  const ticks = Math.min(days.length, 5);
  for (let n = 0; n < ticks; n++) {
    const index = ticks === 1 ? 0 : Math.round(n * (days.length - 1) / (ticks - 1));
    element('text', {x: x(index), y: bottom + 20, 'text-anchor': 'middle', 'font-size': 12}, days[index].fecha);
  }
  element('polyline', {points: days.map((day, index) => `${x(index)},${y(day[key])}`).join(' '), fill: 'none', stroke: '#176a42', 'stroke-width': 2});
  for (const [index, day] of days.entries()) {
    element('circle', {cx: x(index), cy: y(day[key]), r: days.length > 31 ? 1.5 : 3, fill: '#176a42'});
  }
  return svg;
}

productionForm.addEventListener('submit', async event => {
  event.preventDefault();
  productionResults.replaceChildren();
  try {
    const query = new URLSearchParams({fecha: productionDate.value, periodo: productionPeriod.value});
    const response = await fetch(`/api/produccion?${query}`);
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo consultar la producción.');
    const heading = document.createElement('p');
    heading.textContent = `Del ${result.inicio} al ${result.fin} · ${result.dias.length} día(s), incluidos días sin registros`;
    productionResults.append(heading);
    const areas = [['aluminio', 'Piezas de aluminio'], ['vidrio', 'Piezas de vidrio'], ['ensamble', 'Ventanas ensambladas']];
    for (const [key, label] of areas) {
      const graph = document.createElement('section');
      const title = document.createElement('h3');
      title.textContent = `${label}: total ${result.totales[key]} · promedio diario ${result.promedios_diarios[key].toFixed(2)}`;
      graph.append(title, productionChart(result.dias, key, label));
      if (result.totales[key] === 0) {
        const empty = document.createElement('p'); empty.textContent = 'Sin registros en este periodo.'; graph.append(empty);
      }
      productionResults.append(graph);
    }
    const table = document.createElement('table');
    const caption = document.createElement('caption'); caption.textContent = 'Conteos registrados por día'; table.append(caption);
    const head = document.createElement('thead'); const header = document.createElement('tr');
    for (const label of ['Fecha', 'Aluminio', 'Vidrio', 'Ventanas ensambladas']) { const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; header.append(th); }
    head.append(header); table.append(head);
    const body = document.createElement('tbody');
    for (const day of result.dias) {
      const row = document.createElement('tr');
      for (const value of [day.fecha, day.aluminio, day.vidrio, day.ensamble]) { const cell = document.createElement('td'); cell.textContent = value; row.append(cell); }
      body.append(row);
    }
    table.append(body); productionResults.append(table);
  } catch (error) {
    productionResults.textContent = error.message;
  }
});


const ordersDashboard = document.querySelector('#orders-dashboard');
async function loadDashboardOrders() {
  try {
    const response = await fetch('/api/tablero/pedidos');
    if (!response.ok) throw new Error('No se pudieron consultar los pedidos.');
    const groups = await response.json();
    ordersDashboard.replaceChildren();
    for (const [key, title] of [['pendientes', 'Pendientes de fabricación'], ['listos', 'Listos para instalar'],
      ['instalados_por_liquidar', 'Instalados por liquidar'], ['atrasados', 'Instalaciones atrasadas'], ['proximos', 'Instalaciones próximas: hoy y cinco días']]) {
      const section = document.createElement('section');
      const heading = document.createElement('h3'); heading.textContent = `${title}: ${groups[key].length}`; section.append(heading);
      if (!groups[key].length) { const line = document.createElement('p'); line.textContent = 'Ninguno.'; section.append(line); }
      const list = document.createElement('ul');
      for (const order of groups[key]) {
        const row = document.createElement('li'); const link = document.createElement('a');
        link.href = `/pedidos/${order.id}?origen=dashboard`; link.textContent = order.etiqueta ? `Pedido ${order.etiqueta}` : `Pedido ${order.id}`; row.append(link);
        const info = [];
        if (order.fecha_programada) info.push(`instalación ${order.fecha_programada}`);
        if (order.instalacion_atrasada) info.push('atrasada');
        if (key === 'pendientes') {
          if (order.sin_ventanas) info.push('sin ventanas activas');
          else {
            const missing = [['aluminio', 'aluminio'], ['vidrio', 'vidrio'], ['ensamble', 'ensamble']]
              .filter(([area]) => order[area].porcentaje !== 100).map(([, label]) => label);
            if (missing.length) info.push(`pendiente: ${missing.join(', ')}`);
            if (order.sin_plan) info.push('plan incompleto');
          }
        }
        if (info.length) row.append(document.createTextNode(` · ${info.join(' · ')}`));
        list.append(row);
      }
      section.append(list); ordersDashboard.append(section);
    }
  } catch (error) { ordersDashboard.textContent = error.message; }
}
loadDashboardOrders();

const departuresForm = document.querySelector('#departures-form');
const departuresDate = document.querySelector('#departures-date');
const departuresPeriod = document.querySelector('#departures-period');
const departuresResults = document.querySelector('#departures-results');
departuresDate.value = departuresDate.max = productionDate.max;
departuresForm.addEventListener('submit', async event => {
  event.preventDefault(); departuresResults.replaceChildren();
  try {
    const query = new URLSearchParams({fecha: departuresDate.value, periodo: departuresPeriod.value});
    const response = await fetch(`/api/tablero/salidas?${query}`);
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudieron consultar las salidas.');
    const heading = document.createElement('p'); heading.textContent = `Del ${result.inicio} al ${result.fin} · ${result.dias.length} día(s), incluidos días sin registros`; departuresResults.append(heading);
    for (const [key, label] of [['instalados', 'Pedidos instalados'], ['finalizados', 'Pedidos finalizados']]) {
      const section = document.createElement('section'); const title = document.createElement('h3');
      title.textContent = `${label}: total ${result.totales[key]} · promedio diario ${result.promedios_diarios[key].toFixed(2)}`;
      section.append(title, productionChart(result.dias, key, label));
      if (!result.totales[key]) { const empty = document.createElement('p'); empty.textContent = 'Sin registros en este periodo.'; section.append(empty); }
      departuresResults.append(section);
    }
    const table = document.createElement('table'); const caption = document.createElement('caption'); caption.textContent = 'Instalaciones vigentes y cierres por día'; table.append(caption);
    const head = document.createElement('thead'); const header = document.createElement('tr');
    for (const label of ['Fecha', 'Instalados', 'Finalizados']) { const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; header.append(th); }
    head.append(header); table.append(head); const body = document.createElement('tbody');
    for (const day of result.dias) { const row = document.createElement('tr');
      for (const value of [day.fecha, day.instalados, day.finalizados]) { const cell = document.createElement('td'); cell.textContent = value; row.append(cell); }
      body.append(row);
    }
    table.append(body); departuresResults.append(table);
  } catch (error) { departuresResults.textContent = error.message; }
});

function financeChart(days, key, label) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 800 230'); svg.setAttribute('width', '100%'); svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', `Gráfica de ${label} por fecha. Los valores exactos están en la tabla.`);
  const add = (tag, attrs, text) => { const item = document.createElementNS(ns, tag); for (const [name, value] of Object.entries(attrs)) item.setAttribute(name, value); if (text !== undefined) item.textContent = text; svg.append(item); };
  add('title', {}, `${label} por fecha`); add('desc', {}, 'Eje horizontal: fecha. Eje vertical: pesos, incluidos valores negativos. La tabla presenta importes exactos.');
  const left = 82, right = 780, top = 15, bottom = 185;
  const values = days.map(day => Number(day[key]));
  const min = Math.min(0, ...values), max = Math.max(0, ...values);
  const span = max === min ? 1 : max - min;
  const x = index => days.length === 1 ? (left + right) / 2 : left + (right - left) * index / (days.length - 1);
  const y = value => bottom - (bottom - top) * (value - min) / span;
  for (let n = 0; n <= 4; n++) {
    const value = min + span * n / 4, pos = y(value);
    add('line', {x1:left, x2:right, y1:pos, y2:pos, stroke:'#ddd'});
    add('text', {x:left-8, y:pos+4, 'text-anchor':'end', 'font-size':12}, value.toFixed(2));
  }
  add('line', {x1:left, x2:right, y1:y(0), y2:y(0), stroke:'#333'});
  add('line', {x1:left, x2:left, y1:top, y2:bottom, stroke:'#333'});
  const ticks = Math.min(days.length, 5);
  for (let n=0; n<ticks; n++) { const index = ticks === 1 ? 0 : Math.round(n * (days.length - 1) / (ticks - 1)); add('text', {x:x(index), y:bottom+20, 'text-anchor':'middle', 'font-size':12}, days[index].fecha); }
  add('polyline', {points:values.map((value,index) => `${x(index)},${y(value)}`).join(' '), fill:'none', stroke:'#176a42', 'stroke-width':2});
  values.forEach((value,index) => add('circle', {cx:x(index), cy:y(value), r:days.length>31?1.5:3, fill:'#176a42'}));
  return svg;
}

function availableAmount(amount, available, missing) {
  if (!available && missing) return 'No disponible';
  return `$${amount}${missing ? ' (parcial)' : ''}`;
}

const financeForm = document.querySelector('#finance-form');
const financeDate = document.querySelector('#finance-date');
const financePeriod = document.querySelector('#finance-period');
const financeResults = document.querySelector('#finance-results');
financeDate.value = financeDate.max = productionDate.max;
financeForm.addEventListener('submit', async event => {
  event.preventDefault(); financeResults.replaceChildren();
  try {
    const response = await fetch(`/api/tablero/finanzas?${new URLSearchParams({fecha:financeDate.value, periodo:financePeriod.value})}`);
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudieron consultar las finanzas.');
    const range = document.createElement('p'); range.textContent = `Del ${result.inicio} al ${result.fin} · ${result.dias.length} día(s), incluidos días sin movimientos`; financeResults.append(range);
    for (const [key, label] of [['pagos','Pagos recibidos'], ['devoluciones','Devoluciones'], ['neto','Ingresos netos']]) {
      const section = document.createElement('section'), heading = document.createElement('h3');
      heading.textContent = `${label}: total $${result.totales[key]} · promedio diario $${result.promedios_diarios[key]}`;
      section.append(heading, financeChart(result.dias, key, label)); financeResults.append(section);
    }
    const table = document.createElement('table'), caption = document.createElement('caption'); caption.textContent = 'Movimientos y ganancia guardada de cierres por día'; table.append(caption);
    const head = document.createElement('thead'), header = document.createElement('tr');
    for (const label of ['Fecha','Pagos','Devoluciones','Neto','Ganancia estimada de cierres','Ventanas sin ganancia']) { const th = document.createElement('th'); th.scope='col'; th.textContent=label; header.append(th); }
    head.append(header); table.append(head); const body = document.createElement('tbody');
    for (const day of result.dias) { const row = document.createElement('tr'); for (const value of [day.fecha, `$${day.pagos}`, `$${day.devoluciones}`, `$${day.neto}`, availableAmount(day.ganancia_finalizados, day.ganancias_disponibles, day.ganancias_faltantes), day.ganancias_faltantes]) { const td = document.createElement('td'); td.textContent=value; row.append(td); } body.append(row); }
    table.append(body); financeResults.append(table);
    const weekTitle = document.createElement('h3'); weekTitle.textContent = 'Ingreso neto promedio por día de la semana'; financeResults.append(weekTitle);
    const week = document.createElement('ul'), names = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'];
    for (const item of result.dias_semana) { const row = document.createElement('li'); row.textContent = `${names[item.dia]}: ${item.promedio_neto === null ? 'sin ocurrencias en el periodo' : `$${item.promedio_neto} · ${item.ocurrencias} día(s)${item.mayor ? ' · mayor promedio' : ''}`}`; week.append(row); } financeResults.append(week);
    const current = result.actual, currentTitle = document.createElement('h3'); currentTitle.textContent = 'Situación actual de pedidos aceptados activos'; financeResults.append(currentTitle);
    const currentLine = document.createElement('p'); currentLine.textContent = `Saldos pendientes: ${availableAmount(current.saldo, current.con_saldo, current.sin_saldo)} · Excedentes: ${availableAmount(current.excedente, current.con_saldo, current.sin_saldo)} · Pedidos sin saldo calculable: ${current.sin_saldo}`; financeResults.append(currentLine);
    const gain = document.createElement('p'); gain.textContent = `Ganancia estimada guardada: ${availableAmount(current.ganancia, current.con_ganancia, current.faltantes)} · Ventanas sin ganancia: ${current.faltantes} · Ventanas con ganancia desactualizada: ${current.desactualizadas}`; financeResults.append(gain);
    const closed = document.createElement('p'); closed.textContent = `Ganancia estimada guardada de pedidos finalizados en el periodo: ${availableAmount(result.finalizados.ganancia, result.finalizados.con_ganancia, result.finalizados.faltantes)} · Ventanas sin ganancia: ${result.finalizados.faltantes}`; financeResults.append(closed);
  } catch (error) { financeResults.textContent = error.message; }
});
