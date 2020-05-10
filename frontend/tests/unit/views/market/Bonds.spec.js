import { createLocalVue, shallowMount } from '@vue/test-utils';
import Bonds from '@/views/market/Bonds.vue';
import Service from '@/service/service';

const localVue = createLocalVue();

const options = {
  localVue,
  mocks: {
    $http: {
      get() {
        return Promise.resolve({ data: {} });
      },
      post() {
        return Promise.resolve({ data: {} });
      },
    },
  },
};

describe('Bonds', () => {
  let wrapper;

  beforeEach(() => {
    jest.spyOn(Service, 'isAuthenticated').mockImplementation(() => true);

    const c = {
      name: 'Better Invest',
      isin: 'GE000002',
    };

    Service.saveCompany(c);

    wrapper = shallowMount(Bonds, options);
  });

  it('disables the form if the user is not authenticated', () => {
    jest.spyOn(Service, 'isAuthenticated').mockImplementation(() => false);
    wrapper = shallowMount(Bonds, options);

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
