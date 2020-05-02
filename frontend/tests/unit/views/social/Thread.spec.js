import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';

import Forum from '@/views/social/Forum.vue';

import { Table } from '@/service/utils';
import mockRouter from '../../mockRouter';
import getTableDataMock from '../../utilsMock';


const localVue = createLocalVue();
const router = mockRouter.mock();
localVue.use(VueRouter);

const mockItems = [
  {
    name: 'TestTest',
    user: {
      id: 1,
      username: 'dario',
    },
    slug: 'testtest',
    created: '2019-10-28T21:00:55.104922Z',
    updated: '2019-10-28T21:00:55.104947Z',
    locked: false,
    pinned: false,
    id: 4,
  },
  {
    name: 'Suggestion for improving',
    user: {
      id: 1,
      username: 'dario',
    },
    slug: 'suggestion-for-improving',
    created: '2019-10-28T20:48:11.978413Z',
    updated: '2019-10-28T20:48:11.978430Z',
    locked: true,
    pinned: true,
    id: 3,
  },
  {
    name: 'News',
    user: {
      id: 1,
      username: 'dario',
    },
    slug: 'news',
    created: '2019-10-28T20:40:20.966654Z',
    updated: '2019-10-28T20:40:20.966693Z',
    locked: false,
    pinned: false,
    id: 2,
  },
];

jest.spyOn(Table, 'getTableData').mockImplementation(getTableDataMock(mockItems));


describe('Forum', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(Forum, {
      localVue,
      router,
      stubs: ['router-link'],
    });
  });

  it('renders data', async () => {
    expect(Table.getTableData).toBeCalled();

    await wrapper.vm.$nextTick();

    expect(wrapper.findAll('tbody > tr').length).toBe(3);

    const $trs = wrapper.findAll('tbody > tr').wrappers;

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = mockItems[i];

      expect(tr.find('.name').text()).toMatch(item.name);


      const pinned = (item.pinned) ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-danger"></i>';
      const locked = (item.locked) ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-danger"></i>';

      expect(tr.find('.pinned').html()).toContain(pinned);
      expect(tr.find('.locked').html()).toContain(locked);
    }
  });
});
