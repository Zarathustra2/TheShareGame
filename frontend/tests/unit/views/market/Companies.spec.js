import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import Companies from '@/views/market/Companies.vue';
import { Table } from '../../../../src/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();
localVue.use(VueRouter);
const router = new VueRouter();

const mockItems = [
  { isin: 'US000001', name: 'Vue Inc.', user: { username: 'Joe Blocks' } },
  { isin: 'US000002', name: 'Share Inc.', user: { username: 'Joe Blocks' } },
  { isin: 'US000003', name: 'Game Inc.', user: { username: 'Joe Blocks' } },
  { isin: 'US000004', name: 'Centralbank', user: null },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('Companies', () => {
  it('renders data and updates on page change', async () => {
    const wrapper = mount(Companies, {
      localVue, router, stubs: ['router-link'],
    });
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(mockItems.length);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];
      expect(tr.find('.name').text()).toMatch(item.name);
      expect(tr.find('.isin').text()).toMatch(item.isin);

      if (item.user !== null) expect(tr.find('.ceo').text()).toMatch(item.user.username);
    }
  });
});
