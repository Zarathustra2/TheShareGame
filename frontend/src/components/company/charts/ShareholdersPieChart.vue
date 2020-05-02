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
 * Renders a pi chart with the shareholders of this company.
 */
export default {
  name: 'ShareholdersPieChart',
  props: ['shareholders'],
  components: {
    highcharts: Chart,
  },
  data() {
    return {
      dataShareholders: [],
      chartOptions: {
        chart: {
          type: 'pie',
        },
        title: {
          text: 'Shareholders',
        },
        series: [{
          name: 'Amount',
          data: this.dataShareholders,
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
  methods: {

    /**
     * This component is used in two other components:
     *  1. Shareholders View
     *  2. Company View
     *
     *  In the shareholders view the shareholders data is already present,
     *  so we can just pass it to this component. But the data is not present in the company view.
     *  Hence we need to get it.
     */
    async getShareholders() {
      let shareholders;
      await this.$http.get(Api.shareholders(this.$route.params.isin)).then((r) => {
        shareholders = r.data;
      });
      return shareholders;
    },
  },
  async beforeMount() {
    let data = this.shareholders;
    if (data === undefined) data = await this.getShareholders();

    // TODO: Create other-field for all positions below of 5%
    // TODO: Pass copy and not reference to the same array as the table
    data.forEach((e) => {
      e.y = e.amount;
      e.name = e.depot_of.name;
    });

    this.dataShareholders = data;

    this.$emit('shareholders', data);
  },
  watch: {
    dataShareholders: {
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
