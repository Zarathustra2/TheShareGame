import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';

import Messages from '@/views/social/Messages.vue';

import { Table } from '@/service/utils';
import { NavbarPlugin } from 'bootstrap-vue';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);
localVue.use(NavbarPlugin);

const mockItems = [
  {
    subject: 'Order cancelled',
    created: '10/07/2019 19:37',
    read: false,
    id: 2,
  },
  {
    subject: 'Bond payed out!',
    created: '10/07/2019 9:20',
    read: true,
    id: 1,

  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('Messages', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Messages, { localVue, router, stubs: ['router-link'] });
  });

  it('renders data', async () => {
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(2);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];

      expect(tr.find('.subject').text()).toMatch(item.subject);
      expect(tr.find('.lastMessage').text()).toMatch(item.created);

      const readSpan = (item.read) ? '<span class="fas fa-check text-success"></span>' : '<span class="fas fa-envelope text-danger"></span>';

      expect(tr.find('#read').html()).toMatch(readSpan);
    }
  });
});
