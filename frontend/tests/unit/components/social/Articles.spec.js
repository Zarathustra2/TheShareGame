import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';

import Articles from '@/components/social/Articles.vue';
import Article from '@/components/social/Article.vue';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
const router = mockRouter.mock();
localVue.use(VueRouter);

const mockedData = {
  count: 1,
  next: null,
  previous: null,
  results: [
    {
      headline: 'The First Step',
      text: "Although the phrase is nonsense, it does have a long history. The phrase has been used for several centuries by typographers to show the most distinctive features of their fonts. It is used because the letters involved and the letter spacing in those combinations reveal, at their best, the weight, design, and other important features of the typeface.\n\n\nA 1994 issue of \"Before & After\" magazine traces \"Lorem ipsum ...\" to a jumbled Latin version of a passage from de Finibus Bonorum et Malorum, a treatise on the theory of ethics written by Cicero in 45 B.C. The passage \"Lorem ipsum ...\" is taken from text that reads, \"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit ...,\" which translates as, \"There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain...\"\n\n\nDuring the 1500s, a printer adapted Cicero's text to develop a page of type samples. Since then, the Latin-like text has been the printing industry's standard for fake, or dummy, text. Before electronic publishing, graphic designers had to mock up layouts by drawing in squiggled lines to indicate text. The advent of self-adhesive sheets preprinted with \"Lorem ipsum\" gave a more realistic way to indicate where text would go on a page.",
      created: '2019-12-26T12:45:37.302238Z',
      id: 1,
      author: {
        name: 'Dario2 Inc',
        user_id: 2,
        isin: 'US000003',
        id: 3,
      },
    },
  ],
};

const propsData = { url: () => ('/articles') };

describe('Articles', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Articles, {
      localVue,
      propsData,
      router,
      mocks: {
        $http: {
          get() {
            return Promise.resolve({ data: mockedData });
          },
        },
      },
    });
  });

  it('logs an error if the url is not specified', () => {
    console.error = jest.fn();

    mount(Articles, {
      localVue,
      router,
    });

    expect(console.error).toHaveBeenCalledWith('Url is undefined!');
  });

  it('does not log an error if the url is specified', () => {
    console.error = jest.fn();
    expect(console.error).toHaveBeenCalledTimes(0);
  });

  it('renders articles', () => {
    expect(wrapper.vm.articles.length).toBe(1);
    expect(wrapper.vm.total).toBe(1);
    expect(wrapper.html()).not.toContain('No Articles have been written yet!');
  });

  it('displays a message if there are no articles', () => {
    wrapper = mount(Articles, {
      localVue,
      propsData,
      router,
      mocks: {
        $http: {
          get() {
            const copy = JSON.parse(JSON.stringify(mockedData));
            copy.count = 0;
            copy.results = [];
            return Promise.resolve({ data: copy });
          },
        },
      },
    });

    expect(wrapper.vm.articles.length).toBe(0);
    expect(wrapper).not.toContain(Article);
    expect(wrapper.html()).toContain('No Articles have been written yet!');
  });
});
