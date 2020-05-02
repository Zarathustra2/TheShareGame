import { createLocalVue, mount } from '@vue/test-utils';

import VueRouter from 'vue-router';
import Newspaper from '@/views/social/Newspaper.vue';
import ArticleForm from '@/components/social/ArticleForm.vue';
import Service from '@/service/service';
import { NavbarPlugin } from 'bootstrap-vue';
import mockRouter from '../../mockRouter';


const router = mockRouter.mock();
const localVue = createLocalVue();
localVue.use(VueRouter);
localVue.use(NavbarPlugin);


const mockData = {

  count: 3,
  results: [
    {
      headline: 'Human',
      text: 'i am a human.',
      created: '2019-10-17T20:43:16.188236Z',
      id: 10,
      author: {
        name: 'Django Inc.',
        user_id: 1,
        isin: 'GE000001',
        id: 1,
      },
    },
    {
      headline: 'Lorem',
      text: 'Invest in my company. I am known for knowing where to invest. So my share price can only rise to the top.',
      created: '2019-10-17T13:14:54.974151Z',
      id: 9,
      author: {
        name: 'Django Inc.',
        user_id: 1,
        isin: 'GE000001',
        id: 1,
      },
    },
    {
      headline: 'Lorem',
      text: 'Hello my name is frank the tank. i like to play league of legends and also like to play overwatch. My invest in shares and lost all of money investing in bitcoins because I am a piece of shit',
      created: '2019-10-17T13:14:53.713616Z',
      id: 8,
      author: {
        name: 'Django Inc.',
        user_id: 1,
        isin: 'GE000001',
        id: 1,
      },
    },
  ],

};

describe('Newspaper', () => {
  let wrapper;
  beforeEach(() => {
    Service.saveToken('token');
    wrapper = mount(Newspaper, {
      localVue,
      router,
      mocks: {
        $http: {
          get() {
            return Promise.resolve({ data: mockData });
          },
        },
      },
    });
  });

  it('does not render ArticleForm if not authenticated', async () => {
    Service.deleteToken();
    // Rerender since logged in variable is initialised on render
    wrapper = mount(Newspaper, {
      localVue,
      router,
      mocks: {
        $http: {
          get() {
            return Promise.resolve({ data: mockData });
          },
        },
      },
    });

    wrapper.setData({ activeTab: 'newArticle' });
    await wrapper.vm.$nextTick();

    expect(wrapper.contains(ArticleForm)).toBe(false);
  });

  it('renders ArticleForm if authenticated', async () => {
    wrapper.setData({ activeTab: 'newArticle' });
    await wrapper.vm.$nextTick();
    expect(wrapper.contains(ArticleForm)).toBe(true);
  });

  it('renders all articles', () => {
    const { results } = mockData;

    const html = wrapper.html();

    results.forEach((r) => {
      expect(html).toContain(r.text);
    });
  });
});
