import { mount, createLocalVue } from '@vue/test-utils';
import VueRouter from 'vue-router';
import LinksSheets from '@/components/company/LinksSheets.vue';
import mockRouter from '../../mockRouter';


const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();

describe('LinksSheet', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(LinksSheets, {
      localVue,
      router,
      propsData: {
        isin: 'JP000001',
        user: { id: 1, username: 'Son Goku' },
      },
    });
  });

  it('matches Snapshot', () => {
    expect(wrapper).toMatchSnapshot();
  });
});
