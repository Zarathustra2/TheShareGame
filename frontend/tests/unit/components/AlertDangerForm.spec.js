import { createLocalVue, mount } from '@vue/test-utils';

import AlertDangerForm from '@/components/AlertDangerForm.vue';

const localVue = createLocalVue();

describe('AlertDangerForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(AlertDangerForm, {
      localVue,
      propsData: {
        isValid: false,
        errMessage: 'Error 404!',
      },
    });
  });

  it('renders ErrMessage', () => {
    expect(wrapper.html()).toContain('Error 404!');

    wrapper = mount(AlertDangerForm, {
      localVue,
      propsData: {
        isValid: true,
        errMessage: 'Error 404!',
      },
    });

    expect(wrapper.html()).not.toContain('Error 404!');
  });

  it('matches Snapshot', () => {
    expect(wrapper).toMatchSnapshot();
  });
});
