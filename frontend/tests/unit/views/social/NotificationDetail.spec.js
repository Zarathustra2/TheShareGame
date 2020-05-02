import { mount } from '@vue/test-utils';
import NotificationDetail from '@/views/social/NotificationDetail.vue';

const data = {
  subject: 'Bond Payed out', text: 'You received 100,000$', extra: {}, created: '10/07/2019 19:37',
};

describe('NotificationDetail', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = mount(NotificationDetail, {

      mocks: {
        $route: {
          params: {
            id: '1',
          },
        },
        $http: {
          get() {
            return Promise.resolve({ data });
          },
        },
      },
    });
  });

  it('renders data correctly', () => {
    expect(wrapper.find('#headline').text()).toMatch(data.subject);
    expect(wrapper.find('#text').text()).toMatch(data.text);
    expect(wrapper.find('#date').text()).toMatch(`Received: ${data.created}`);
  });
});
