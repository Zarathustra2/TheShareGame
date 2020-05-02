import { createLocalVue, mount } from '@vue/test-utils';

import VueRouter from 'vue-router';
import ThreadDetailForm from '@/components/social/ThreadDetailForm.vue';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);


describe('ThreadDetailForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ThreadDetailForm, {
      localVue,
      router,
      mocks: {
        $http: {

        },
      },
    });
  });

  it('displays error messages', async () => {
    const keys = ['textErrMsg', 'errMessage'];

    const data = {
      formFeedback: {
        textValid: false,
        textErrMsg: 'Name Error!',
        isValid: false,
        errMessage: 'Err Message!',
      },
    };

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    keys.forEach((e) => {
      expect(wrapper.html()).toContain(data.formFeedback[e]);
    });
  });
});
