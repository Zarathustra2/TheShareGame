import { createLocalVue, shallowMount } from '@vue/test-utils';
import LiquidityOverview from '@/components/company/LiquidityOverview.vue';

import { Number } from '@/service/utils';

const localVue = createLocalVue();

const data = {
  cash: 1033212,
  bonds: 55322,
  buy_orders: 7792,
};

describe('LiquidityOverview', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(LiquidityOverview, {
      localVue,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data }),
        },
      },
    });
  });

  it('renders the data formatted', () => {
    const cashFormatted = Number.numberWithDollar(data.cash);
    const buyOrdersFormatted = Number.numberWithDollar(data.buy_orders);

    const total = Number.numberWithDollar(data.cash - data.buy_orders);

    expect(wrapper.html()).toContain(cashFormatted);
    expect(wrapper.html()).toContain(buyOrdersFormatted);
    expect(wrapper.html()).toContain(total);
  });
});
