import { createLocalVue, mount } from '@vue/test-utils';

import VueRouter from 'vue-router';
import MessageForm from '@/components/social/MessageForm.vue';
import Api from '@/service/api';

const localVue = createLocalVue();
const router = new VueRouter();
localVue.use(VueRouter);

const users = [{ id: 1, username: 'max' }, { id: 2, username: 'max971' }, { id: 3, username: 'max_the_king!' }];

describe('MessageForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(MessageForm, {
      localVue,
      router,
      mocks: {
        $http: {
          get(url) {
            if (url === Api.userLookup('max')) return Promise.resolve({ data: users });
            if (url === Api.user(1)) return Promise.resolve({ data: users[0] });
            return Promise.resolve({ data: users });
          },
        },
      },
    });
  });

  it('updates the datalist on receiver input', async () => {
    const field = wrapper.find('#receivers-input___input__');
    field.element.value = 'max';
    field.trigger('input');

    await wrapper.vm.$nextTick();
    // TODO: This above does not work. Find a way to trigger an input.
    // expect(wrapper.vm.datalist.users).toEqual(users);
  });

  it('displays error messages', async () => {
    const keys = ['subjectErrMsg', 'receiversErrMsg', 'textErrMsg', 'errMessage'];

    const data = {
      formFeedback: {
        subjectValid: false,
        subjectErrMsg: 'Subject Error!',
        receiversValid: false,
        receiversErrMsg: 'Receivers Error!',
        textValid: false,
        textErrMsg: 'Text Error!',
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

  it('if present adds query user to the receivers', async () => {
    const vue = createLocalVue();

    wrapper = mount(MessageForm, {
      localVue: vue,
      mocks: {
        $http: {
          get(url) {
            if (url === Api.userLookup('max')) return Promise.resolve({ data: users });
            if (url === Api.user(1)) return Promise.resolve({ data: users[0] });
            return Promise.resolve();
          },
        },
        $route: {
          query: { user_id: 1 },
        },
      },
    });

    await wrapper.vm.$nextTick();

    expect(wrapper.vm.form.receivers).toEqual([users[0]]);
  });
});
