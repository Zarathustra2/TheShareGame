import { createLocalVue, shallowMount } from '@vue/test-utils';
import VueRouter from 'vue-router';
import HighchartsVue from 'highcharts-vue';
import Company from '@/views/company/Company.vue';
import LinksSheets from '@/components/company/LinksSheets.vue';
import Datasheet from '@/components/company/Datasheet.vue';
// import Vuex from 'vuex';
// import store from '@/store';
import dataSheetRendersCorrectly from '../../components/company/Datasheet.spec';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
localVue.use(HighchartsVue);
// localVue.use(Vuex);
const router = mockRouter.mock();

const data = {
  company:
    {
      name: 'Vue Invest',
      user: {
        username: 'Joe Blocks',
      },
      isin: 'US000001',
      cash: 1000000,
      shares: 1000,
      key_figures: {
        book_value: 1000000,
        share_price: '2.00',
        activity: 57,
        bid: null,
        ask: {
          price: 9.2,
          total_amount: 5000,
        },
      },
    },
};

const methods = {
  // disable http call
  getData: () => {

  },
};

describe('Company', () => {
  it('renders data correctly', async () => {
    const wrapper = shallowMount(Company, {
      methods,
      localVue,
      router,
      // store,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data: [] }),
        },
      },
      stubs: {
        Datasheet, LinksSheets,
      },
    });

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    expect(wrapper.find('#company_name').text()).toMatch(data.company.name);
    expect(wrapper.find('#isin').text()).toMatch(data.company.isin);
    expect(wrapper.find('#ceo_username').text()).toMatch(data.company.user.username);

    dataSheetRendersCorrectly(wrapper, data.company);
  });
});
