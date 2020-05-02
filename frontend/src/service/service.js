import axios from 'axios';

const Service = {

  /**
   * Returns the authentication token for api calls of the user.
   * @returns {string, null}
   */
  getToken() {
    return localStorage.getItem('token');
  },

  /**
   * Saves an authentication token in the local storage.
   * @param token
   */
  saveToken(token) {
    localStorage.setItem('token', token);
    this.checkAxiosToken();
  },

  /**
   * Deletes an authentication token from the local storage.
   */
  deleteToken() {
    localStorage.removeItem('token');
  },

  /**
   * Returns if an user has a token saved in his local storage
   * @returns {boolean}
   */
  isAuthenticated() {
    const t = this.getToken();
    return t !== null && t !== '' && t !== undefined;
  },

  checkAxiosToken() {
    if (this.isAuthenticated()) {
      const token = `Token ${this.getToken()}`;
      if (this.isAuthenticated() && axios.defaults.headers.common.Authorization !== token) {
        axios.defaults.headers.common.Authorization = token;
      }
    }
  },

  saveCompany(company) {
    console.log('Saving company, ', company);
    localStorage.setItem('company', JSON.stringify(company));
  },

  getCompany() {
    const c = localStorage.getItem('company');
    if (c === null) return c;
    return JSON.parse(c);
  },

  hasCompany() {
    return this.getCompany() !== null;
  },

};

export default Service;
