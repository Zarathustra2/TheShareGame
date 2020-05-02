<template>

  <div v-if="name===undefined || shareholders === []">Loading...</div>

  <div v-else>
    <CompanyBreadCrumb :active="headline" :companyName="name" />
    <p class="font-weight-light font-italic">
      In the Shareholders view one can view the current shareholders of the company.
      If a company holds more than 75% it can take over the company. Generally speaking:
      If a company has a lot of shareholders it makes trading a lot easier.
    </p>

    <b-row>

      <b-col sm>
        <ShareholdersTable :shareholders="shareholders" :key="shareholders.length">
        </ShareholdersTable>
      </b-col>

      <b-col sm>
        <ShareholdersPieChart :shareholders="shareholders" :key="shareholders.length">
        </ShareholdersPieChart>
      </b-col>
    </b-row>

  </div>
</template>

<script>
import Api from '@/service/api';
import ShareholdersTable from '@/components/company/ShareholdersTable.vue';
import ShareholdersPieChart from '@/components/company/charts/ShareholdersPieChart.vue';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';

import { BRow, BCol } from 'bootstrap-vue';

/**
 * Renders all shareholders of this company.
 */
export default {
  name: 'Shareholders',
  components: {
    CompanyBreadCrumb, ShareholdersPieChart, ShareholdersTable, BRow, BCol,
  },
  props: ['companyName', 'sharePriceCompany'],
  data() {
    return {
      name: this.companyName,
      sharePrice: this.sharePriceCompany,
      isin: this.$route.params.isin,
      shareholders: [],
    };
  },

  beforeMount() {
    // If the view got access directly instead of a company's page,
    // the company name will not be present. We need to get it.
    if (this.name === undefined || this.sharePrice === undefined) {
      this.$http.get(Api.company(this.isin)).then((r) => {
        this.name = r.data.name;
        this.sharePrice = r.data.key_figures.share_price;
        this.getShareholders();
      });
    } else {
      this.getShareholders();
    }
  },
  computed: {
    headline() {
      return `Shareholders - ${this.name}`;
    },
  },
  methods: {
    getShareholders() {
      this.$http.get(Api.shareholders(this.isin)).then((r) => {
        const shareholders = r.data;
        shareholders.forEach((s) => {
          s.value = s.amount * this.sharePrice;
        });
        this.shareholders = shareholders;
      });
    },
  },
};
</script>

<style scoped>

</style>
