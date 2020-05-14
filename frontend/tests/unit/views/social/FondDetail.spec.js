import { shallowMount, createLocalVue } from '@vue/test-utils';
import FondDetail from '@/views/social/FondDetail.vue';
import { NavbarPlugin, BNav, BNavItem } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(NavbarPlugin);

const data = {
  name: 'Black Mamba Fond',
  id: 1,
  members: [
    {
      user: {
        id: 6,
        username: 'Kobe',
        companies_book_value: 1402985.72,
      },
      leader: true,
      id: 1,
    },
  ],
  profile: {
    description: 'The Mamba Mentality\n\n“The beauty in being blessed with talent is rising above doubters to create a beautiful moment.”',
    open_for_application: true,
    id: 1,
    logo: 'http://www.thesharegame.com/mediafiles/fond_logo/Black_Mamba_Fond.png',
  },
  created: '04/19/2020 12:20',
  founder: {
    id: 6,
    username: 'Kobe',
  },
};

const mocks = {
  $route: {
    params: {
      id: 1,
    },
  },
  $http: {
    get: () => Promise.resolve({ data }),
  },
  $store: {
    getters: {
      isFondLeader: true,
      hasFond: true,
      getFond: {
        fond: {
          id: 1,
        },
      },
    },
  },
};

describe('FondDetail', () => {
  let wrapper;

  const switchToForm = (wrap, tab) => {
    const elemes = wrap.find('.fonds-tabs').findAll('a');
    expect(elemes.length).toBe(5);

    const elem = elemes.at(tab);

    elem.trigger('click');
  };


  beforeEach(() => {
    wrapper = shallowMount(FondDetail, {
      localVue,
      mocks,
      stubs: { 'router-link': true, BNav, BNavItem },
    });
  });

  it('renders data', () => {
    expect(wrapper.html()).toContain(data.name);

    const { members } = data;
    for (let i = 0; i < members.length; i++) {
      const { user } = members[i];
      expect(wrapper.html()).toContain(user.username);
    }
  });

  it('switches tab to forum', async () => {
    expect(wrapper.html()).not.toContain('fondforum-stub');
    switchToForm(wrapper, 1);
    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain('fondforum-stub');
  });

  it('switches tab to edit', async () => {
    expect(wrapper.html()).not.toContain('fondprofileform-stub');
    switchToForm(wrapper, 2);
    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain('fondprofileform-stub');
  });

  it('switches tab to applications', async () => {
    expect(wrapper.html()).not.toContain('fondapplicationslist-stub');
    switchToForm(wrapper, 3);
    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain('fondapplicationslist-stub');
  });

  it('switches tab to leave', async () => {
    expect(wrapper.html()).not.toContain('fondleaveform-stub');
    switchToForm(wrapper, 4);
    await wrapper.vm.$nextTick();
    expect(wrapper.html()).toContain('fondleaveform-stub');
  });

  it('does not render nav-tabs if user is not in the fond', () => {
    mocks.$store.getters.hasFond = false;

    wrapper = shallowMount(FondDetail, {
      localVue,
      mocks,
      stubs: { 'router-link': true, BNav, BNavItem },
    });

    expect(wrapper.find('.fonds-tabs').exists()).toBe(false);

    mocks.$store.getters.hasFond = true;
  });
});
