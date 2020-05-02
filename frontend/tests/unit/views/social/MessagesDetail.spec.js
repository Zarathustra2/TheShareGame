import { createLocalVue, mount } from '@vue/test-utils';
import MessageDetail from '@/views/social/MessageDetail.vue';
import Service from '@/service/service';
import VueRouter from 'vue-router';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
localVue.use(VueRouter);
const router = mockRouter.mock();

const data = {
  conversation: {
    created: '10/08/2019 16:38',
    id: 1,
    subject: 'Hey',
    unread_by: [],
    users: [
      { id: 1, username: 'marie' },
      { id: 2, username: 'max' },
    ],
  },
  results: [
    {
      sender: { username: 'max', id: 2 }, text: 'Hey, how are you doing?', created: '10/08/2019 16:38', id: 1,
    },
    {
      sender: { username: 'marie', id: 1 }, text: 'Fine and you?', created: '10/08/2019 16:40', id: 2,
    },
    {
      sender: { username: 'max', id: 2 }, text: 'Good. Do you want to go on a date with me?', created: '10/08/2019 16:45', id: 3,
    },
    {
      sender: { username: 'marie', id: 1 }, text: 'Sure. I would love too!', created: '10/08/2019 16:47', id: 4,
    },
  ],
};


describe('MessagesDetail', () => {
  let wrapper;
  Service.saveCompany({
    name: 'Invest Inc.',
    isin: 'IR000001',
    user_id: 1,
  });
  beforeEach(() => {
    wrapper = mount(MessageDetail, {
      localVue,
      router,
      mocks: {
        $http: {
          get() {
            return Promise.resolve({ data });
          },
        },
      },
    });
  });

  it('renders data correctly', () => {
    expect(wrapper.find('#headline').text()).toMatch(data.conversation.subject);

    const $msgs = wrapper.findAll('.msg').wrappers;

    for (let i = 0; i < $msgs.length; i++) {
      const m = $msgs[i];
      const d = data.results[i];
      expect(m.text()).toContain(d.text);
      expect(m.text()).toContain(d.sender.username);
    }
  });
});
