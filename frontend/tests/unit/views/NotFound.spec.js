import { mount } from '@vue/test-utils';
import NotFound from '@/views/NotFound.vue';

describe('Welcome.vue', () => {
  it('matches Snapshot', () => {
    expect(mount(NotFound)).toMatchSnapshot();
  });
});
