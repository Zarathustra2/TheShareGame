import { createLocalVue, mount } from '@vue/test-utils';

import { NavbarPlugin } from 'bootstrap-vue';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import NavbarLoggedIn from '@/components/navbar/NavbarLoggedIn.vue';
import Service from '@/service/service';
import store from '@/store';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
localVue.use(NavbarPlugin);
const router = mockRouter.mock();

localVue.use(Vuex);


const isin = 'CH000001';

describe('NavbarLoggedIn', () => {
  let wrapper;
  beforeEach(() => {
    Service.saveCompany({ name: 'Smart Invest', isin, user_id: 1 });
    wrapper = mount(NavbarLoggedIn, { localVue, router, store });
  });

  it('renders the urls if the user hasCompany', () => {
    const html = wrapper.html();
    const companyUrl = wrapper.vm.$router.resolve({ name: 'company', params: { isin } }).href;
    const statementUrl = wrapper.vm.$router.resolve({ name: 'statementOfAccount', params: { isin } }).href;
    const depotUrl = wrapper.vm.$router.resolve({ name: 'depot', params: { isin } }).href;

    expect(html).toContain(companyUrl);
    expect(html).toContain(statementUrl);
    expect(html).toContain(depotUrl);
  });
});
