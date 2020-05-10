import { createLocalVue, mount } from '@vue/test-utils';

import ThreadDetailForm from '@/components/social/ThreadDetailForm.vue';

const localVue = createLocalVue();

const validText = 'hey';
const inValidText = 'invalid';

describe('ThreadDetailForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ThreadDetailForm, {
      localVue,
      mocks: {
        $route: {
          params: { id: 1 },
        },
        $http: {
          post(_, data) {
            if (data.text === validText) {
              return Promise.resolve();
            }
            return Promise.reject({
              response: {
                data: {
                  text: 'Text too long!',
                },
              },
            });
          },
        },
      },
    });
  });

  it('displays error messages', async () => {
    wrapper.setData({ form: { text: inValidText } });
    wrapper.find('.submit-btn').trigger('submit');

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain('Text too long!');
  });

  it('emits event if new thread post has been created', async () => {
    wrapper.setData({
      form: {
        text: validText,
      },
    });

    wrapper.find('.submit-btn').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('forceReload')).toBeTruthy();
  });
});
