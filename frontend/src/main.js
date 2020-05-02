import Vue from 'vue';

import {
  NavbarPlugin,
  ToastPlugin,
} from 'bootstrap-vue';


import Axios from 'axios/lib/axios';
import * as Sentry from '@sentry/browser/esm/index';
import { Vue as VueIntegration } from '@sentry/integrations/esm/index';
import VueAnalytics from 'vue-analytics';

import VueAuthenticate from 'vue-authenticate';

import Service from './service/service';
import App from './App.vue';
import router from './router';
import store from './store';

// eslint-disable-next-line
import(/* webpackPrefetch: true */ 'bootstrap/dist/css/bootstrap.css');
// eslint-disable-next-line
import(/* webpackPrefetch: true */ 'bootstrap-vue/dist/bootstrap-vue.css');

const DEBUG = window.webpackHotUpdate;


Vue.config.productionTip = false;
Vue.use(ToastPlugin);
Vue.use(NavbarPlugin);

Vue.prototype.$http = Axios;

// If we have a 401 error the user did not provide a valid token.
// Hence, we clear the local storage
// and direct him to the login page
Vue.prototype.$http.interceptors.response.use((response) => response, (error) => {
  if (error.response !== undefined && error.response.status === 401) {
    localStorage.clear();
    router.push('/login');
  }
  return Promise.reject(error);
});

const token = Service.getToken();
if (token) {
  Vue.prototype.$http.defaults.headers.common.Authorization = `Token ${token}`;
}

if (!DEBUG) {
  Sentry.init({
    dsn: process.env.VUE_APP_SENTRY_DSN,
    integrations: [new VueIntegration({ Vue, attachProps: true, logErrors: true })],
  });

  Vue.use(VueAnalytics, {
    id: process.env.VUE_APP_GOOGLE_ANALYTICS,
    router,
  });
} else {
  console.log('Development mode!');
}

Vue.use(VueAuthenticate, {
  baseUrl: process.env.VUE_APP_URL || 'http://localhost:8000/api', // Your API domain

  tokenType: 'Token',

  providers: {
    github: {
      clientId: process.env.VUE_APP_GITHUB_AUTH_ID,
      redirectUri: process.env.VUE_APP_REDIRECT_URI || 'http://localhost:8080/login',
      url: '/auth/github/',
      tokenPath: 'key',
    },
  },
});

export default new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');
