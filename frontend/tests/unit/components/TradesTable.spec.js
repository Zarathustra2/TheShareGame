
import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import TradesTable from '@/components/TradesTable.vue';

import { Table, Number } from '@/service/utils';
import getTableDataMock from '../utilsMock';
import mockRouter from '../mockRouter';

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

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));
jest.spyOn(Table, 'getTableNameAndCompanyName').mockImplementation(jest.fn(() => {}));

describe('TradesTable', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(TradesTable, {
      localVue,
      router,
      propsData: {
        url: 'url/',
      },
    });
  });

  it('renders data', async () => {
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(2);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];

      const value = Number.numberWithDollar(item.value);
      const price = Number.numberWithDollar(item.price);
      const amount = Number.formatNumber(item.amount);

      expect(tr.find('.value').text()).toMatch(value);
      expect(tr.find('.price').text()).toMatch(price);
      expect(tr.find('.amount').text()).toMatch(amount);

      const buyerName = (item.buyer === null) ? item.history.buyer_name : item.buyer.name;
      const sellerName = (item.seller === null) ? item.history.seller_name : item.seller.name;
      const companyName = (item.company === null) ? item.history.company_name : item.company.name;

      expect(tr.find('.buyer').text()).toMatch(buyerName);
      expect(tr.find('.seller').text()).toMatch(sellerName);
      expect(tr.find('.company').text()).toMatch(companyName);
    }
  });

  it('disabledFields are not shown', async () => {
    const { fields } = wrapper;
    wrapper = mount(TradesTable, {
      localVue,
      router,
      propsData: {
        url: 'url/',
        disabledFields: ['company'],
      },
    });

    expect(wrapper.vm.fields).not.toEqual(fields);
    expect(wrapper.vm.fields.filter((e) => e.key === 'company')).toEqual([]);
  });
});
