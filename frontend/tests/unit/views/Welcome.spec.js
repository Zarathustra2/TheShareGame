import { mount } from '@vue/test-utils';
import Welcome from '@/views/Welcome.vue';

describe('Welcome.vue', () => {
  it('matches Snapshot', () => {
    expect(mount(Welcome)).toMatchSnapshot();
  });
});
