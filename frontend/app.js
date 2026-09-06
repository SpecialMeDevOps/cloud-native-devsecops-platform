const API_BASES = {
  users: 'http://localhost:8001',
  products: 'http://localhost:8002',
  orders: 'http://localhost:8003'
};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadHealth() {
  const healthEls = {
    userHealth: document.getElementById('userHealth'),
    productHealth: document.getElementById('productHealth'),
    orderHealth: document.getElementById('orderHealth')
  };

  for (const [key, value] of Object.entries(API_BASES)) {
    try {
      const result = await fetchJson(`${value}/health`);
      healthEls[`${key.replace('s', '')}Health`] = healthEls[`${key.replace('s', '')}Health`];
      const elementId = key === 'users' ? 'userHealth' : key === 'products' ? 'productHealth' : 'orderHealth';
      const element = document.getElementById(elementId);
      element.textContent = result.status === 'ok' ? 'Healthy' : 'Warning';
      element.className = result.status === 'ok' ? 'status-ok' : 'status-error';
    } catch (error) {
      const element = document.getElementById(key === 'users' ? 'userHealth' : key === 'products' ? 'productHealth' : 'orderHealth');
      element.textContent = 'Offline';
      element.className = 'status-error';
    }
  }
}

async function loadUsers() {
  const list = document.getElementById('userList');
  list.innerHTML = '';
  try {
    const users = await fetchJson(`${API_BASES.users}/users`);
    users.forEach((user) => {
      const li = document.createElement('li');
      li.textContent = `${user.username} (${user.role})`;
      list.appendChild(li);
    });
  } catch (error) {
    const li = document.createElement('li');
    li.textContent = 'Unable to load users';
    list.appendChild(li);
  }
}

async function loadProducts() {
  const list = document.getElementById('productList');
  list.innerHTML = '';
  try {
    const products = await fetchJson(`${API_BASES.products}/products`);
    products.forEach((product) => {
      const li = document.createElement('li');
      li.textContent = `${product.name} - $${product.price} (stock: ${product.stock})`;
      list.appendChild(li);
    });
  } catch (error) {
    const li = document.createElement('li');
    li.textContent = 'Unable to load products';
    list.appendChild(li);
  }
}

async function loadOrders() {
  const list = document.getElementById('orderList');
  list.innerHTML = '';
  try {
    const orders = await fetchJson(`${API_BASES.orders}/orders`);
    if (orders.length === 0) {
      list.innerHTML = '<li>No orders created yet.</li>';
      return;
    }
    orders.forEach((order) => {
      const li = document.createElement('li');
      li.textContent = `Order #${order.id}: user ${order.user_id} • ${order.status} • $${order.total_amount}`;
      list.appendChild(li);
    });
  } catch (error) {
    const li = document.createElement('li');
    li.textContent = 'Unable to load orders';
    list.appendChild(li);
  }
}

async function refreshData() {
  await Promise.all([loadHealth(), loadUsers(), loadProducts(), loadOrders()]);
}

document.getElementById('refreshBtn').addEventListener('click', refreshData);
refreshData();
