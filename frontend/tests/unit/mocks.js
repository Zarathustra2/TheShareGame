var sanitizeHtml = require('sanitize-html');

class LocalStorageMock {
  constructor() {
    this.store = {};
  }

  clear() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key];
  }

  setItem(key, value) {
    this.store[key] = value;
  }

  removeItem(key) {
    delete this.store[key];
  }
}

global.localStorage = new LocalStorageMock();

global.console = {
  log: jest.fn(), // console.log are ignored in tests

  error: console.error,
  warn: console.warn,
  info: console.info,
  debug: console.debug,
};


global.MutationObserver = class {
    constructor(callback) {}
    disconnect() {}
    observe(element, initObject) {}
};


// jsdom on which jest relies does not include support for innerText
// values during test.
//
// https://github.com/jsdom/jsdom/issues/1245
Object.defineProperty(global.Element.prototype, 'innerText', {
  get() {
    return sanitizeHtml(this.textContent, {
      allowedTags: [], // remove all tags and return text content only
      allowedAttributes: {}, // remove all tags and return text content only
    });
  },
  configurable: true, // make it so that it doesn't blow chunks on re-running tests with things like --watch
});
