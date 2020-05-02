import { shallowMount, createLocalVue } from '@vue/test-utils';
import { TooltipPlugin } from 'bootstrap-vue';
import Datasheet from '@/components/company/Datasheet.vue';
import { Number } from '@/service/utils';
import VueRouter from 'vue-router';
import mockRouter from '../../mockRouter';

const localVue = createLocalVue();
localVue.use(TooltipPlugin);
localVue.use(VueRouter);
const router = mockRouter.mock();

const propsData = {
  cash: 1000000,
  shares: 1000,
  isin: 'IR000001',
  key_figures: {
    book_value: 1000000,
    share_price: '2.00',
    activity: 57,
    bid: null,
    ask: {
      price: 9.2,
      total_amount: 5000,
    },
  },
};

const round = (num) => Math.round(num * 100) / 100;

/**
 * Exporting the function since we also test the same in Company.spec.js
 * @param wrapper
 * @param data
 */
export default function dataSheetRendersCorrectly(wrapper, data) {
  let bvShare = data.key_figures.book_value / data.shares;
  bvShare = Number.numberWithDollar(bvShare);

  let marketCap = data.key_figures.share_price * data.shares;
  marketCap = Number.numberWithDollar(marketCap);

  const sharePrice = Number.numberWithDollar(round(data.key_figures.share_price));

  expect(wrapper.find('#share_price').text()).toMatch(sharePrice);
  expect(wrapper.find('#bv-s').text()).toMatch(bvShare);
  expect(wrapper.find('#bv').text()).toMatch(Number.numberWithDollar(data.key_figures.book_value));
  expect(wrapper.find('#activity').text()).toMatch(`${data.key_figures.activity}%`);
  expect(wrapper.find('#market_cap').text()).toMatch(marketCap);
  expect(wrapper.find('#quant_shares').text()).toMatch(Number.formatNumber(data.shares));
}


describe('Datasheet', () => {
  it('renders key figures correctly', () => {
    const wrapper = shallowMount(Datasheet, { propsData, router, localVue });

    dataSheetRendersCorrectly(wrapper, propsData);
  });
});
