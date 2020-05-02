import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import Shareholders from '@/views/company/Shareholders.vue';
import Api from '@/service/api';


const localVue = createLocalVue();
localVue.use(HighchartsVue);

describe('Shareholders', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Shareholders, {
      localVue,
      stubs: ['router-link'],
      mocks: {
        $http: {
          get: (url) => {
            if (url === Api.company('RS000001')) {
              const data = {
                name: 'Russia Invest',
                key_figures: { share_price: 2.00 },
              };
              return Promise.resolve({ data });
            }
            if (url === Api.shareholders('RS000001')) {
              const data = [];
              return Promise.resolve({ data });
            }
            return Promise.resolve();
          },
        },
        $route: {
          params: { isin: 'RS000001' },
        },
      },
    });
  });

  it('makes api call if name or share_price props not present', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.name).toEqual('Russia Invest');
    expect(wrapper.vm.sharePrice).toEqual(2.00);
  });
});
