<template>
  <div>
    <CompanyBreadCrumb :active="headlineName" :companyName="name" v-bind:key="headlineName"/>
    <p class="font-weight-light font-italic">
      In the Trades view one can view which shares this company has recently sold.
    </p>
    <TradesTable :url="url"/>

  </div>
</template>

<script>
import TradesTable from '@/components/TradesTable.vue';
import Api from '@/service/api';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';

/**
 * Renders the trades of the company, meaning all the shares this company has sold.
 *
 * Furthermore, one can analyze whether this company made a profit or not.
 */
export default {
  name: 'Trades',
  components: { TradesTable, CompanyBreadCrumb },
  props: ['companyName'],
  data() {
    return {
      name: this.companyName,
      url: (page, size) => Api.tradesCompany(this.$route.params.isin, page, size),
    };
  },
  beforeMount() {
    if (this.name === undefined) {
      this.name = '';
      this.$http.get(Api.company(this.$route.params.isin)).then((r) => {
        this.name = r.data.name;
      });
    }
  },
  computed: {
    headlineName() {
      return `Trades - ${this.name}`;
    },
  },
};
</script>
