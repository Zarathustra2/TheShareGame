import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import LiquidityPieChart from '@/components/company/charts/LiquidityPieChart.vue';


const localVue = createLocalVue();
localVue.use(HighchartsVue);

const mockData = { cash: 100000, bonds: 250000, depot: 50000 };

describe('LiquidityPieChart', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(LiquidityPieChart, {
      localVue,
      mocks: {
        $route: {
          params: {
            isin: 'NR000001',
          },
        },
        $http: {
          get: () => Promise.resolve({ data: mockData }),
        },
      },
    });
  });

  it('sets data correctly', async () => {
    await wrapper.vm.$nextTick();
    const { data } = wrapper.vm.chartOptions.series[0];
    data.forEach((e) => {
      const key = e.name.toLowerCase();
      expect(mockData[key]).toBe(e.y);
    });

    const mockDataLength = Object.keys(mockData).length;

    expect(mockDataLength).toBe(data.length);
  });
});
