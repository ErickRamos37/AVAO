const capture = document.querySelector('#capture');
const detail = document.querySelector('#detail');
const message = document.querySelector('#message');
const errorReturn = document.querySelector('#error-return');

function showError(text) {
  message.textContent = text;
  message.hidden = false;
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
    document.querySelector('#order-title').textContent = `Pedido ${order.id}`;
    const content = document.querySelector('#order-content');
    content.replaceChildren();
    for (const window of order.ventanas) {
      const item = document.createElement('p');
      item.textContent = `Ventana ${window.numero}: ${window.ancho} × ${window.alto}`;
      content.append(item);
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
  const button = event.currentTarget.querySelector('button');
  button.disabled = true;
  try {
    const response = await fetch('/api/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ancho: document.querySelector('#width').value,
        alto: document.querySelector('#height').value,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'No se pudo guardar el pedido.');
    }
    const order = await response.json();
    history.pushState({}, '', `/pedidos/${order.id}`);
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
if (match) openOrder(match[1]);
