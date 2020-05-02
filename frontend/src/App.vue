<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <div class="wrapper flex-grow-1">
      <Navbar :key="$route.fullPath"/>
      <b-container fluid>
        <router-view ref="router-view"/>
      </b-container>
    </div>

    <footer class="footer">
      <hr>
      <div class="container pt-5 border-bottom">

        <div class="row">
          <div class="col-md-12">
            <div class="py-4 d-flex justify-content-center align-items-center">
              <router-link class="mr-4" :to="{name: 'imprint'}">
                Imprint
              </router-link>
              <router-link :to="{name: 'dataProtection'}">
                Data protection
              </router-link>

            </div>
          </div>
        </div>
      </div>
    </footer>

  </div>
</template>

<script>

import Service from '@/service/service';
import { BContainer } from 'bootstrap-vue';
import Navbar from './components/navbar/Navbar.vue';

export default {
  components: { Navbar, BContainer },
  data() {
    return {
      ws: null,
      authenticated: Service.isAuthenticated(),
      form: {
        msg: '',
      },
      messages: [],
      websocketUrl: process.env.VUE_APP_WEBSOCKET_URL || 'localhost:8412',
    };
  },

  created() {
    const maxMessage = this.amount || 10;

    let tokenStr = '';
    if (this.authenticated) {
      if (Service.getToken() !== '') {
        tokenStr = `?token=${Service.getToken()}`;
      }
    }

    let query = '';
    if (Service.getToken() !== '') {
      if (tokenStr !== '') {
        query = `${tokenStr}&amount=${maxMessage}`;
      } else {
        query = `?amount=${maxMessage}`;
      }
    }

    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';

    const url = `${wsScheme}://${this.websocketUrl}/ws${query}`;

    this.ws = new WebSocket(url);

    this.$store.commit('setWebsocket', this.ws);

    this.ws.addEventListener('message', (e) => {
      const message = JSON.parse(e.data);

      const type = typeof message;

      // eslint-disable-next-line
        if (!(type === 'function' || type === 'object' && !!message)) {
        console.error('msg is not an object: ', message);
        return;
      }

      switch (message.type) {
        case 0:
          this.$store.commit('newChatMsg', message.data);
          break;
        case 1:
          this.handleEvent(message);
          break;
        default:
          console.error('Type not recognized!', message);
      }
    });
  },
  methods: {
    handleEvent(message) {
      const { typ, msg } = message.data;

      let variant;
      switch (typ.toLowerCase()) {
        case 'bond':
          variant = 'success';
          break;
        default:
          variant = 'primary';
      }

      this.$bvToast.toast(msg, {
        title: typ,
        autoHideDelay: 5000,
        appendToast: false,
        variant,
      });
    },
  },
};
</script>

<style scoped>

</style>
