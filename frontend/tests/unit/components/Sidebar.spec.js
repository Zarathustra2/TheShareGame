import { createLocalVue, mount } from '@vue/test-utils';
import Sidebar from '@/components/Sidebar.vue';
import VueRouter from 'vue-router';
import mockRouter from '../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();

const data = {
  companies: [
    {
      name: 'A', share_price: 5, id: 0, isin: 'GE000001',
    },
    {
      name: 'B', share_price: 6, id: 1, isin: 'GE000002',
    },
    {
      name: 'C', share_price: 6, id: 2, isin: 'GE000003',
    },
    {
      name: 'D', share_price: 6, id: 3, isin: 'GE000004',
    },
  ],
  companies_count: 10,
  bond_rate: 5,
  buy_orders_count: 6,
  sell_orders_count: 3,
};

describe('Sidebar.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Sidebar,
      {
        router,
        localVue,
        mocks: {
          $http: {
            get: () => Promise.resolve({ data }),
          },
        },
      });
  });

  it('renders data', () => {
    expect(wrapper.html()).toContain(data.companies_count);
    expect(wrapper.html()).toContain(data.bond_rate);
    expect(wrapper.html()).toContain(data.sell_orders_count);
    expect(wrapper.html()).toContain(data.buy_orders_count);

    for (let i = 0; i < data.companies.length; i++) {
      const c = data.companies[i];
      expect(wrapper.html()).toContain(c.name);
      expect(wrapper.html()).toContain(c.share_price);
      expect(wrapper.html()).toContain(c.id);
      expect(wrapper.html()).toContain(c.isin);
    }
  });
});
