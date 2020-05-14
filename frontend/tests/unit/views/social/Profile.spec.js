import { mount, createLocalVue, createWrapper } from '@vue/test-utils';
import Profile from '@/views/social/Profile.vue';
import { NavbarPlugin, ToastPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(NavbarPlugin);
localVue.use(ToastPlugin);

const data = {
  company: {
    name: 'Some company',
  },
  user: {
    username: 'marie',
  },
  is_own_profile: true,
  age: 11,
  description: 'hello world!',
  company_logo: 'https://cdn.pixabay.com/photo/2017/01/08/21/37/flame-1964066_1280.png',

};

const badAge = 42;
const errData = {
  age: '42 is the solution, not your age u fool!',
};

describe('Profile', () => {
  let wrapper;

  const switchToForm = (wrap) => {
    const elemes = wrap.find('.profile-tabs').findAll('a');
    expect(elemes.length).toBe(2);

    const elem = elemes.at(1);

    elem.trigger('click');
  };

  beforeEach(() => {
    wrapper = mount(Profile, {
      localVue,
      stubs: ['router-link'],
      mocks: {
        $http: {
          get: () => Promise.resolve({ data }),
          put(_, postData) {
            if (postData.age === badAge) {
              return Promise.reject({
                response: {
                  data: errData,
                },
              });
            }
            return Promise.resolve({ data: postData });
          },
        },
        $route: {
          params: { id: 13 },
        },
      },
    });
  });

  it('renders the data', async () => {
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(data.company.name);
    expect(wrapper.html()).toContain(data.user.username);
  });

  it('switches to form if navbar clicked', async () => {
    const msg = 'Edit your profile and tell the world a little bit about yourself!';
    expect(wrapper.html()).not.toContain(msg);
    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(msg);
  });

  it('renders errors if post does not succeed', async () => {
    wrapper.setData({ form: { age: badAge } });
    await wrapper.vm.$nextTick();

    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    wrapper.find('.btn-submit').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(errData.age);
  });

  it('displays toast on success', async () => {
    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    wrapper.find('.btn-submit').trigger('submit');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#profile-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('Your profile has been updated!');
  });
});
