import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import ShareholdersTable from '@/components/company/ShareholdersTable.vue';

import { Number } from '@/service/utils';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);

const data = [
  {
    depot_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    amount: 15000,
    value: 30000,
    price_bought: '0.00',
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
    value: 50000,
    price_bought: '0.00',
    day_time: '10/13/2019 16:30',
    private_depot: false,
    id: 2,
  }];

describe('ShareholdersTable', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ShareholdersTable, {
      localVue,
      router,
      stubs: ['router-link'],
      propsData: {
        shareholders: data,
      },
    });
  });

  it('renders data', () => {
    expect(wrapper.findAll('tbody > tr').length).toBe(2);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = data[i];

      const value = Number.numberWithDollar(item.value);
      const amount = Number.formatNumber(item.amount);

      expect(tr.find('.value').text()).toMatch(value);
      expect(tr.find('.amount').text()).toMatch(amount);

      expect(tr.find('.company').text()).toMatch(item.depot_of.name);
    }
  });
});
