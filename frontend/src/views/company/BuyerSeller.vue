<template>
  <div>
    <CompanyBreadCrumb active="Buyer-Seller" :companyName="name" v-bind:key="name"/>
    <p class="font-weight-light font-italic">
      In the Buyer & Seller view one can see who has bought sold the company in the most recent
      time.
    </p>
    <TradesTable
      :url="url"
      :disabledFields="disabledFields"
    >
    </TradesTable>
  </div>

</template>

<script>

import Api from '@/service/api';
import TradesTable from '@/components/TradesTable.vue';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';

/**
 * Renders all recent buyers and sellers of the company, or in other words:
 *  All the trades where this company got traded.
 */
export default {
  name: 'BuyerSeller',
  components: { CompanyBreadCrumb, TradesTable },
  props: ['companyName'],
  data() {
    return {
      url: (page, size) => Api.buyerSeller(this.$route.params.isin, page, size),
      disabledFields: ['company'],
      name: this.companyName,
    };
  },
  beforeMount() {
    if (this.name !== undefined) {
      return;
    }

    this.$http.get(Api.company(this.$route.params.isin)).then((r) => {
      this.name = r.data.name;
    });
  },
};
</script>

<style scoped>

</style>
