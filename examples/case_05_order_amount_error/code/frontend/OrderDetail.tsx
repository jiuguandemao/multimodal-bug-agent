export function calcTotal(order) {
  const items = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  return Number((items + order.freight).toFixed(2));
}
