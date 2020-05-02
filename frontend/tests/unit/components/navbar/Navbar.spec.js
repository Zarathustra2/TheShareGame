import { createLocalVue, mount } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';

import Navbar from '@/components/navbar/Navbar.vue';
import NavbarLoggedIn from '@/components/navbar/NavbarLoggedIn.vue';
import NavbarNotLoggedIn from '@/components/navbar/NavbarNotLoggedIn.vue';
import store from '@/store';
import { NavbarPlugin } from 'bootstrap-vue';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
localVue.use(NavbarPlugin);
const router = mockRouter.mock();

localVue.use(Vuex);


describe('Navbar.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Navbar, { localVue, router, store });
  });

  it('renders the correct navbar when user is/is not authenticated', async () => {
    wrapper.setData({ loggedIn: true });
    await wrapper.vm.$nextTick();
    expect(wrapper.contains(NavbarLoggedIn)).toBe(true);

    wrapper.setData({ loggedIn: false });
    await wrapper.vm.$nextTick();
    expect(wrapper.contains(NavbarNotLoggedIn)).toBe(true);
  });
});
