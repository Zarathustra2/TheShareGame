<template>
  <list :getData="getOrders" :slots="templates" :childFields="fields" id="orders-table" ref="table">

    <template slot="order_of" slot-scope="data">
      <router-link :to="{name: 'company', params: {isin: data.tbl.value.isin}}">
        {{ data.tbl.value.name }}
      </router-link>
    </template>

    <template slot="typ" slot-scope="data">
        <span v-if="data.tbl.value === 'Sell'" class="text-danger">
          {{ data.tbl.value }}
        </span>
      <span v-else class="text-success">
          {{ data.tbl.value }}
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

    <template slot="edit" slot-scope="data">
      <a href="" v-on:click="deleteOrder($event, data.tbl.item.id)">
        <span class="text-danger fas fa-trash"/>
        </a>
    </template>

  </list>
</template>

<script>
import List from '@/components/List.vue';
import { Number, Table } from '@/service/utils';
import Api from '@/service/api';
import Service from '@/service/service';

/**
   * This component renders a table with orders.
   *
   * It is being used by LiveOrders and UserOrders. Depending on whether it got rendered
   * from LiveOrders or UserOrders it will call a different url.
   *
   * Also if it go rendered by UserOrders, it will also render an edit field in the table
   * which allows user to edit/delete their order quickly.
   *
   */
export default {
  name: 'OrdersTable',
  components: { List },
  props: ['isUserOrders'],
  data() {
    const fields = [
      {
        key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
      },
      {
        key: 'order_of',
        label: 'Company',
        sortable: true,
        sortDirection: 'desc',
        class: 'company',
      },
      {
        key: 'typ',
        label: 'Typ',
        sortable: true,
        sortDirection: 'desc',
        class: 'typ',
      },
      {
        key: 'price', label: 'Price', sortable: true, sortDirection: 'desc', class: 'price',
      },
      {
        key: 'amount', label: 'Amount', sortable: true, sortDirection: 'desc', class: 'amount',
      },
      {
        key: 'created',
        label: 'Created',
        sortable: true,
        sortDirection: 'desc',
        class: 'created',
      },
    ];

    if (this.isUserOrders) {
      fields.push({
        key: 'edit',
        label: 'Delete',
        sortable: false,
        class: 'edit',
      });
    }

    return {
      templates: [
        { name: 'order_of', field: 'order_of' },
        { name: 'typ', field: 'typ' },
        { name: 'value', field: 'value' },
        { name: 'edit', field: 'edit' },
      ],
      fields,
      highestTrade: Number.numberWithDollar(-1),
      lowestTrade: Number.numberWithDollar(1000000000000),

    };
  },
  methods: {
    getOrders(c, ctx) {
      this.highestTrade = Number.numberWithDollar(-1);
      this.lowestTrade = Number.numberWithDollar(1000000000000);

      const formatter = (item) => {
        const value = item.price * item.amount;
        item.value = Number.numberWithDollar(value);
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
        url: this.getUrl(), component: c, page: c.page, size: c.size, formatter, ctx,
      });
    },
    getUrl() {
      if (this.isUserOrders) {
        return Api.ordersByUser;
      }
      return Api.orders;
    },
    deleteOrder(e, id) {
      e.preventDefault();

      const c = Service.getCompany();
      const url = Api.ordersCompany(c.isin, 0, 0);
      const data = {
        order_id: id,
      };

      // Axios.delete has the signatur delete(path, config)
      // while all the other methods such as put, post have the signature
      // post(path, data, config)
      //
      // To pass data while making a delete request we can use config.data.
      this.$http.delete(url, { data }).then(() => {
        this.$refs.table.getExternalData();
      }).catch((err) => {
        console.error(err);
      });
    },

  },
};
</script>

<style scoped>

</style>
