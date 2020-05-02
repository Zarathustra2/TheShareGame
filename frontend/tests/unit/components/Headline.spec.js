import { shallowMount } from '@vue/test-utils';
import Headline from '@/components/Headline.vue';

describe('Headline.vue', () => {
  it('renders props.name when passed', () => {
    const name = 'A new headline';
    const wrapper = shallowMount(Headline, {
      propsData: { name },
    });
    expect(wrapper.text()).toMatch(name);
  });

  it('matches Snapshot', () => {
    expect(shallowMount(Headline)).toMatchSnapshot();
  });
});
