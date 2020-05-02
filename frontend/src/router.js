import Vue from 'vue';
import Router from 'vue-router';
import axios from 'axios';
import Service from './service/service';
import Api from './service/api';
import routes from './routes';
// import NProgress from 'nprogress';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});


router.beforeResolve(async (to, from, next) => {
  if (to.name) {
    // NProgress has been imported in the index.html
    // via unpkg.

    // eslint-disable-next-line
    NProgress.configure({ easing: 'ease', speed: 200, minimum: 0.5 });
    // eslint-disable-next-line
    NProgress.start();
  }

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (Service.isAuthenticated()) {
      // If a user does not have a company, he/she should first
      // found one to continue
      console.log('hasCompany: ', Service.hasCompany());

      // If the user wants to log out, let him
      if (to.name === 'logout') {
        next();
        return;
      }

      if (!Service.hasCompany() && to.name !== 'foundFirstCompany') {
        await axios.get(Api.activeCompany())
          .then((r) => {
            const company = r.data;
            Service.saveCompany(company);
            next();
          })
          .catch((e) => {
            console.log(e);
            console.log('User does not have a company, redirecting!');
            next('/found/first/company');
          });
      }

      next();
      return;
    }
    console.log('User not logged in!');
    next('/login');
  }

  // a public page which does not need authentication such as the newspaper, a company page and more
  next();
});


router.afterEach(() => {
  // Complete the animation of the route progress bar.
  // eslint-disable-next-line
  NProgress.done();
});

export default router;
