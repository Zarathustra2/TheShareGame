import { createLocalVue, mount } from '@vue/test-utils';

import ThreadDetail from '@/views/social/ThreadDetail.vue';

const localVue = createLocalVue();

const mockPosts = {
  count: 2,
  next: null,
  previous: null,
  results: [

    {
      user: {
        id: 2,
        username: 'Melvin',
      },
      text: "Sure. \n\n What's the matter?",
      created: '11/04/2019 20:30',
      id: 2,
    },
    {
      user: {
        id: 1,
        username: 'dario',
      },
      text: 'Hey can anyone help me?',
      created: '11/04/2019 20:29',
      id: 1,
    },
  ],
};

describe('ThreadDetail', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(ThreadDetail, {
      localVue,
      mocks: {
        $http: {
          get() {
            return Promise.resolve({ data: mockPosts });
          },
        },
        $route: {
          params: {
            id: 1,
            slug: 'slug',
          },
        },
      },
    });
  });

  it('renders data', async () => {
    await wrapper.vm.$nextTick();
    expect(wrapper.findAll('.post').length).toBe(2);

    const $trs = wrapper.findAll('.posts').wrappers;

    // The items should be the other way around since it makes it easier to read for the user.
    const reversedMockItems = JSON.parse(JSON.stringify(mockPosts.results)).reverse();

    for (let i = 0; i < $trs.length; i++) {
      const tr = $trs[i];
      const item = reversedMockItems[i];

      expect(tr.find('.author').text()).toMatch(item.user.username);
      expect(tr.find('.text').html()).toContain(item.text);
      expect(tr.find('.dateTime').html()).toContain(item.created);
    }
  });
});
