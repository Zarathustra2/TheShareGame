import { createLocalVue, mount } from '@vue/test-utils';
import HighchartsVue from 'highcharts-vue';
import Bonds from '@/views/market/Bonds.vue';
import Service from '@/service/service';

const localVue = createLocalVue();
localVue.use(HighchartsVue);

const mockRateData = [
  {
    rate: 2.5,
    created: '2019-12-27T15:19:32.697000Z',
    id: 1,
  },
  {
    rate: 3.0,
    created: '2019-12-27T16:19:38.226000Z',
    id: 2,
  },
  {
    rate: 2.7,
    created: '2019-12-27T17:19:53.984000Z',
    id: 3,
  },
];

describe('Bonds', () => {
  let wrapper;

  beforeEach(() => {
    jest.spyOn(Service, 'isAuthenticated').mockImplementation(() => true);

    const c = {
      name: 'Better Invest',
      isin: 'GE000002',
    };

    Service.saveCompany(c);

    wrapper = mount(Bonds, {
      localVue,
      attachToDocument: true,
      mocks: {
        $http: {
          get(url) {
            if (url.includes('rates')) return Promise.resolve({ data: mockRateData });
            return Promise.resolve({ data: {} });
          },
          post() {
            return Promise.resolve({ data: {} });
          },
        },
      },
    });
  });

  it('disables the form if the user is not authenticated', () => {
    jest.spyOn(Service, 'isAuthenticated').mockImplementation(() => false);
    wrapper = mount(Bonds, {
      localVue,
      mocks: {
        $http: {
          get(url) {
            if (url.includes('rates')) return Promise.resolve({ data: mockRateData });
            return Promise.resolve({ data: {} });
          },
        },
      },
    });

    expect(wrapper.html()).toContain('  You need an account to buy bonds!');
  });

  it('shows the form if the user is authenticated', () => {
    expect(wrapper.html()).not.toContain('  You need an account to buy bonds!');
  });

  it('sets and displays the data correctly', async () => {
    const data = {
      form: {
        value: 123456,
        amount: 6,
        runtime: 2,
      },
    };
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.$refs.valueInput.value).toEqual(data.form.value);
    expect(wrapper.vm.$refs.amountInput.value).toEqual(data.form.amount);
    expect(wrapper.vm.$refs.runtimeInput.value).toEqual(data.form.runtime);
  });
});
