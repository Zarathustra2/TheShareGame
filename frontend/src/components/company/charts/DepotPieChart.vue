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
 * Renders a depot pie chart of the company with all of his shares.
 */
export default {
  name: 'DepotPieChart',
  components: {
    highcharts: Chart,
  },
  data() {
    return {
      dataDepot: [],
      chartOptions: {
        chart: {
          type: 'pie',
        },
        title: {
          text: 'Depot',
        },
        tooltip: {
          headerFormat: '',
          pointFormat: 'Value: <span>{point.y}$</span>',
        },
        series: [{
          name: 'Value',
          data: this.dataDepot,
        }],
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
  mounted() {
    const { isin } = this.$route.params;
    this.$http.get(Api.depotPieChart(isin)).then((r) => {
      const { data } = r;
      data.forEach((e) => {
        e.y = e.value;
        delete e.value;
      });
      this.dataDepot = data;

      this.dataDepot.sort((a, b) => a.y < b.y);

      this.$emit('depot', data);
    });
  },
  watch: {
    dataDepot: {
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
