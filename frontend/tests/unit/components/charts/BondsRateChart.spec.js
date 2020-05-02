import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import BondsRateChart from '@/components/charts/BondsRateChart.vue';
import { DateParse } from '@/service/utils';

const localVue = createLocalVue();
localVue.use(HighchartsVue);

const mockRateData = [
  {
    rate: 2.5,
    created: '2019-12-27T15:19:32.697000Z',
    id: 1,
  },
  {
    rate: 3.0,
    created: '2019-12-27T16:19:38.226000Z',
    id: 2,
  },
  {
    rate: 2.7,
    created: '2019-12-27T17:19:53.984000Z',
    id: 3,
  },
];

describe('BondsRateChart', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(BondsRateChart, {
      localVue,
      mocks: {
        $http: {
          get: () => {
            const clone = JSON.parse(JSON.stringify(mockRateData));
            return Promise.resolve({ data: clone });
          },
        },
      },
    });
  });

  it('sets data correctly', async () => {
    await wrapper.vm.$nextTick();
    const { data } = wrapper.vm.chartOptions.series[0];

    data.forEach((e) => {
      expect(e.length).toBe(2);

      // rate is unique in the mock data, so we can use it as a key
      const key = e[1];
      const obj = mockRateData.find((elem) => elem.rate === key);

      expect(e[0]).toEqual(DateParse.parseToUTC(obj.created));
    });

    expect(mockRateData.length).toBe(data.length);
  });
});
