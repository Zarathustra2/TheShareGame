describe('LocalStorage Mock', () => {
  it('set & get', () => {
    const store = global.localStorage;
    store.setItem('name', 'max');
    expect(store.getItem('name')).toEqual('max');
  });

  it(' remove & clear', () => {
    const store = global.localStorage;
    store.setItem('name', 'max');
    store.setItem('last name', 'blocks');
    store.setItem('company-name', 'Max Inc.');

    store.removeItem('name');
    expect(store.getItem('name')).toEqual(null);
    expect(store.getItem('last name')).toEqual('blocks');
    expect(store.getItem('company-name')).toEqual('Max Inc.');

    store.clear();
    expect(store.getItem('last name')).toEqual(null);
    expect(store.getItem('company-name')).toEqual(null);
  });
});
