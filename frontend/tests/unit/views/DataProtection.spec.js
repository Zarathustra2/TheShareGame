import { mount, createLocalVue } from '@vue/test-utils';
import DataProtection from '@/views/DataProtection.vue';
import VueRouter from 'vue-router';
import mockRouter from '../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();


describe('DataProtection.vue', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(DataProtection, { localVue, router });
  });

  it('matches Snapshot', () => {
    expect(wrapper).toMatchSnapshot();
  });
});
