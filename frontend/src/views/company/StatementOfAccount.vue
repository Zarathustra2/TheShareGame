<template>
  <div>
    <CompanyBreadCrumb active="Statement Of Account" :companyName="name" v-bind:key="name"/>
    <p class="font-weight-light font-italic">
      In the Statement of Account you can read look up all transactions of a company.
      Everything it has bought/sold has been logged here.
    </p>
    <list :getData="getStatements" :childFields="fields" id="statements" :slots="templates">

      <template slot="typ" slot-scope="data">
        <span v-if="data.tbl.value === 'Order'" class="text-primary">
          {{ data.tbl.value }}
          <b-button size="sm" @click="info(data.tbl.item)" class="mr-1 order-info-btn">
          Info
        </b-button>
        </span>

        <span v-else class="text-info">
          {{ data.tbl.value }}
        </span>

      </template>

      <template slot="value" slot-scope="data">
         <span v-if="data.tbl.item.received" class="text-success">
           {{ data.tbl.value }}
         </span>
        <span v-else class="text-danger">
             -{{ data.tbl.value }}
           </span>
      </template>

    </list>

  </div>
</template>

<script>

import List from '@/components/List.vue';
import Api from '@/service/api';
import { Table, Number } from '@/service/utils';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';
import { BButton, ModalPlugin } from 'bootstrap-vue';

import Vue from 'vue';

Vue.use(ModalPlugin);

/**
 * Renders the statement of account for this company.
 *
 * The statement allows one to track where this company invested its cash.
 *
 */
export default {
  name: 'StatementOfAccount',
  components: { CompanyBreadCrumb, List, BButton },
  props: ['companyName'],
  data() {
    return {
      isBusy: false,
      page: 1,
      size: 10,
      total: 0,
      templates: [
        { name: 'typ', field: 'typ' },
        { name: 'value', field: 'value' },
      ],
      fields: [
        {
          key: 'value', label: 'Value', sortable: true, sortDirection: 'desc', class: 'value',
        },
        {
          key: 'typ', label: 'Typ', sortable: true, sortDirection: 'desc', class: 'typ',
        },
        {
          key: 'amount', label: 'Amount', sortable: true, sortDirection: 'desc', class: 'amount',
        },
        {
          key: 'created',
          label: 'Date',
          sortable: true,
          sortDirection: 'desc',
          class: 'created',
        },
      ],
      items: [],
      name: this.companyName,
    };
  },
  methods: {
    getStatements(c) {
      const formatter = (item) => {
        item.value = Number.numberWithDollar(item.value);
        item.amount = Number.formatNumber(item.amount);
      };
      const wrapper = (page, size) => Api.statementOfAccount(this.$route.params.isin, page, size);
      Table.getTableData({
        url: wrapper, component: c, page: c.page, size: c.size, formatter,
      });
    },
    info(item) {
      const h = this.$createElement;

      const messageVNode = h('ul', { class: [''] }, [
        h('li', [
          h('span', { class: ['text-warning'] }, 'Seller: '),
          h('router-link', {
            attrs: {
              to: {
                name: 'company',
                params: { isin: item.trade.seller.isin },
              },
            },
          }, `${item.trade.seller.name}`),

        ]),
        h('li', [
          h('span', { class: ['text-success'] }, 'Buyer: '),
          h('router-link', {
            attrs: {
              to: {
                name: 'company',
                params: { isin: item.trade.buyer.isin },
              },
            },
          }, `${item.trade.buyer.name}`),
        ]),
        h('li', [
          h('span', { class: [''] }, 'Company: '),
          h('router-link', {
            attrs: {
              to: {
                name: 'company',
                params: { isin: item.trade.company.isin },
              },
            },
          }, `${item.trade.company.name}`),
        ]),
        h('hr'),
        h('li', `Price: ${Number.numberWithDollar(item.trade.price)}`),
        h('li', `Amount: ${Number.formatNumber(item.trade.amount)}`),
        h('li', `Value: ${Number.numberWithDollar(item.value)}`),
      ]);

      const title = h('div', { class: ['text-center'] }, 'Trade details');

      this.$bvModal.msgBoxOk([messageVNode], {
        title: [title],
        buttonSize: 'sm',
        centered: true,
        size: 'sm',
        id: 'order-info',
      });
    },
  },
  beforeMount() {
    console.log(this.companyName);
    if (this.name === undefined) {
      this.name = '';
      this.$http.get(Api.company(this.$route.params.isin)).then((r) => {
        this.name = r.data.name;
      });
    }
  },

};
</script>
