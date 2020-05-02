<template>
  <div>
    <Headline name="Your Orders"></Headline>
    <OrdersTable isUserOrders="true"></OrdersTable>

  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import OrdersTable from '@/components/OrdersTable.vue';

/**
   * Displays all orders created by the user.
   * Users can edit/delete their orders from the table.
   *
   */
export default {
  name: 'UserOrders',
  components: { Headline, OrdersTable },
};
</script>

<style scoped>

</style>
