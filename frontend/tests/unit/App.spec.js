import { createLocalVue, mount } from '@vue/test-utils';
import Vuex from 'vuex';
import App from '@/App.vue';
import store from '@/store';

import { NavbarPlugin } from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(NavbarPlugin);

describe('App', () => {
  it('works', () => {
    mount(App, {
      localVue,
      store,
      stubs: ['router-link', 'router-view'],
      mocks: {
        $route: {
          fullPath: '/',
        },
      },
    });
  });
});
