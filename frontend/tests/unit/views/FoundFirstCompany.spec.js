import { shallowMount, createLocalVue } from '@vue/test-utils';
import FoundFirstCompany from '@/views/FoundFirstCompany.vue';

const localVue = createLocalVue();

describe('Login.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = shallowMount(FoundFirstCompany, { localVue, attachToDocument: true });
  });

  it('renders name, country and shares', async () => {
    const data = {
      form: {
        name: 'Max',
        country: 'IR',
        shares: 1000,
      },
    };
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.$refs.nameInput.value).toEqual(('Max'));
    expect(wrapper.vm.$refs.countryInput.value).toEqual(('IR'));
    expect(wrapper.vm.$refs.sharesInput.value).toEqual((1000));
  });
});
