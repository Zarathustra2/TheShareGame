import { createLocalVue, shallowMount } from '@vue/test-utils';

import Orderbook from '@/views/company/Orderbook.vue';

const localVue = createLocalVue();
const name = 'company';

describe('Orderbook.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(Orderbook, {
      localVue,
      mocks: {
        $http: {
          get: () => Promise.resolve({ data: { name } }),
        },
        $route: {
          params: {
            isin: 'IR000001',
          },
        },
      },
    });
  });

  it('gets Name if not present in props', () => {
    expect(wrapper.vm.name).toEqual(name);
  });

  it('name is present in props, no http will be made', () => {
    wrapper = shallowMount(Orderbook, {
      localVue,
      propsData: {
        companyName: 'other-company',
      },
      mocks: {
        $http: {
          get: () => Promise.resolve({ data: { name } }),
        },
        $route: {
          params: {
            isin: 'IR000001',
          },
        },
      },
    });

    expect(wrapper.vm.name).toEqual('other-company');
  });
});
