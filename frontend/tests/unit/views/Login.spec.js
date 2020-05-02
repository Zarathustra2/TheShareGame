import { mount, createLocalVue } from '@vue/test-utils';
import Login from '@/views/Login.vue';

const localVue = createLocalVue();
const $router = {};

describe('Login.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Login, {
      data() {
        return {
          username: 'Max',
          password: 'securePassword',
        };
      },
      localVue,
      attachToDocument: true,
      mocks: {
        $http: {
          post: () => Promise.resolve({ data: { token: 'someToken' } }),
          get: () => Promise.resolve({ data: { isin: 'IR00001', name: 'Oil Invest' } }),
          defaults: { headers: { common: { Authorization: null } } },
        },
        $router,
      },
    });
  });

  it('renders username and password', () => {
    expect(wrapper.vm.$refs.usernameInput.value).toEqual(('Max'));
    expect(wrapper.vm.$refs.passwordInput.value).toEqual(('securePassword'));
  });

  it('redirects to company page if user has a company', async () => {
    const spy = jest.fn();
    wrapper.vm.$router.push = spy;
    wrapper.find('.buttonLogin').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    // Popup will be shown for 1500ms and then the user will be redirected
    await new Promise((r) => setTimeout(r, 2000));
    expect(spy).toHaveBeenCalledWith({ name: 'company', params: { isin: 'IR00001' } });
  });
});
