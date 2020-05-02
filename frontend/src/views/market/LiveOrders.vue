<template>
  <div>
    <Headline name="Live-Orders"/>
    <p class="font-weight-light font-italic">
      All current active orders in the market sorted by the most recent created order.
    </p>
    <OrdersTable></OrdersTable>

  </div>
</template>

<script>

import Headline from '@/components/Headline.vue';
import OrdersTable from '@/components/OrdersTable.vue';

/**
 * Renders all orders from the market sorted by the most recent orders.
 *
 * The highest and lowest order based on their value are marked for the current page.
 *
 */
export default {
  name: 'LiveOrders',
  components: { OrdersTable, Headline },
};
</script>
