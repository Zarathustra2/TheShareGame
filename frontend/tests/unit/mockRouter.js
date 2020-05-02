import VueRouter from 'vue-router';
import routes from '@/routes';

export default {
  mock() {
    return new VueRouter({
      routes,
    });
  },
};
