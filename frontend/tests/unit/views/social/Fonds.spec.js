import { mount, createLocalVue } from '@vue/test-utils';
import Fonds from '@/views/social/Fonds.vue';
import { NavbarPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(NavbarPlugin);

const data = {
  count: 1,
  next: null,
  previous: null,
  results: [
    {
      name: 'Black Mamba Fond',
      id: 1,
      amount_members: 1,
      slug: 'black-mamba-fond',
      created: '04/19/2020 12:20',
      profile: {
        description: 'The Mamba Mentality\n\n“The beauty in being blessed with talent is rising above doubters to create a beautiful moment.”',
        open_for_application: true,
        id: 1,
        logo: 'http://www.thesharegame.com/mediafiles/fond_logo/Black_Mamba_Fond.png',
      },
    },
  ],
};

const invalidName = 'invalid-fond';
const errData = {
  name: 'already taken. I am really sorry!',
};

const mocks = {
  $http: {
    get: () => Promise.resolve({ data }),
    post: (_, postData) => {
      if (postData.name === invalidName) {
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
    commit: jest.fn(),
    dispatch: jest.fn(),
  },
};

describe('Fonds', () => {
  let wrapper;

  const switchToForm = (wrap) => {
    const elemes = wrap.find('.fonds-tabs').findAll('a');
    expect(elemes.length).toBe(2);

    const elem = elemes.at(1);

    elem.trigger('click');
  };


  beforeEach(() => {
    wrapper = mount(Fonds, {
      mocks,
      localVue,
      stubs: ['router-link'],
    });
  });

  afterEach(() => {
    mocks.$store.getters.hasFond = false;
  });

  it('renders data', async () => {
    await wrapper.vm.$nextTick();
    const fond = data.results[0];
    expect(wrapper.html()).toContain(fond.name);
    expect(wrapper.html()).toContain(fond.amount_members);
  });

  it('adds apply field if user does not have a fond', async () => {
    await wrapper.vm.$nextTick();

    // The header as well as each row will have the apply
    // class, hence the total value is the total of all results + 1
    expect(wrapper.findAll('.apply').length).toBe(data.results.length + 1);
  });

  it('does not add apply field if user has fond', async () => {
    mocks.$store.getters.hasFond = false;
    wrapper = mount(Fonds, {
      mocks,
      localVue,
      stubs: ['router-link'],
    });

    await wrapper.vm.$nextTick();
    expect(wrapper.findAll('.apply').length).toBe(1);
  });

  it('changes to found new form tab if clicked', async () => {
    expect(wrapper.find('form').exists()).toBe(false);
    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    expect(wrapper.find('form').exists()).toBe(true);
  });

  it('does not let users found new fond if they have one already', async () => {
    mocks.$store.getters.hasFond = true;
    wrapper = mount(Fonds, {
      mocks,
      localVue,
      stubs: ['router-link'],
    });

    expect(wrapper.find('.fonds-tabs').exists()).toBe(false);
  });

  it('can create new fond', async () => {
    wrapper.setData({
      form: { name: 'cool-name' },
    });

    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    wrapper.find('button').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(mocks.$store.commit).toHaveBeenCalled();
    expect(mocks.$store.dispatch).toHaveBeenCalled();
  });

  it('renders errors on creation of new fond', async () => {
    wrapper.setData({
      form: { name: invalidName },
    });

    switchToForm(wrapper);
    await wrapper.vm.$nextTick();

    wrapper.find('button').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(errData.name);
  });
});
