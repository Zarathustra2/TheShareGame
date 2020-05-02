import { mount, createLocalVue } from '@vue/test-utils';
import VueRouter from 'vue-router';
import Logout from '@/views/Logout.vue';
import Service from '@/service/service';
import mockRouter from '../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);

const router = mockRouter.mock();

describe('Logout.vue', () => {
  it('token & vuex data gets deleted from local storage', () => {
    const wrapper = mount(Logout, { localVue, router });

    const c = {
      name: 'Better Invest',
      isin: 'GE000002',
    };

    Service.saveCompany(c);

    const { localStorage } = global;

    localStorage.setItem('token', 'auth-token');
    expect(localStorage.getItem('token')).toEqual('auth-token');

    wrapper.find('.buttonLogout').trigger('click');
    expect(localStorage.getItem('token')).toEqual(null);

    expect(Object.entries(localStorage)).toEqual([]);
  });
});
