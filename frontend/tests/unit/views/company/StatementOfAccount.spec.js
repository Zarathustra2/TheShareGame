import { createLocalVue, mount, shallowMount } from '@vue/test-utils';
import StatementOfAccount from '@/views/company/StatementOfAccount.vue';
import { Table, Number } from '@/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();

const mockItems = [
  {
    company: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Bond',
    value: '100000.00',
    received: true,
    day_time: '10/04/2019 15:19',
    id: 3,
    amount: 5999,
    extras: {},
  },
  {
    company: {
      name: 'Django Inc.',
      user_id: 1,
      isin: 'GE000001',
    },
    typ: 'Order',
    value: '100000.00',
    received: true,
    day_time: '10/04/2019 15:19',
    id: 1,
    amount: 5999,
    extras: {
      price: 2.0,
      seller: {
        name: 'Big Company',
        user_id: 2,
        isin: 'US000002',
      },
      buyer: {
        name: 'Django Inc.',
        user_id: 1,
        isin: 'GE000001',
      },
      company: {
        name: 'Cardiff Inc.',
        user_id: 3,
        isin: 'US000003',
      },
    },
  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('StatementOfAccount', () => {
  it('renders data correctly', async () => {
    const wrapper = mount(StatementOfAccount, {
      localVue,
      mocks: {
        $route: {
          params: {
            isin: 'GE000007',
          },
        },
      },
      propsData: {
        companyName: 'SomeGermanName',
      },
    });

    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(2);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    const N = Number;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];
      expect(tr.find('.value').text()).toMatch(N.numberWithDollar(item.value));
      expect(tr.find('.typ').text()).toMatch(item.typ);
      expect(tr.find('.amount').text()).toMatch(N.formatNumber(item.amount));
    }
  });

  it('gets name via http if not present in props', async () => {
    const wrapper = shallowMount(StatementOfAccount, {
      localVue,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data: { name: 'name' } }),
        },
        $route: {
          params: {
            isin: 'RU000001',
          },
        },
      },
    });

    await wrapper.vm.$nextTick();
    expect(wrapper.vm.name).toEqual('name');
  });
});
