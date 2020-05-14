import { mount, createLocalVue, createWrapper } from '@vue/test-utils';
import FondApplication from '@/views/social/FondApplication.vue';
import { ToastPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(ToastPlugin);

const data = {
  name: 'Black Mamba Fond',
  id: 1,
  slug: 'black-mamba-fond',
};

const badFondId = 42;
const errData = {
  text: 'text too short! Write more...',
};

const mocks = {
  $route: {
    params: { id: 1 },
  },
  $http: {
    get: () => Promise.resolve({ data }),
    post: (_, postData) => {
      if (postData.fond_id === badFondId) {
        return Promise.reject({
          response: {
            data: errData,
          },
        });
      }
      return Promise.resolve({});
    },
  },

  $store: {
    getters: {
      hasFond: false,
    },
  },
};

describe('FondApplication', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(FondApplication, {
      localVue,
      mocks,
    });
  });

  it('renders the form if the user does not have a fond', () => {
    expect(wrapper.html()).toContain('form');
  });

  it('does not render form if user has fond', () => {
    mocks.$store.getters.hasFond = true;
    wrapper = mount(FondApplication, {
      localVue,
      mocks,
    });
    expect(wrapper.html()).not.toContain('form');
    mocks.$store.getters.hasFond = false;
  });

  it('renders errors on submit', async () => {
    wrapper.setData({
      fond: { id: badFondId },
      form: { text: 'some-text' },
    });

    await wrapper.vm.$nextTick();

    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(errData.text);
  });

  it('displays a toast notification if successful', async () => {
    wrapper.setData({
      form: { text: 'some-text' },
      fond: { id: 1 },
    });

    await wrapper.vm.$nextTick();
    wrapper.find('.submit-btn').trigger('submit');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#application-notfication');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('has been submitted');
  });
});
