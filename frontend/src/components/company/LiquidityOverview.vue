<template>
  <div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item text-success">Cash: {{this.cashFormatted}}</li>
      <li class="list-group-item text-danger">Buy-Orders: {{this.buyOrderFormatted}}</li>
      <li class="list-group-item text-info">Available: {{this.available}}</li>
    </ul>
  </div>
</template>

<script>
import Api from '@/service/api';
import { Number } from '@/service/utils';

export default {
  name: 'LiquidityOverview',
  components: {},
  data() {
    return {
      cash: 0,
      bonds: 0,
      buyOrders: 0,
    };
  },
  mounted() {
    this.$http.get(Api.liquidityOverview()).then((r) => {
      console.log(r);
      const { data } = r;
      this.cash = data.cash;
      this.bonds = data.bonds;
      this.buyOrders = data.buy_orders;
    });
  },
  computed: {
    cashFormatted() {
      return Number.numberWithDollar(this.cash);
    },
    buyOrderFormatted() {
      return Number.numberWithDollar(this.buyOrders);
    },
    available() {
      return Number.numberWithDollar(this.cash - this.buyOrders);
    },
  },
};
</script>

<style scoped>

</style>
