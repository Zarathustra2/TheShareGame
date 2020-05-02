import { createLocalVue, mount } from '@vue/test-utils';
import BondsTable from '@/components/company/BondsTable.vue';

import { Table, Number } from '@/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();

const mockItems = [
  {
    id: 1,
    value: '100000.00',
    rate: '2.50',
    runtime: 3,
    expires: '10/09/2019 12:21',
  },
  {
    id: 2,
    value: '20000.00',
    rate: '3.50',
    runtime: 2,
    expires: '10/09/2019 12:21',
  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('BondsTable', () => {
  it('renders data and updates on page change', async () => {
    const wrapper = mount(BondsTable, { localVue });
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(2);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    const N = Number;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];

      expect(tr.find('.value').text()).toMatch(N.numberWithDollar(item.value));
      expect(tr.find('.rate').text()).toMatch(`${item.rate}%`);
      expect(tr.find('.runtime').text()).toMatch(`${item.runtime}`);
      expect(tr.find('.expires').text()).toMatch(item.expires);
    }
  });
});
