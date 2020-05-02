<template>
  <div>
    <b-table-simple borderless>
      <b-tbody>
        <b-tr>
          <b-th>Local time</b-th>
          <b-th class="text-right">{{hours}}:{{minutes}}:{{seconds}}</b-th>
        </b-tr>
      </b-tbody>
    </b-table-simple>
    <b-table-simple borderless>
      <b-thead>
        <b-tr>
          <b-th colspan="2" class="text-center">
            <h4>Newcomers</h4>
          </b-th>
        </b-tr>
        <b-tr>
          <b-th>Name</b-th>
          <b-th class="text-right">Price</b-th>
        </b-tr>
      </b-thead>
      <b-tbody>
        <b-tr v-for="c in companies" v-bind:key="c.id">
            <b-th>
              <router-link :to="{name: 'company', params: {isin: c.isin}}">
                {{c.name}}
              </router-link>
            </b-th>
            <b-th class="text-right">{{c.share_price}}</b-th>
        </b-tr>
      </b-tbody>
    </b-table-simple>
    <b-table-simple borderless>
      <b-thead>
        <b-tr>
          <b-th colspan="2" class="text-center">
            <h4>Stats</h4>
          </b-th>
        </b-tr>
      </b-thead>
      <b-tbody>
        <b-tr>
            <b-th>Companies</b-th>
            <b-th class="text-right">{{companies_count}}</b-th>
        </b-tr>
        <b-tr>
            <b-th>Bond Rate</b-th>
            <b-th class="text-right">{{bond_rate}}%</b-th>
        </b-tr>
        <b-tr>
            <b-th class="text-success">Buy Orders</b-th>
            <b-th class="text-right">{{buy_orders_count}}</b-th>
        </b-tr>
        <b-tr>
            <b-th class="text-danger">Sell Orders</b-th>
            <b-th class="text-right">{{sell_orders_count}}</b-th>
        </b-tr>
      </b-tbody>
    </b-table-simple>
  </div>
</template>

<script>
import Api from '@/service/api';
import { Number } from '@/service/utils';

import {
  BTableSimple, BTh, BTr, BThead, BTbody,
} from 'bootstrap-vue';

export default {
  name: 'Sidebar',
  components: {
    BTableSimple, BTh, BTr, BThead, BTbody,
  },
  data() {
    return {
      date: new Date(),
      hours: 0,
      minutes: 0,
      seconds: 0,
      companies: [],
      companies_count: 0,
      bond_rate: 0,
      buy_orders_count: 0,
      sell_orders_count: 0,
    };
  },
  created() {
    const self = this;
    self.updateDate();
    setInterval(() => {
      self.updateDate();
    }, 1000);
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$http.get(Api.sidebar()).then((r) => {
        const { data } = r;
        this.companies = data.companies;

        this.companies.forEach((c) => {
          c.share_price = Number.numberWithDollar(c.share_price);
        });

        this.companies_count = Number.formatNumber(data.companies_count);
        this.bond_rate = data.bond_rate;

        this.buy_orders_count = Number.formatNumber(data.buy_orders_count);
        this.sell_orders_count = Number.formatNumber(data.sell_orders_count);
      });
    },
    updateDate() {
      const date = new Date();
      this.hours = date.getHours();
      this.minutes = date.getMinutes();
      this.seconds = date.getSeconds();

      if (this.seconds < 10) {
        this.seconds = `0${this.seconds}`;
      }

      if (this.minutes < 10) {
        this.minutes = `0${this.minutes}`;
      }

      if (this.hours < 10) {
        this.hours = `0${this.hours}`;
      }
    },
  },
};
</script>

<style scoped>

</style>
