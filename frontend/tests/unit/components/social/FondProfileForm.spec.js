import { mount, createLocalVue } from '@vue/test-utils';
import FondProfileForm from '@/components/social/FondProfileForm.vue';

const localVue = createLocalVue();
const invalidDescription = 'invalid';
const errData = {
  description: 'write more!',
};
const propsData = {
  profile: {
    description: 'hello-world!',
    open_for_application: true,
  },
};
const mocks = {
  $route: {
    params: { id: 1 },
  },
  $http: {
    put: (_, postData) => {
      if (postData.description === invalidDescription) {
        return Promise.reject({
          response: {
            data: errData,
          },
        });
      }
      return Promise.resolve({ data: postData });
    },
  },
};

describe('FondProfileForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(FondProfileForm, {
      propsData,
      localVue,
      mocks,
    });
  });

  it('renders errors', async () => {
    wrapper.setData({
      form: { description: invalidDescription },
    });

    await wrapper.vm.$nextTick();
    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(errData.description);
  });

  it('emits after successful update', async () => {
    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('profileUpdate')).toBeTruthy();
  });
});
