import { createLocalVue, mount } from '@vue/test-utils';

import ArticleForm from '@/components/social/ArticleForm.vue';
import Service from '@/service/service';

const localVue = createLocalVue();

describe('ArticleForm', () => {
  let wrapper;
  beforeEach(() => {
    Service.saveCompany({
      name: 'Invest Inc.',
      isin: 'IR000001',
      user_id: 1,
      id: 1,
    });

    wrapper = mount(ArticleForm, {
      localVue,
      mocks: {
        $http: {
          post() {
            return Promise.resolve({ data: {} });
          },
        },
      },
    });
  });

  it('previews the article', async () => {
    wrapper.setData({ form: { text: '__markdown__ **moreMarkdown**' } });
    await wrapper.vm.$nextTick();
    const html = wrapper.find('#preview').html();

    expect(html).toContain('<strong>markdown</strong>');
    expect(html).toContain('<strong>moreMarkdown</strong>');
    expect(html).not.toContain('__markdown__');
    expect(html).not.toContain('**moreMarkdown**');
  });

  it('displays success message after submit', async () => {
    wrapper.setData({ form: { text: 'HelloWorld', headline: 'Hey' } });

    wrapper.find('#submitArticleButton').trigger('submit');

    await wrapper.vm.$nextTick();

    expect(wrapper.vm.showSuccess).toBe(true);
  });
});
