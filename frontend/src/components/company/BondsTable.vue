<template>
  <div>
    <h2>Bonds</h2>
    <list :getData="getBonds" :childFields="fields" id="bondstable"/>

  </div>
</template>

<script>

import Api from '@/service/api';
import { Table, Number } from '@/service/utils';
import List from '@/components/List.vue';

export default {
  name: 'BondsTable',
  components: { List },
  data() {
    return {
      fields: [
        {
          key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
        },
        {
          key: 'rate', label: 'Rate', sortable: true, sortDirection: 'desc', class: 'rate',
        },
        {
          key: 'runtime',
          label: 'Runtime',
          sortable: true,
          sortDirection: 'desc',
          class: 'runtime',
        },
        {
          key: 'expires',
          label: 'Expires',
          sortable: true,
          sortDirection: 'desc',
          class: 'expires',
        },


      ],
    };
  },
  methods: {
    getBonds(c) {
      const formatter = (item) => {
        // Needs to best the first one in the order. Otherwise we would pass in strings
        item.value = Number.numberWithDollar(item.value);
        item.rate += '%';
      };

      const url = (page, size) => Api.bondsCompany(this.$route.params.isin, page, size);
      Table.getTableData({
        url, component: c, page: c.page, size: c.size, formatter,
      });
    },
  },
};
</script>
