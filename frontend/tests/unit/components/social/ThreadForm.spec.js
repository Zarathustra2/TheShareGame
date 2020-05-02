import { createLocalVue, mount } from '@vue/test-utils';

import VueRouter from 'vue-router';
import ThreadForm from '@/components/social/ThreadForm.vue';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);


describe('ThreadForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ThreadForm, {
      localVue,
      router,
      mocks: {
        $http: {

        },
      },
    });
  });

  it('displays error messages', async () => {
    const keys = ['nameErrMsg', 'errMessage'];

    const data = {
      formFeedback: {
        nameValid: false,
        nameErrMsg: 'Name Error!',
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
