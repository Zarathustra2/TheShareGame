<template>
  <list :getData="getTrades" :slots="templates" :childFields="fields" id="trades">

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

      <template slot="seller" slot-scope="data">
        <span v-if="data.tbl.value.isin === undefined">
          {{ data.tbl.item.history.seller_name }}
        </span>
        <span v-else>
        <router-link :to="{name: 'company', params: {isin: data.tbl.value.isin}}">
          {{ data.tbl.value.name }}
        </router-link>
          </span>
      </template>

      <template slot="buyer" slot-scope="data">
        <span v-if="data.tbl.value.isin === undefined">
          {{ data.tbl.item.history.buyer_name }}
        </span>
        <span v-else>
        <router-link :to="{name: 'company', params: {isin: data.tbl.value.isin}}">
          {{ data.tbl.value.name }}
        </router-link>
          </span>
      </template>

      <template slot="value" slot-scope="data">
        <span v-if="data.tbl.value === highestTrade" class="text-success">
          {{ data.tbl.value }}
        </span>
        <span v-else-if="data.tbl.value === lowestTrade" class="text-danger">
          {{ data.tbl.value }}
        </span>
        <span v-else>
          {{ data.tbl.value }}
        </span>
      </template>

    </list>
</template>

<script>

import { Table, Number } from '@/service/utils';
import List from '@/components/List.vue';

export default {
  name: 'TradesTable',
  components: { List },
  props: ['url', 'disabledFields'],
  data() {
    return {
      templates: [
        { name: 'buyer', field: 'buyer' },
        { name: 'seller', field: 'seller' },
        { name: 'company', field: 'company' },
        { name: 'value', field: 'value' },
      ],
      name: null,
      fields: [
        {
          key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
        },
        {
          key: 'buyer', label: 'Buyer', sortable: true, sortDirection: 'desc', class: 'buyer',
        },
        {
          key: 'seller', label: 'Seller', sortable: true, sortDirection: 'desc', class: 'seller',
        },
        {
          key: 'company',
          label: 'Company',
          sortable: true,
          sortDirection: 'desc',
          class: 'company',
        },
        {
          key: 'price', label: 'Price', sortable: true, sortDirection: 'desc', class: 'price',
        },
        {
          key: 'amount', label: 'Amount', sortable: true, sortDirection: 'desc', class: 'amount',
        },

      ],
      highestTrade: Number.numberWithDollar(-1),
      lowestTrade: Number.numberWithDollar(1000000000000),
    };
  },
  beforeMount() {
    // Some views do not want to display all the fields.
    // For instance, the Buyer/Seller View does not need the company field
    if (this.disabledFields !== undefined) {
      for (let i = 0; i < this.disabledFields.length; i++) {
        this.fields = this.fields.filter(((e) => e.key !== this.disabledFields[i]));
      }
    }
  },
  methods: {
    getTrades(c, ctx) {
      if (this.url === undefined) {
        console.error('Url is undefined!');
        return;
      }

      const formatter = (item) => {
        item.value = Number.numberWithDollar(item.value);
        item.price = Number.numberWithDollar(item.price);
        item.amount = Number.formatNumber(item.amount);

        const undo = Number.formatedNumberToNumber;

        if (undo(item.value) > (undo(this.highestTrade))) {
          this.highestTrade = item.value;
        }

        if (undo(item.value) < (undo(this.lowestTrade))) {
          this.lowestTrade = item.value;
        }
      };


      Table.getTableData({
        url: this.url, component: c, page: c.page, size: c.size, formatter, ctx,
      });
    },
  },
};
</script>

<style scoped>

</style>
