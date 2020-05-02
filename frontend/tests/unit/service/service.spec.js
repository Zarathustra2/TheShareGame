import axios from 'axios';
import Service from '@/service/service';


describe('service', () => {
  beforeEach(() => {
    localStorage.clear();
    axios.defaults.headers.common.Authorization = undefined;
  });

  it('getToken', () => {
    localStorage.setItem('token', '123456');
    const v = Service.getToken();
    expect(v).toBe('123456');
  });

  it('setToken & deleteToken', () => {
    Service.saveToken('12');
    expect(localStorage.getItem('token')).toBe('12');
    expect(Service.isAuthenticated()).toBe(true);

    Service.deleteToken();
    expect(localStorage.getItem('token')).toBe(null);
    expect(Service.isAuthenticated()).toBe(false);
  });

  it('checkAxiosToken', () => {
    Service.checkAxiosToken();
    expect(axios.defaults.headers.common.Authorization).toBe(undefined);

    localStorage.setItem('token', '12');

    expect(axios.defaults.headers.common.Authorization).toBe(undefined);
    Service.checkAxiosToken();
    expect(axios.defaults.headers.common.Authorization).toBe('Token 12');

    localStorage.setItem('token', '13');
    Service.checkAxiosToken();
    expect(axios.defaults.headers.common.Authorization).toBe('Token 13');

    Service.saveToken('14');
    expect(axios.defaults.headers.common.Authorization).toBe('Token 14');
  });
});
