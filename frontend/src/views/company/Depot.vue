<template>
  <div>
    <CompanyBreadCrumb active="Depot" :companyName="name" v-bind:key="name"/>
    <p class="font-weight-light font-italic">
      In the depot one can analyze how the values of a company are distributed.
      You can see which shares this company holds, how much it has in cash and how many bonds
      it has bought and when they run out.
    </p>
    <b-row>
      <b-col sm>
        <DepotPieChart/>
      </b-col>
      <b-col sm>
        <LiquidityPieChart/>
      </b-col>
    </b-row>
    <DepotPositionTable/>
    <BondsTable/>
  </div>
</template>

<script>
import DepotPositionTable from '@/components/company/DepotPositionTable.vue';
import BondsTable from '@/components/company/BondsTable.vue';
import DepotPieChart from '@/components/company/charts/DepotPieChart.vue';
import LiquidityPieChart from '@/components/company/charts/LiquidityPieChart.vue';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';
import Api from '@/service/api';
import { BRow, BCol } from 'bootstrap-vue';

/**
 * Renders the Depot of the given company.
 *
 * A depot consists of bonds and shares.
 *
 *
 */
export default {
  name: 'Depot',
  components: {
    CompanyBreadCrumb,
    LiquidityPieChart,
    DepotPieChart,
    BondsTable,
    DepotPositionTable,
    BRow,
    BCol,
  },
  props: ['companyName'],
  data() {
    return {
      name: this.companyName,
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
};
</script>

<style scoped>

</style>
