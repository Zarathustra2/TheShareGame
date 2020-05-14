import { createLocalVue, shallowMount } from '@vue/test-utils';
import Company from '@/views/company/Company.vue';
import LinksSheets from '@/components/company/LinksSheets.vue';
import Datasheet from '@/components/company/Datasheet.vue';
import ShareholdersPieChart from '@/components/company/charts/ShareholdersPieChart.vue';
import DepotPieChart from '@/components/company/charts/DepotPieChart.vue';
import VueRouter from 'vue-router';
import dataSheetRendersCorrectly from '../../components/company/Datasheet.spec';

let localVue = createLocalVue();

const data = {
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
};

describe('Company', () => {
  let wrapper;
  beforeEach(() => {
    localVue = createLocalVue();
    wrapper = shallowMount(Company, {
      localVue,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data }),
        },
        $route: {
          params: { isin: 'JP002314' },
        },
      },
      stubs: {
        Datasheet, LinksSheets, 'router-link': true,
      },
    });
  });

  it('renders data correctly', async () => {
    await wrapper.vm.$nextTick();

    expect(wrapper.find('#company_name').text()).toMatch(data.name);
    expect(wrapper.find('#isin').text()).toMatch(data.isin);
    expect(wrapper.find('#ceo_username').text()).toMatch(data.user.username);

    dataSheetRendersCorrectly(wrapper, data);
  });

  it('redirects to notFound if api call does not succeed', async () => {
    wrapper = shallowMount(Company, {
      localVue,
      mocks: {
        $http: {
          get: () => Promise.reject(),
        },
        $route: {
          params: { isin: 'JP002314' },
        },
        $router: {
          push: jest.fn(),
        },
      },
      stubs: {
        Datasheet, LinksSheets, 'router-link': true,
      },
    });


    await wrapper.vm.$nextTick();
    expect(wrapper.vm.$router.push).toHaveBeenCalled();
    expect(wrapper.vm.$router.push).toHaveBeenCalledWith('notFound');
  });


  it('Updates the data if route changes', async () => {
    const otherCompany = JSON.parse(JSON.stringify(data));
    otherCompany.name = 'Why-not-react?';
    otherCompany.user.username = 'reactPower';
    otherCompany.isin = 'RU004421';

    const router = new VueRouter({ routes: [{ path: '/company/:isin/', name: 'company' }] });
    localVue.use(VueRouter);

    router.push({ name: 'company', params: { isin: 'JP002233' } });

    wrapper = shallowMount(Company, {
      localVue,
      router,
      mocks: {
        $http: {
          get: (url) => {
            if (url.includes(otherCompany.isin)) {
              return Promise.resolve({ data: otherCompany });
            }
            return Promise.resolve({ data });
          },
        },
      },
      stubs: {
        Datasheet, LinksSheets,
      },
    });

    expect(wrapper.vm.$route).toBeInstanceOf(Object);

    router.push({ name: 'company', params: { isin: otherCompany.isin } });

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(otherCompany.name);
    expect(wrapper.html()).toContain(otherCompany.isin);
    expect(wrapper.html()).toContain(otherCompany.user.username);
  });


  it('receives the depot and shareholders data from its child components', async () => {
    const shareholders = [
      {
        depot_of: {
          name: 'Centralbank',
          user_id: null,
          isin: 'US000001',
          id: 1,
        },
        amount: 13122,
        price_bought: 0.0,
        created: '04/16/2020 17:19',
        private_depot: false,
        id: 1,
      },
      {
        depot_of: {
          name: 'Black Mamba Inc',
          user_id: 6,
          isin: 'GE000004',
          id: 4,
        },
        amount: 5058,
        price_bought: 0.0,
        created: '04/17/2020 16:38',
        private_depot: false,
        id: 4,
      }];

    const depot = [{ name: 'Black Mamba Inc', value: 950.0 }, { name: 'Sebwolf AG', value: 1837.11 }];

    const router = new VueRouter({ routes: [{ path: '/company/:isin/', name: 'company' }] });
    localVue.use(VueRouter);

    router.push({ name: 'company', params: { isin: 'JP002233' } });

    wrapper = shallowMount(Company, {
      localVue,
      router,
      mocks: {
        $http: {
          get: (url) => {
            if (url.includes('shareholders')) {
              return Promise.resolve({ data: shareholders });
            }

            if (url.includes('depot')) {
              return Promise.resolve({ data: depot });
            }

            return Promise.resolve({ data });
          },
        },
      },
      stubs: {
        Datasheet, LinksSheets, ShareholdersPieChart, DepotPieChart,
      },
    });

    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(`Depot - ${depot.length}`);
    expect(wrapper.html()).toContain(`Shareholders - ${shareholders.length}`);
  });
});
