import { createLocalVue, mount, createWrapper } from '@vue/test-utils';
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
    trade: {
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
  let wrapper;
  beforeEach(() => {
    wrapper = mount(StatementOfAccount, {
      stubs: ['router-link'],
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
  });

  it('renders data correctly', async () => {
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

  it('Displays order information in popup', async () => {
    wrapper.find('.order-info-btn').trigger('click');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let modal = document.querySelector('#order-info');
    modal = createWrapper(modal);

    const item = mockItems[1].trade;

    expect(modal.html()).toContain(item.seller.name);
    expect(modal.html()).toContain(item.buyer.name);
    expect(modal.html()).toContain(item.company.name);
  });

  it('gets name via http if not present in props', async () => {
    wrapper = mount(StatementOfAccount, {
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
