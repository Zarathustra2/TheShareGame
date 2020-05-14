import { createLocalVue, createWrapper, shallowMount } from '@vue/test-utils';
import Bonds from '@/views/market/Bonds.vue';
import Service from '@/service/service';
import {
  BFormGroup, BButton, BFormInput, BForm, BFormSelect, BFormInvalidFeedback, ToastPlugin,
} from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(ToastPlugin);

const tooMuchValue = 100000000;
const errData = ["You don't have enough money!"];

const options = {
  localVue,
  stubs: {
    BFormGroup,
    BButton,
    BFormInput,
    BForm,
    BFormSelect,
    BFormInvalidFeedback,
  },
  mocks: {
    $http: {
      get() {
        return Promise.resolve({ data: {} });
      },
      post(_, data) {
        if (data.value === tooMuchValue) {
          return Promise.reject({
            response: {
              data: errData,
            },
          });
        }
        return Promise.resolve({});
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

    expect(wrapper.html()).toContain('You need an account to buy bonds!');
  });

  it('shows the form if the user is authenticated', () => {
    expect(wrapper.html()).not.toContain('You need an account to buy bonds!');
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

  it('renders and displays errors on submit', async () => {
    const data = {
      form: {
        value: tooMuchValue,
        amount: 1,
        runtime: 3,
      },
    };

    wrapper.setData(data);

    await wrapper.vm.$nextTick();

    wrapper.find('.buttonBond').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.html()).toContain(errData[0]);
  });

  it('displays a toast message on succesfull bond creation', async () => {
    const data = {
      form: {
        value: 100000,
        amount: 1,
        runtime: 3,
      },
    };

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    wrapper.find('.buttonBond').trigger('submit');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#bond-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('1 bond has been bought!');
  });

  it('displays a toast with the correct grammar if amount more than 1', async () => {
    const data = {
      form: {
        value: 100000,
        amount: 2,
        runtime: 3,
      },
    };

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    wrapper.find('.buttonBond').trigger('submit');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#bond-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain('2 bonds have been bought!');
  });
});
