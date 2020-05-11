import { mount, createLocalVue } from '@vue/test-utils';
import Login from '@/views/Login.vue';
import Service from '@/service/service';

const localVue = createLocalVue();
const $router = {};

const validName = 'max';
const githubToken = 'github-token';

const data = {
  username: validName,
  password: 'league_of_legends_is_cool',
};

const loginSubmit = async (wrapper) => {
  wrapper.find('.buttonLogin').trigger('submit');
  await wrapper.vm.$nextTick();

  // Popup will be shown for 1500ms and then the user will be redirected
  await new Promise((r) => setTimeout(r, 2000));
};

const mocks = {
  $http: {
    post: (_, payload) => {
      if (payload.username === validName) {
        return Promise.resolve({ data: { token: 'someToken' } });
      }
      return Promise.reject({
        response: {
          username: 'Username may have been wrong!',
          password: 'Password may have been wrong!',
        },
      });
    },
    get: () => Promise.resolve({ data: { isin: 'IR00001', name: 'Oil Invest' } }),
    defaults: { headers: { common: { Authorization: null } } },
  },
  $router,
  $auth: {
    authenticate: () => Promise.resolve({ data: { key: githubToken } }),
  },
};

describe('Login.vue', () => {
  let wrapper;
  beforeEach(() => {
    localStorage.clear();
    wrapper = mount(Login, {
      localVue,
      mocks,
    });

    data.username = validName;
  });

  it('renders username and password', async () => {
    wrapper.setData(data);
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.$refs.usernameInput.value).toEqual((data.username));
    expect(wrapper.vm.$refs.passwordInput.value).toEqual((data.password));
  });

  it('redirects to company page if user has a company', async () => {
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    const spy = jest.fn();
    wrapper.vm.$router.push = spy;

    await loginSubmit(wrapper);
    expect(spy).toHaveBeenCalledWith({ name: 'company', params: { isin: 'IR00001' } });
  });

  it('displays error if the login fails', async () => {
    data.username = 'invalid';
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    wrapper.find('.buttonLogin').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain('Username or password was wrong. Please try again!');
  });

  it('redirects to foundNewCompany if user does not have one', async () => {
    const clonedMocks = { ...mocks };
    clonedMocks.$http.get = () => Promise.reject();

    wrapper = mount(Login, {
      mocks: clonedMocks,
      localVue,
    });

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    const spy = jest.fn();
    wrapper.vm.$router.push = spy;

    await loginSubmit(wrapper);
    expect(spy).toHaveBeenCalledWith({ name: 'foundFirstCompany' });
  });

  it('allows to login with github', async () => {
    const spy = jest.fn();
    wrapper.vm.$router.push = spy;


    wrapper.find('.submit-github').trigger('click');
    await wrapper.vm.$nextTick();

    // Popup will be shown for 1500ms and then the user will be redirected
    await new Promise((r) => setTimeout(r, 2000));
    expect(Service.getToken()).toEqual(githubToken);
  });

  it('displays errors when github login fails', async () => {
    const clonedMocks = { ...mocks };
    clonedMocks.$auth.authenticate = () => Promise.reject();

    wrapper = mount(Login, {
      mocks: clonedMocks,
      localVue,
    });

    console.error = jest.fn();

    wrapper.find('.submit-github').trigger('click');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain('Something during the authentication with github failed.');
    expect(console.error).toHaveBeenCalled();
  });
});
