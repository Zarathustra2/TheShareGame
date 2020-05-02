import { createLocalVue, shallowMount } from '@vue/test-utils';

import Depot from '@/views/company/Depot.vue';

const localVue = createLocalVue();
const name = 'company';

describe('Depot.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(Depot, {
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
    wrapper = shallowMount(Depot, {
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
