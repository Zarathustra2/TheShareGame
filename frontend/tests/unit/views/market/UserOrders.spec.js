import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import UserOrders from '@/views/market/UserOrders.vue';
import { Table } from '@/service/utils';
import getTableDataMock from '../../utilsMock';
import mockRouter from '../../mockRouter';

import { mockItems, checkWrapper } from './orders_utils';

const localVue = createLocalVue();
const router = mockRouter.mock();
localVue.use(VueRouter);

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));

describe('UserOrders', () => {
  it('renders data correctly', async () => {
    const wrapper = mount(UserOrders, {
      localVue, router,
    });

    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    checkWrapper(wrapper);
  });
});
