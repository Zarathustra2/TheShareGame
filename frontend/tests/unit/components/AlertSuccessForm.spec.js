import { createLocalVue, mount } from '@vue/test-utils';

import AlertSuccessForm from '@/components/AlertSuccessForm.vue';

const localVue = createLocalVue();

describe('AlertSuccessForm', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(AlertSuccessForm, {
      localVue,
      propsData: {
        show: true,
        msg: 'Form Submitted!',
      },
    });
  });

  it('only shows when show is true', () => {
    wrapper = mount(AlertSuccessForm, {
      localVue,
      propsData: {
        show: false,
        msg: 'Form Submitted!',
      },
    });

    const html = wrapper.html();

    expect(html).not.toContain('Form Submitted!');
  });

  it('matches Snapshot', () => {
    expect(wrapper).toMatchSnapshot();
  });
});
