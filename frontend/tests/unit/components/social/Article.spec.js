import { createLocalVue, mount } from '@vue/test-utils';
import VueRouter from 'vue-router';

import Article from '@/components/social/Article.vue';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
const router = mockRouter.mock();
localVue.use(VueRouter);

const propsData = {
  headline: 'TheShareGame has started',
  text: 'TheShareGame has officially been launched\n. Now it is time to see hwo many users it can attract!',
  author: { name: 'Akali', isin: 'CA000001' },
  dateTime: '2019-10-17T20:43:16.188236Z',
};

describe('Article', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(Article, {
      localVue,
      propsData,
      router,
    });
  });

  it('renders data correctly', () => {
    const authorName = wrapper.find('.author').text();
    const text = wrapper.find('.text').text();
    const dateTime = wrapper.find('.dateTime').text();

    expect(authorName).toEqual(propsData.author.name);
    expect(text).toEqual(propsData.text);
    expect(dateTime).toEqual(propsData.dateTime);
  });

  it('renders markdown', () => {
    propsData.text = '__markdown__';

    wrapper = mount(Article, {
      localVue,
      propsData,
      router,
    });

    const html = wrapper.html();
    expect(html).not.toContain(propsData.text);
    expect(html).toContain('<strong>markdown</strong>');
  });
});
