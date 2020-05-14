import { mount, createLocalVue, createWrapper } from '@vue/test-utils';
import FondApplicationsList from '@/components/social/FondApplicationsList.vue';
import { ToastPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(ToastPlugin);

const data = {
  count: 1,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      user: { id: 3, username: 'ABC' },
      text: 'invite me',
      created: '05/14/2020 19:03',
    },
    {
      id: 2,
      user: { id: 1, username: 'user_number_two' },
      text: 'invite me, user 1 is not as good as me!',
      created: '05/20/2020 19:03',
    },

  ],
};

const mocks = {
  $route: {
    params: { id: 1 },
  },
  $http: {
    get: () => Promise.resolve({ data }),
    delete: () => Promise.resolve({}),
  },
};

describe('FondApplicationsList', () => {
  let wrapper;

  const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
  const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

  beforeEach(() => {
    wrapper = mount(FondApplicationsList, {
      localVue,
      mocks,
      stubs: ['router-link'],
    });
  });

  it('renders the data', () => {
    const { results } = data;
    for (let i = 0; i < results.length; i++) {
      const appl = results[i];
      expect(wrapper.html()).toContain(appl.user.username);
      expect(wrapper.html()).toContain(appl.text);
    }
  });

  it('can accept applications', async () => {
    wrapper.find('.btn-success').trigger('click');
    await wrapper.vm.$nextTick();

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#appl-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('Accepted');
  });

  it('can decline applications', async () => {
    wrapper.find('.btn-warning').trigger('click');
    await wrapper.vm.$nextTick();

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#appl-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('Declined');
  });
});
