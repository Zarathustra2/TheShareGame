import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import ShareholdersPieChart from '@/components/company/charts/ShareholdersPieChart.vue';

const localVue = createLocalVue();
localVue.use(HighchartsVue);

const mockData = [
  {
    depot_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    amount: 15000,
    price_bought: 0.0,
    day_time: '10/13/2019 16:30',
    private_depot: false,
    id: 3,
  },
  {
    depot_of: {
      name: 'Big Company',
      user_id: 2,
      isin: 'US000002',
    },
    amount: 10000,
    price_bought: 0.0,
    day_time: '10/13/2019 16:30',
    private_depot: false,
    id: 2,
  },
];

describe('ShareholdersPieChart', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ShareholdersPieChart, {
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
      const obj = mockData.find((elem) => elem.depot_of.name === key);
      expect(obj.amount).toBe(e.y);
    });

    expect(mockData.length).toBe(data.length);
  });
});
