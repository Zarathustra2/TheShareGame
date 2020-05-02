export default function getTableDataMock(mockItems) {
  return jest.fn(({
    // eslint-disable-next-line
    url, component, page, size, formatter, ctx,
  }) => {
    const clone = JSON.parse(JSON.stringify(mockItems));
    if (formatter !== undefined) for (let i = 0; i < clone.length; i++) formatter(clone[i]);
    component.items = clone;
    component.total = clone.length;
    component.isBusy = false;
  });
}
