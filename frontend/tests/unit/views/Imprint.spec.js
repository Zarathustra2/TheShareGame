import { mount, createLocalVue } from '@vue/test-utils';
import Imprint from '@/views/Imprint.vue';
import VueRouter from 'vue-router';
import mockRouter from '../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();

describe('Imprint.vue', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(Imprint, { localVue, router });
  });

  it('matches Snapshot', () => {
    expect(wrapper).toMatchSnapshot();
  });
});
