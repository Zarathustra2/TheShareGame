<template>
  <div>
    <Headline name="Market Trades"/>
    <p class="font-weight-light font-italic">
      The last trades which have happened in the market. Scroll through the table to get even more
      results.
    </p>
    <TradesTable :url="url"/>
  </div>
</template>

<script>

import Headline from '@/components/Headline.vue';
import TradesTable from '@/components/TradesTable.vue';
import Api from '@/service/api';

/**
 * Renders all recent trades of the market, meaning shares which got sold.
 */
export default {
  name: 'MarketTrades',
  components: { TradesTable, Headline },
  data() {
    return {
      url: (page, size, ctx) => Api.trades(page, size, ctx),
    };
  },
};
</script>
