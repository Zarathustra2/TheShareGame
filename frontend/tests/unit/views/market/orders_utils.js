import { Number } from '@/service/utils';

export const mockItems = [
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:23',
    id: 10,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:23',
    id: 9,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:23',
    id: 8,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:23',
    id: 7,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:23',
    id: 6,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Sell',
    price: '1.50',
    amount: 10000,
    created: '10/02/2019 19:16',
    id: 5,
  },
  {
    order_of: {
      name: 'Cardiff Inc.',
      user_id: 3,
      isin: 'US000003',
    },
    typ: 'Buy',
    price: '0.97',
    amount: 10000,
    created: '10/02/2019 19:16',
    id: 4,
  },
  {
    order_of: {
      name: 'Big Company',
      user_id: 2,
      isin: 'US000002',
    },
    typ: 'Buy',
    price: '0.97',
    amount: 10000,
    created: '10/02/2019 19:16',
    id: 3,
  },
  {
    order_of: {
      name: 'Big Company',
      user_id: 2,
      isin: 'US000002',
    },
    typ: 'Buy',
    price: '0.98',
    amount: 10000,
    created: '10/02/2019 19:16',
    id: 2,
  },
  {
    order_of: {
      name: 'Big Company',
      user_id: 2,
      isin: 'US000002',
    },
    typ: 'Buy',
    price: '0.99',
    amount: 1000,
    created: '10/02/2019 19:15',
    id: 1,
  },
];


export const checkWrapper = (wrapper) => {
  expect(wrapper.findAll('tbody > tr').length).toBe(10);

  const $trs = wrapper.findAll('tbody > tr').wrappers;

  const N = Number;

  for (let i = 0; i < $trs.length; i++) {
    const tr = $trs[i];
    const item = mockItems[i];
    expect(tr.find('.value').text()).toMatch(N.numberWithDollar(item.price * item.amount));
    expect(tr.find('.company').text()).toMatch(item.order_of.name);
    expect(tr.find('.price').text()).toMatch(N.numberWithDollar(item.price));
    expect(tr.find('.amount').text()).toMatch(N.formatNumber(item.amount));
    expect(tr.find('.created').text()).toMatch(item.created);
  }
};
