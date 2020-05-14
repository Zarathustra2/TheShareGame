import { mount, createLocalVue } from '@vue/test-utils';
import FondForum from '@/components/social/FondForum.vue';

const localVue = createLocalVue();

const data = {
  results: [
    {
      name: 'Simple Thread',
      user: { id: 1, username: 'A' },
      slug: 'simple-thread',
      created: '2019-12-27T15:19:32.697000Z',
      updated: '2019-12-27T18:19:32.697000Z',
      locked: false,
      pinned: false,
      id: 123,
    },
  ],
};

const resolveMock = jest.fn();
resolveMock.mockReturnValue('url');

const mocks = {
  $http: {
    get: () => Promise.resolve({ data }),
  },
  $route: {
    params: { id: 1 },
  },
  $router: {
    resolve: resolveMock,
  },
};

describe('FondForum', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(FondForum, {
      localVue,
      mocks,
      stubs: ['router-link'],
    });
  });

  it('renders data', () => {
    const { results } = data;
    for (let i = 0; i < results.length; i++) {
      const obj = results[i];
      expect(wrapper.html()).toContain(obj.name);
    }

    expect(resolveMock).toHaveBeenCalledWith({
      name: 'threadFond',
      params: {
        id: 1,
        slug: 'simple-thread',
        threadId: 123,
      },
    });
  });
});
