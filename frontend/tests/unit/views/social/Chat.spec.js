import { shallowMount, createLocalVue } from '@vue/test-utils';
import Chat from '@/views/social/Chat.vue';

const localVue = createLocalVue();

describe('Chat', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(Chat, {
      localVue,
    });
  });

  it('renders', () => {
    // TODO: Obvisously...
    expect(wrapper.html()).toContain('chatbox-stub');
  });
});
