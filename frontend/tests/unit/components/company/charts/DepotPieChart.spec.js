import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import DepotPieChart from '@/components/company/charts/DepotPieChart.vue';

const localVue = createLocalVue();
localVue.use(HighchartsVue);

const mockData = [
  {
    name: 'Big Company',
    value: 1000.0,
  },
  {
    name: 'Small Company',
    value: 10000.0,
  },
  {
    name: 'Medium Company',
    value: 5000.0,
  },
  {
    name: 'Huge Company',
    value: 14321.56,
  },

];

describe('DepotPieChart', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(DepotPieChart, {
      localVue,
      mocks: {
        $route: {
          params: {
            isin: 'NR000001',
          },
        },
        $http: {
          get: () => {
            const clone = JSON.parse(JSON.stringify(mockData));
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
      const key = e.name;
      const obj = mockData.find((elem) => elem.name === key);
      expect(obj.value).toBe(e.y);
    });

    expect(mockData.length).toBe(data.length);
  });
});
