import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import Shareholders from '@/views/company/Shareholders.vue';
import Api from '@/service/api';
import { Number } from '@/service/utils';


const localVue = createLocalVue();
localVue.use(HighchartsVue);

const shareholders = [
  {
    depot_of: {
      name: 'Centralbank',
      user_id: null,
      isin: 'US000001',
      id: 1,
    },
    amount: 13122,
    price_bought: 0.0,
    created: '04/16/2020 17:19',
    private_depot: false,
    id: 1,
  },
  {
    depot_of: {
      name: 'Black Mamba Inc',
      user_id: 6,
      isin: 'GE000004',
      id: 4,
    },
    amount: 5058,
    price_bought: 0.0,
    created: '04/17/2020 16:38',
    private_depot: false,
    id: 4,
  },
];

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
              return Promise.resolve({ data: shareholders });
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

  it('renders the shareholders', () => {
    for (let i = 0; i < shareholders.length; i++) {
      const item = shareholders[i];
      expect(wrapper.html()).toContain(Number.formatNumber(item.amount));

      // Renders the value as well. Value is the amount multiplied with the current
      // share price of the company.
      expect(wrapper.html()).toContain(Number.numberWithDollar(item.amount * 2.00));

      expect(wrapper.html()).toContain(item.depot_of.name);
    }
  });


  it('does not call for company name & share price if present', () => {
    wrapper = mount(Shareholders, {
      localVue,
      stubs: ['router-link'],
      propsData: {
        companyName: 'secret company',
        sharePriceCompany: 42,
      },
      mocks: {
        $http: {
          get: (url) => {
            if (url === Api.company('RS000001')) {
              // eslint-disable-next-line
              fail('Should not ask for company name and share price!');
            }
            if (url === Api.shareholders('RS000001')) {
              return Promise.resolve({ data: shareholders });
            }
            return Promise.resolve();
          },
        },
        $route: {
          params: { isin: 'RS000001' },
        },
      },
    });

    expect(wrapper.vm.sharePrice).toEqual(42);
    expect(wrapper.vm.name).toEqual('secret company');
  });
});
