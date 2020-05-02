import { mount, createLocalVue } from '@vue/test-utils';
import Register from '@/views/Register.vue';
import VueRouter from 'vue-router';
import mockRouter from '../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();

const WIDGET_ID = 'widgetId';

function createMock() {
  return {
    render: jest.fn(function handler(ele, options) {
      // Save the callback

      // eslint-disable-next-line no-underscore-dangle
      this._verify = options.callback;

      // eslint-disable-next-line no-underscore-dangle
      this._expire = options['expired-callback'];
      return WIDGET_ID;
    }),
    execute: jest.fn(function handler() {
      // eslint-disable-next-line no-underscore-dangle
      this._verify();
    }),
    reset: jest.fn(),
  };
}


const postData = {
  username: 'maxMustermann',
  email: 'max@web.de',
  password: 'superSecret',
};

const data = {
  form: {
    ...postData,
    passwordConfirm: 'superSecret',
  },
  authenticated: false,
};

const options = {
  localVue,
  router,
  stubs: ['router-link'],
  mocks: {
    $http: {
      post: () => Promise.resolve({ data: { token: 'token' } }),
    },
  },
};

describe('Register.vue', () => {
  let wrapper;

  beforeEach(() => {
    window.grecaptcha = createMock();
    wrapper = mount(Register, options);
    wrapper.setData(data);
  });

  it('token is saved on successful login', async () => {
    const store = global.localStorage;
    wrapper.find('.buttonRegister').trigger('submit');
    await wrapper.vm.$nextTick();
    expect(store.getItem('token')).toEqual('token');
  });

  it('displays error message if the passwords do not match', async () => {
    wrapper.setData({ form: { passwordConfirm: 'doesNotMatch' } });

    expect(wrapper.text()).not.toContain('Passwords did not match!');

    wrapper.find('.buttonRegister').trigger('submit');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.formFeedback.passwordConfirmValid).toEqual(false);
    expect(wrapper.text()).toContain('Passwords did not match!');
  });

  it('does not allow already authenticated users to register again', async () => {
    const copyData = { ...data };
    copyData.authenticated = true;
    wrapper.setData(copyData);
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('You are already logged in');
  });
});
