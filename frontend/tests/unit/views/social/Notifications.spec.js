import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';

import Notifications from '@/views/social/Notifications.vue';

import { Table } from '@/service/utils';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);

const mockItems = [
  {
    text: 'Your Order for the company Invest Inc. has been cancelled!',
    subject: 'Order cancelled',
    created: '10/07/2019 19:37',
    read: false,
    id: 2,
  },
  {
    text: 'Bond payed out! You received 120,345$!',
    subject: 'Bond payed out!',
    created: '10/07/2019 9:20',
    read: true,
    id: 1,

  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));


describe('Notifications', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(Notifications, {
      localVue,
      router,
      stubs: ['router-link'],
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

      expect(tr.find('.subject').text()).toMatch(item.subject);
      expect(tr.find('.received').text()).toMatch(item.created);

      const readSpan = (item.read) ? '<span class="fas fa-check text-success"></span>' : '<span class="fas fa-envelope text-danger"></span>';

      expect(tr.find('#read').html()).toMatch(readSpan);
    }
  });
});
