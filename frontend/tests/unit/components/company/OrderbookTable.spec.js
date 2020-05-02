
import { createLocalVue, mount } from '@vue/test-utils';

import OrderbookTable from '@/components/company/OrderbookTable.vue';

import { Table, Number } from '@/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();

const mockItems = [
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Sell',
    price: 8.0,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 8000.0,
    id: 23,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Sell',
    price: 6.0,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 6000.0,
    id: 22,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Buy',
    price: 5.0,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 5000.0,
    id: 19,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Buy',
    price: 4.99,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 4990.0,
    id: 20,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Buy',
    price: 4.98,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 4980.0,
    id: 21,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Buy',
    price: 2.0,
    amount: 1000,
    created: '10/16/2019 18:42',
    value: 2000.0,
    id: 18,
  },
  {
    order_of: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Buy',
    price: 2.0,
    amount: 100000,
    created: '10/16/2019 18:43',
    value: 200000.0,
    id: 24,
  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('OrderbookTable', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(OrderbookTable, {
      localVue,
      stubs: ['router-link'],
      mocks: {
        $route: {
          params: {
            isin: 'RU000001',
          },
        },
      },
    });
  });

  it('renders data', async () => {
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(7);

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
      expect(tr.find('.typ').text()).toMatch(item.typ);
    }
  });
});
