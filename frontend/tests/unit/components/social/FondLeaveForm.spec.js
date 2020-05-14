import { mount, createLocalVue } from '@vue/test-utils';
import FondLeaveForm from '@/components/social/FondLeaveForm.vue';

const localVue = createLocalVue();
const mocks = {
  $http: {
    delete: () => Promise.resolve({}),
  },
  $store: {
    commit: jest.fn(),
  },
  $router: {
    push: jest.fn(),
  },
};

describe('FondLeaveForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(FondLeaveForm, {
      localVue,
      mocks,
    });
  });

  it('deletes fond from store on leave', async () => {
    wrapper.find('.leave-btn').trigger('click');
    await wrapper.vm.$nextTick();

    expect(mocks.$store.commit).toHaveBeenCalledWith('setFond', null);
    expect(mocks.$router.push).toHaveBeenCalledWith({ name: 'fonds' });
  });

  it('logs error if something unexpected happens', async () => {
    console.error = jest.fn();
    mocks.$http.delete = () => Promise.reject({});

    wrapper = mount(FondLeaveForm, {
      localVue,
      mocks,
    });

    wrapper.find('.leave-btn').trigger('click');
    await wrapper.vm.$nextTick();
    expect(console.error).toHaveBeenCalled();

    console.error.mockClear();
  });
});
