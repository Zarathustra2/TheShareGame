import { shallowMount, createLocalVue, createWrapper } from '@vue/test-utils';
import Order from '@/views/market/Order.vue';
import {
  BFormGroup, BButton, BFormInput, BForm, BFormSelect, BFormInvalidFeedback, ToastPlugin,
} from 'bootstrap-vue';

const localVue = createLocalVue();
localVue.use(ToastPlugin);

const query = {
  price: 5,
  amount: 2321,
  typ: 'Sell',
};


const invalidIsin = 'GE001122';
const errData = {
  isin: 'I dont like your isin... Rejected!',
};

describe('Order', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(Order, {
      stubs: {
        BFormGroup,
        BButton,
        BFormInput,
        BForm,
        BFormSelect,
        BFormInvalidFeedback,
      },
      localVue,
      mocks: {
        $http: {
          post: (_, data) => {
            if (data.order_of_isin === invalidIsin) {
              return Promise.reject({
                response: {
                  data: errData,
                },
              });
            }
            return Promise.resolve({});
          },
        },
        $route: {
          params: {
            isin: 'SK002873',
          },
          query,
        },
      },
    });
  });

  it('sets the data of the query attributes if present', () => {
    expect(wrapper.vm.form.price).toEqual(query.price);
    expect(wrapper.vm.form.amount).toEqual(query.amount);
    expect(wrapper.vm.form.typ).toEqual(query.typ);
  });

  it('renders the errors if present', async () => {
    wrapper.setData({ form: { isin: invalidIsin } });
    await wrapper.vm.$nextTick();

    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.formFeedback.isValid).toBe(false);
    expect(wrapper.vm.formFeedback.isinValid).toBe(false);
    expect(wrapper.html()).toContain(errData.isin);
  });

  it('displays a toast on succesfull order creation', async () => {
    wrapper.find('.submit-btn').trigger('submit');

    const waitNT = (ctx) => new Promise((resolve) => ctx.$nextTick(resolve));
    const waitRAF = () => new Promise((resolve) => requestAnimationFrame(resolve));

    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();
    await waitNT(wrapper.vm);
    await waitRAF();

    let toast = document.querySelector('#order-notification');
    expect(toast).toBeDefined();
    toast = createWrapper(toast);
    expect(toast.html()).toContain(`Amount: ${wrapper.vm.form.amount}`);
  });
});
