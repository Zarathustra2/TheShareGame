<template>
  <div>
    <CompanyBreadCrumb active="Orderbook" :companyName="name" v-bind:key="name"/>
    <p class="font-weight-light font-italic">
      In the Orderbook one can view the amount of sell and buy orders for this company.
    </p>

    <OrderbookTable/>
  </div>
</template>

<script>
import OrderbookTable from '@/components/company/OrderbookTable.vue';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';
import Api from '@/service/api';

/**
 * Renders all orders which have been issued for this company.
 */
export default {
  name: 'Orderbook',
  components: { CompanyBreadCrumb, OrderbookTable },
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
