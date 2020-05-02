import { DateParse, Number, Table } from '@/service/utils';

describe('utils', () => {
  it('formatsNumber', () => {
    const N = Number;

    expect(N.formatNumber(100)).toMatch('100');
    expect(N.formatNumber(1000)).toMatch('1,000');
    expect(N.formatNumber(10000)).toMatch('10,000');
    expect(N.formatNumber(100000)).toMatch('100,000');
    expect(N.formatNumber(1000000)).toMatch('1,000,000');
  });

  it('formatedNumberToNumber', () => {
    const N = Number;

    expect(N.formatedNumberToNumber('100')).toEqual(100);
    expect(N.formatedNumberToNumber('1,000$')).toEqual(1000);
    expect(N.formatedNumberToNumber('10,000')).toEqual(10000);
    expect(N.formatedNumberToNumber('100,000.56$')).toEqual(100000.56);
    expect(N.formatedNumberToNumber('1,000,000,000.01')).toEqual(1000000000.01);
  });

  it('formatsNumber with DollarSign', () => {
    const N = Number;

    expect(N.numberWithDollar(100)).toMatch('100$');
    expect(N.numberWithDollar(1000)).toMatch('1,000$');
    expect(N.numberWithDollar(10000)).toMatch('10,000$');
    expect(N.numberWithDollar(100000)).toMatch('100,000$');
    expect(N.numberWithDollar(1000000)).toMatch('1,000,000$');
  });

  it('getTableData logs an error if required fields not specified', () => {
    console.error = jest.fn();
    Table.getTableData({
      url: '', component: {}, page: 1, size: 10,
    });
    expect(console.error).toHaveBeenCalled();
  });

  it('getTableData sets the received data to the component', async () => {
    const data = { count: 2, results: [{ name: 'bar', number: 1 }, { name: 'foo', number: 2 }] };

    const formatter = (e) => {
      e.number = 42;
      return e;
    };

    const component = {
      $http: {
        get() {
          return Promise.resolve({ data });
        },
      },
      isBusy: false,
      total: 0,
      items: [],
    };

    await Table.getTableData({
      url: () => 'url/', component, page: 1, size: 2, formatter,
    });

    expect(component.total).toEqual(2);

    const formattedData = data.results.map(formatter);
    expect(component.items).toEqual(formattedData);
    expect(component.isBusy).toEqual(false);
  });

  it('parses dates correctly', () => {
    const data = [
      {
        str: '2019-12-27T15:19:32.697000Z', hours: 15, minutes: 19, seconds: 32, year: 2019, month: 12, day: 27,
      },
      {
        str: '2019-12-27T16:19:32.697000Z', hours: 16, minutes: 19, seconds: 32, year: 2019, month: 12, day: 27,
      },
      {
        str: '2019-12-27T16:20:32.697000Z', hours: 16, minutes: 20, seconds: 32, year: 2019, month: 12, day: 27,
      },
      {
        str: '2018-11-1T16:20:45.697000Z', hours: 16, minutes: 20, seconds: 45, year: 2018, month: 11, day: 1,
      },
    ];

    for (let i = 0; i < data.length; i++) {
      const d = data[i];
      const result = new Date(DateParse.parseToUTC(d.str));

      expect(result.getHours()).toEqual(d.hours);
      expect(result.getMinutes()).toEqual(d.minutes);
      expect(result.getSeconds()).toEqual(d.seconds);
      expect(result.getFullYear()).toEqual(d.year);

      // getMonth is zero indexed
      expect(result.getMonth() + 1).toEqual(d.month);
      expect(result.getDate()).toEqual(d.day);
    }
  });
});
