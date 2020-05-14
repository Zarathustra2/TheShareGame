import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import MarketTrades from '@/views/market/MarketTrades.vue';
import { Number } from '@/service/utils';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
const router = mockRouter.mock();
localVue.use(VueRouter);

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

describe('MarketTrades', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(MarketTrades, {
      localVue,
      router,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data: { results: mockItems } }),
        },
      },
    });
  });

  it('renders the data', async () => {
    expect(wrapper.exists()).toBe(true);

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    for (let i = 0; i < mockItems.length; i++) {
      const item = mockItems[i];
      expect(wrapper.html()).toContain(Number.formatNumber(item.amount));
    }
  });
});
