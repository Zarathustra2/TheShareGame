<template>
  <div>
      <list :getData="getOrders" :slots="templates" :childFields="fields" id="orders">
      <template slot="typ" slot-scope="data">
        <span v-if="data.tbl.value === 'Sell'" class="text-danger">
          {{ data.tbl.value }}
        </span>
        <span v-else class="text-success">
          {{ data.tbl.value }}
        </span>

      </template>

    </list>
  </div>
</template>

<script>

import Api from '@/service/api';
import { Table, Number } from '@/service/utils';
import List from '@/components/List.vue';

/**
 * OrderbookTable holds the data about all orders for a single company
 * but it does not show who placed the orders obviosuly.
 */
export default {
  name: 'OrderbookTable',
  components: { List },
  data() {
    return {
      templates: [
        { name: 'typ', field: 'typ' },
      ],
      name: null,
      fields: [
        {
          key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
        },
        {
          key: 'price', label: 'Price', sortable: true, sortDirection: 'desc', class: 'price',
        },
        {
          key: 'amount', label: 'Amount', sortable: true, sortDirection: 'desc', class: 'amount',
        },
        {
          key: 'typ', label: 'Typ', sortable: true, sortDirection: 'desc', class: 'typ',
        },

      ],

    };
  },
  methods: {
    getOrders(c) {
      const formatter = (item) => {
        item.value = Number.numberWithDollar(item.value);
        item.price = Number.numberWithDollar(item.price);
        item.amount = Number.formatNumber(item.amount);
      };

      const { isin } = this.$route.params;
      const url = (page, size) => Api.ordersCompany(isin, page, size);
      Table.getTableData({
        url, component: c, page: c.page, size: c.size, formatter,
      });
    },
  },
};
</script>

<style scoped>

</style>
