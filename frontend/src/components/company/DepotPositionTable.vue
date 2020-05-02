<template>
  <div>
    <h2>Depot Positions</h2>
    <list :getData="getPositions" :slots="templates" :childFields="fields" id="depot">

      <template slot="company" slot-scope="data">
        <span v-if="data.tbl.value.isin === undefined">
          {{ data.tbl.item.history.company_name }}
        </span>
        <span v-else>
        <router-link :to="{name: 'company', params: {isin: data.tbl.value.isin}}">
          {{ data.tbl.value.name }}
        </router-link>
          </span>
      </template>

    </list>

  </div>
</template>

<script>

import Api from '@/service/api';
import { Table, Number } from '@/service/utils';
import List from '@/components/List.vue';

export default {
  name: 'DepotPositionTable',
  components: { List },
  data() {
    return {
      templates: [
        { name: 'company', field: 'company' },
      ],
      fields: [
        {
          key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
        },
        {
          key: 'company',
          label: 'Company',
          sortable: true,
          sortDirection: 'desc',
          class: 'company',
        },
        {
          key: 'price_bought',
          label: 'Payed',
          sortable: true,
          sortDirection: 'desc',
          class: 'payed',
        },
        {
          key: 'share_price',
          label: 'Share Price',
          sortable: true,
          sortDirection: 'desc',
          class: 'share_price',
        },
        {
          key: 'amount', label: 'Amount', sortable: true, sortDirection: 'desc', class: 'amount',
        },

      ],
      items: [],
    };
  },
  methods: {
    getPositions(c) {
      const formatter = (item) => {
        // Needs to best the first one in the order. Otherwise we would pass in strings
        item.value = Number.numberWithDollar(item.share_price * item.amount);

        item.price_bought = Number.numberWithDollar(item.price_bought);
        item.share_price = Number.numberWithDollar(item.share_price);
        item.amount = Number.formatNumber(item.amount);
      };

      const url = (page, size) => Api.depot(this.$route.params.isin, page, size);
      Table.getTableData({
        url, component: c, page: c.page, size: c.size, formatter,
      });
    },
  },
};
</script>
