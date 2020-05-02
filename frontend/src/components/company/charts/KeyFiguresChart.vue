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
 * Renders a line chart with the most recent key figures of this company.
 */
export default {
  name: 'KeyFigures',
  components: {
    highcharts: Chart,
  },
  data() {
    return {
      book_value: [],
      ttoc: [],
      share_price: [],
      dates: [],
      chartOptions: {
        chart: {
          type: 'line',
        },
        xAxis: {
          type: 'datetime',

          title: {
            text: 'Day',
          },
        },
        yAxis: {
          title: {
            text: '',
          },
          labels: {
            formatter() {
              return `${this.value}$`;
            },
          },

        },
        title: {
          text: 'Key Figures',
        },
        tooltip: {
          headerFormat: '',
          pointFormat: '{series.name}: <span>{point.y}$</span>',
        },
        series: [{
          data: this.book_value,
          name: 'BV',
        }, {
          data: this.share_price,
          name: 'Share Price',
        }, {
          data: this.ttoc,
          name: 'TTOC',
        }],
      },
    };
  },
  mounted() {
    this.$http.get(Api.past_key_figures(this.$route.params.isin)).then((r) => {
      const { data } = r;
      data.forEach((d) => {
        const {
          shares, book_value, ttoc, share_price, // eslint-disable-line camelcase
        } = d;
        const day = DateParse.parseToUTC(d.day);
        this.book_value.push(
          [day, this.round(book_value / shares)], // eslint-disable-line camelcase
        );

        this.ttoc.push(
          [day, this.round(ttoc / shares)],
        );

        this.share_price.push(
          [day, share_price], // eslint-disable-line camelcase
        );
      });
    });
  },
  methods: {
    round(num) {
      return Math.round(num * 1000) / 1000;
    },
  },
  watch: {
    book_value: {
      handler() {
        this.chartOptions.series[0].data = this.book_value;
        this.chartOptions.series[1].data = this.share_price;
        this.chartOptions.series[2].data = this.ttoc;
      },
      deep: true,
    },
  },
};
</script>

<style scoped>

</style>
