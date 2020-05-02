import { createLocalVue, mount } from '@vue/test-utils';

import CompanyArticles from '@/views/company/CompanyArticles.vue';
import Api from '@/service/api';

const localVue = createLocalVue();

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

const companyUrl = Api.company('NI000001');
const companyName = 'Nigeria Invest';
const options = {
  stubs: ['router-link'],
  localVue,
  mocks: {
    $http: {
      get(url) {
        if (url === companyUrl) {
          return Promise.resolve({ data: { name: companyName } });
        }
        return Promise.resolve({ data: mockedData });
      },
    },
    $route: {
      params: { isin: 'NI000001' },
    },
  },
};

describe('CompanyArticles', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(CompanyArticles, options);
  });

  it('fetches the company name if not in props data', () => {
    expect(wrapper.vm.name).toEqual(companyName);
  });

  it('renders articles', () => {
    expect(wrapper.html()).not.toContain('No Articles have been written yet!');
  });
});
