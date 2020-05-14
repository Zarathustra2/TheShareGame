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

const validName = 'Max';

const data = {
  form: {
    name: validName,
    country: 'IR',
    shares: 1000,
  },
};


const errData = {
  name: 'Not a real name!',
  country: 'not in choices',
  shares: 'too few',
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
          post: (_, payload) => {
            if (payload.name === validName) {
              return Promise.resolve({ data: postData });
            }
            return Promise.reject({
              response: {
                data: errData,
              },
            });
          },
        },
      },
    });

    localStorage.clear();
    data.form.name = validName;
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

  it('renders errors', async () => {
    data.form.name = 'invalid-name';

    wrapper.setData(data);
    await wrapper.vm.$nextTick();

    console.error = jest.fn();
    wrapper.find('.submit-btn').trigger('submit');
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    expect(console.error).toHaveBeenCalled();

    // eslint-disable-next-line
    for (const [_, value] of Object.entries(errData)) {
      expect(wrapper.html()).toContain(value);
    }
  });
});
