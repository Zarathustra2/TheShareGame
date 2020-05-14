import { createLocalVue, mount } from '@vue/test-utils';
import Trades from '@/views/company/Trades.vue';
import { Number } from '@/service/utils';

const localVue = createLocalVue();

const mockItems = [
  {
    buyer: null,
    seller: null,
    company: null,
    price: '5.56',
    amount: 10000,
    price_bought: '2.00',
    day_time: '09/29/2019 09:28',
    buyer_pd: false,
    seller_pd: false,
    value: '55600.00',
    id: 2,
    history: {
      buyer_name: 'Ramm Inc.',
      seller_name: 'Cool Inc.',
      company_name: 'Comp Inc.',
    },
  },
  {
    buyer: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    seller: {
      name: 'Big Company',
      user_id: 2,
      isin: 'US000002',
    },
    company: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    price: '2.00',
    amount: 1000,
    price_bought: '1.50',
    day_time: '09/29/2019 09:16',
    buyer_pd: false,
    seller_pd: false,
    value: '2000.00',
    id: 1,
    history: {},
  },
];

describe('Trades', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Trades, {
      localVue,
      stubs: ['router-link'],
      mocks: {
        $route: {
          params: { isin: 'RU002346' },
        },
        $http: {
          get(url) {
            if (!url.includes('trade')) {
              return Promise.resolve({ data: { name: 'Company Name' } });
            }
            const copy = JSON.parse(JSON.stringify(mockItems));
            return Promise.resolve({ data: { results: copy } });
          },
        },
      },
    });
  });

  it('fetches the company name if not provided', () => {
    expect(wrapper.vm.name).toEqual('Company Name');
  });

  it('renders the data', async () => {
    await wrapper.vm.$nextTick();

    for (let i = 0; i < mockItems.length; i++) {
      const item = mockItems[i];
      expect(wrapper.html()).toContain(Number.numberWithDollar(item.price));
    }
  });
});
