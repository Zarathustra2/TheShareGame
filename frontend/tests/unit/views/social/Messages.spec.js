import { createLocalVue, mount } from '@vue/test-utils';
import Messages from '@/views/social/Messages.vue';
import { NavbarPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
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

const mocks = {
  $http: {
    get: () => Promise.resolve({ data: { results: mockItems } }),
  },
};


describe('Messages', () => {
  let wrapper;

  const switchToForm = (wrap, tab) => {
    const elemes = wrap.find('.msg-tabs').findAll('a');
    expect(elemes.length).toBe(2);

    const elem = elemes.at(tab);

    elem.trigger('click');
  };

  beforeEach(() => {
    wrapper = mount(Messages, {
      localVue,
      mocks,
      stubs: { 'router-link': true, MessageForm: true },
    });
  });

  it('renders data', () => {
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

  it('switches tab to new message form and back', async () => {
    expect(wrapper.html()).not.toContain('messageform-stub');
    switchToForm(wrapper, 1);

    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain('messageform-stub');

    switchToForm(wrapper, 0);

    await wrapper.vm.$nextTick();

    expect(wrapper.html()).not.toContain('messageform-stub');
  });
});
