import { createLocalVue, mount } from '@vue/test-utils';

import ThreadForm from '@/components/social/ThreadForm.vue';

const localVue = createLocalVue();

const validName = 'new-thread';
const inValidName = 'invalid-name';

describe('ThreadForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ThreadForm, {
      localVue,
      mocks: {
        $http: {
          post: (_, data) => {
            if (data.name === validName) {
              return Promise.resolve();
            }
            return Promise.reject({
              response: {
                data: {
                  name: 'Name Error!',
                },
              },
            });
          },
        },
      },
    });
  });

  it('displays error messages', async () => {
    wrapper.setData({
      form: {
        name: inValidName,
      },
    });

    wrapper.find('.submit-btn').trigger('submit');

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain('Name Error!');
  });

  it('emits event if new thread has been created', async () => {
    wrapper.setData({
      form: {
        name: validName,
      },
    });

    wrapper.find('.submit-btn').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('forceReload')).toBeTruthy();
  });
});
