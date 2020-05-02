<template>
    <highcharts :options="chartOptions"></highcharts>
</template>

<script>
import Api from '@/service/api';
import { DateParse } from '@/service/utils';
import { Chart } from 'highcharts-vue';

import Highcharts from 'highcharts';
import theme from '@/highcharts_theme';

Highcharts.setOptions(theme);

/**
 * Renders a highchart with the most recent bond rates
 */
export default {
  name: 'BondsRateChart',
  components: {
    highcharts: Chart,
  },
  data() {
    return {
      rates: [],
      chartOptions: {
        chart: {
          type: 'line',
        },
        xAxis: {
          type: 'datetime',

          title: {
            text: 'Time',
          },
        },
        yAxis: {
          title: {
            text: 'Rates',
          },

        },
        title: {
          text: 'Rates',
        },
        tooltip: {
          headerFormat: '',
        },
        series: [{
          data: this.rates,
          name: 'Bond-Rate',
        }],
      },
    };
  },
  mounted() {
    this.$http.get(Api.rates()).then((r) => {
      const { data } = r;

      this.rates = data.map((e) => {
        const d = [];
        d[0] = DateParse.parseToUTC(e.created);
        d[1] = e.rate;
        return d;
      });
    }).catch((err) => {
      console.error(err);
    });
  },
  watch: {
    rates: {
      handler(newValue) {
        this.chartOptions.series[0].data = newValue;
      },
      deep: true,
    },
  },
};
</script>

<style scoped>

</style>
