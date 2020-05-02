import { createLocalVue, mount } from '@vue/test-utils';

import MessageReplyForm from '@/components/social/MessageReplyForm.vue';


const localVue = createLocalVue();


describe('MessageReplyForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(MessageReplyForm, { localVue });
  });

  it('submits the message', async () => {
    wrapper = mount(MessageReplyForm, {
      localVue,
      mocks: {
        $http: {
          post: () => Promise.resolve({ status: 201, data: {} }),
        },
      },
    });

    const data = { form: { text: 'Hey, whats up?' } };
    wrapper.setData(data);

    wrapper.find('#replySubmitButton').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.vm.form.text).toEqual('');
  });

  it('displays errors from request correctly', async () => {
    wrapper = mount(MessageReplyForm, {
      localVue,
      mocks: {
        $http: {
          post: () => Promise.reject({ response: { status: 400, data: { text: ['This field may not be blank'] } } }),
        },
      },
    });

    const data = { form: { text: '' } };
    wrapper.setData(data);

    wrapper.find('#replySubmitButton').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('This field may not be blank');
  });

  it('resetData', () => {
    const data = {
      form: { text: 'Testing takes a lot of time and effort!' },
      formFeedback: {
        isValid: false,
        errMessage: 'Something went wrong!',
        textValid: false,
        textErrMsg: 'Text may not contain any bad words!',
      },

    };

    wrapper.setData(data);

    wrapper.vm.resetData();

    expect(wrapper.vm.form.text).toEqual('');
    expect(wrapper.vm.formFeedback.isValid).toEqual(true);
    expect(wrapper.vm.formFeedback.errMessage).toEqual('');
    expect(wrapper.vm.formFeedback.textValid).toEqual(true);
    expect(wrapper.vm.formFeedback.textErrMsg).toEqual('');
  });
});
