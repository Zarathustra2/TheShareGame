
// TODO Move to Prototype, so we can call it as instance method
export const Number = {
  /**
   *
   * @param number
   * @returns {string} number as string formatted with , as a thousand separator.
   */
  formatNumber(number) {
    if (number === undefined || number == null) return number;
    const parts = number.toString().split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return parts.join('.');
  },

  /**
   *
   * @param number
   * @returns {string} Number formatted with a thousand separator and dollar sign.
   */
  numberWithDollar(number) {
    if (number === undefined || number == null) return number;
    return `${Number.formatNumber(number)}$`;
  },

  /**
   *
   * @param num
   * @returns {number}
   */
  formatedNumberToNumber(num) {
    if (num.endsWith('$')) {
      num = num.slice(0, num.length - 1);
    }

    const actualNumber = num.replace(/,/g, '');
    return parseFloat(actualNumber);
  },
};

export const Table = {
  /**
   * getTableData requests the data for a given server side rendering table.
   * Furthermore, it sets the corresponding fields of the component
   *
   * The table needs to have the following fields:
   *    isBusy, total, items
   */
  getTableData({
    url, component, page, size, formatter, ctx,
  }) {
    if (component.isBusy === undefined
      || component.total === undefined || component.items === undefined) {
      console.error('Component does not have one of the following fields: [isBusy, total, items]');
      return null;
    }

    component.isBusy = true;

    let promise;

    if (page !== null && size !== null) {
      promise = component.$http.get(url(page, size, ctx));
    } else {
      promise = component.$http.get(url());
    }

    promise.then((d) => {
      const { results } = d.data;

      component.total = d.data.count;
      component.isBusy = false;

      if (formatter !== undefined) for (let i = 0; i < results.length; i++) formatter(results[i]);

      component.items = results;
    }).catch((e) => {
      console.log(e);
      component.isBusy = false;
    });

    return promise;
  },

  getTableNameAndCompanyName(url, component, page, size, formatter, childComponent) {
    const promise = this.getTableData(url, component, page, size, formatter);

    promise.then((r) => {
      const name = r.data.company_name;
      if (name !== undefined) {
        childComponent.name = name;
      }
    });

    return promise;
  },
};

export const DateParse = {

  /**
   * Converts a string date to utc date timestamp
   * @param date
   * @returns {number}
   */
  parseToUTC(date) {
    const d = new Date(date.replace(/\.\w+[^Z]/, '').replace(/-/g, '/').replace(/[T|Z]/g, ' '));
    return Date.UTC(
      d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(),
      d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds(),
    );
  },
};
