<template>
  <div>
    <highcharts :options="chartOptions"/>
  </div>
</template>

<script>
import Api from '@/service/api';
import { Chart } from 'highcharts-vue';

import Highcharts from 'highcharts';
import theme from '@/highcharts_theme';

Highcharts.setOptions(theme);

/**
 * Pie chart for a company displaying its liquidity
 *
 * It is split up in 3 sections:
 *  1. cash
 *  2. bonds
 *  3. depot
  */
export default {
  name: 'LiquidityPieChart',
  components: {
    highcharts: Chart,
  },
  data() {
    return {

      dataLiquidity: [],
      chartOptions: {
        chart: {
          type: 'pie',
        },

        title: {
          text: 'Liquidity',
        },
        series: [{
          name: 'Value',
          data: this.dataLiquidity,
        }],
        tooltip: {
          headerFormat: '',
          pointFormat: 'Value: <span>{point.y}$</span>',
        },
        plotOptions: {
          pie: {
            allowPointSelect: true,
            cursor: 'pointer',

            dataLabels: {
              enabled: true,
              format: '<b>{point.name}</b><br>{point.percentage:.1f} %',
              distance: -50,
              filter: {
                property: 'percentage',
                operator: '>',
                value: 4,
              },
            },
          },
        },

      },
    };
  },
  beforeMount() {
    const { isin } = this.$route.params;

    this.$http.get(Api.liquidity(isin)).then((r) => {
      const { data } = r;
      const liquidity = [];

      Object.keys(data).forEach((key) => {
        const d = {};

        // Capitalize a name the javascript way....
        d.name = key.charAt(0).toUpperCase() + key.slice(1);
        d.y = data[key];
        let color;
        switch (d.name) {
          case 'Cash':
            color = 'grey';
            break;
          case 'Bonds':
            color = 'green';
            break;
          case 'Depot_value':
          case 'Depot':
            color = 'blue';
            break;
          default:
            console.error('Unexpected key: ', d.name);
        }
        d.color = color;
        liquidity.push(d);
      });

      this.dataLiquidity = liquidity;
    });
  },
  watch: {
    dataLiquidity: {
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
