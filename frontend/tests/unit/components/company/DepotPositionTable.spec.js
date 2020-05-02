import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import DepotPositionTable from '@/components/company/DepotPositionTable.vue';

import { Table, Number } from '@/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);

const mockItems = [{
  company: { name: 'Big Company', user_id: 2, isin: 'US000002' }, amount: 1000, price_bought: '1.00', day_time: '10/05/2019 19:04', id: 1, share_price: '1.00',
}];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('BondsTable', () => {
  it('renders data and updates on page change', async () => {
    const wrapper = mount(DepotPositionTable, { localVue, router, stubs: ['router-link'] });
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(1);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    const N = Number;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];

      expect(tr.find('.value').text()).toMatch(N.numberWithDollar(item.share_price * item.amount));
      expect(tr.find('.company').text()).toMatch(item.company.name);
      expect(tr.find('.payed').text()).toMatch(N.numberWithDollar(item.price_bought));
      expect(tr.find('.share_price').text()).toMatch(N.numberWithDollar(item.share_price));
      expect(tr.find('.amount').text()).toMatch(N.formatNumber(item.amount));
    }
  });
});
