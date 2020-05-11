import { mount, createLocalVue } from '@vue/test-utils';
import FoundFirstCompany from '@/views/FoundFirstCompany.vue';
import Service from '@/service/service';

const localVue = createLocalVue();

const postData = {
  isin: 'IR000007',
  name: 'Company',
  user: {
    id: 1,
    username: 'max',
  },
};

const data = {
  form: {
    name: 'Max',
    country: 'IR',
    shares: 1000,
  },
};


describe('FoundFirstCompany.vue', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(FoundFirstCompany, {
      localVue,
      attachToDocument: true,
      mocks: {
        $router: {
          push: jest.fn(),
        },
        $http: {
          post: () => Promise.resolve({ data: postData }),
        },
      },
    });

    localStorage.clear();
  });

  it('renders name, country and shares', async () => {
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.$refs.nameInput.value).toEqual(('Max'));
    expect(wrapper.vm.$refs.countryInput.value).toEqual(('IR'));
    expect(wrapper.vm.$refs.sharesInput.value).toEqual((1000));
  });

  it('saves company in localStorage after submit', async () => {
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();

    const c = Service.getCompany();

    // eslint-disable-next-line
    for (const [key, value] of Object.entries(c)) {
      expect(value).toEqual(c[key]);
    }
  });

  it('redirects to company after creation', async () => {
    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.$router.push).toHaveBeenCalledWith({
      name: 'company',
      params: {
        isin:
      postData.isin,
      },
    });
  });
});
