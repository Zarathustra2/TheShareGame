<template>
  <div>
    <Headline name="Login"/>
    <div v-if="authenticated">You are already logged in</div>
    <div v-else>
      If you do not have an account, click here to sign up!
      <b-row class="justify-content-md-center">

        <b-form inline @submit.prevent="login">

          <label class="sr-only">Username</label>
          <b-form-input class="mb-2 mr-sm-2 mb-sm-0" :state="isValid"
                   placeholder="Username" v-model="username" ref="usernameInput"/>

          <label class="sr-only">Password</label>
          <b-form-input class="mb-2 mr-sm-2 mb-sm-0" :state="isValid"
                   placeholder="password" type="password" v-model="password" ref="passwordInput"/>

          <b-button variant="primary" type="submit" class="buttonLogin">Submit</b-button>
        </b-form>

      </b-row>

      <b-row class="justify-content-md-center">
        <b-alert show variant="danger"
                 v-if="isValid !== null && !isValid">{{ errMessage }}
        </b-alert>
      </b-row>
    </div>
    <hr>
    <b-row class="justify-content-md-center">
      <b-button variant="success" v-on:click="githubLogin">Login/Register with Github</b-button>
    </b-row>

    <b-modal id="bv-modal-success" centered hide-footer>
      <template v-slot:modal-title>
        <span class="text-success">Success!</span>
      </template>
      <div class="d-block text-center">
        <h3>You have successfully authenticated yourself! You'll be redirected shortly</h3>
      </div>
    </b-modal>
  </div>
</template>

<script>
import Api from '@/service/api';
import Service from '@/service/service';
import Headline from '@/components/Headline.vue';
import {
  BRow, BButton, BForm, BModal, BFormInput, ModalPlugin,
} from 'bootstrap-vue';

import Vue from 'vue';

Vue.use(ModalPlugin);

export default {
  name: 'Login',
  components: {
    Headline, BRow, BButton, BForm, BModal, BFormInput,
  },
  data() {
    return {
      username: '',
      password: '',
      badRequest: false,
      isValid: null,
      errMessage: '',
      authenticated: Service.isAuthenticated(),
    };
  },
  methods: {
    login() {
      const { username } = this;
      const { password } = this;

      const data = { username, password };
      this.isValid = null;
      this.errMessage = '';

      this.$http.post(Api.login(), data)
        .then((r) => {
          const { token } = r.data;

          Service.saveToken(token);
          console.log('Token has been saved!');

          this.$bvModal.show('bv-modal-success');
          setTimeout(() => {
            this.$bvModal.hide('bv-modal-success');
            this.forward(token);
          }, 1300);
        })
        .catch((e) => {
          console.log(e);
          this.errMessage = 'An unexpected error occurred!';
          this.isValid = false;

          if (e.response.status === 400) {
            this.errMessage = 'Username or password was wrong. Please try again!';
          }
        });
    },

    forward(token) {
      Service.checkAxiosToken();
      this.$http.defaults.headers.common.Authorization = `Token ${token}`;

      this.$http.get(Api.activeCompany())
        .then((r) => {
          const company = r.data;
          Service.saveCompany(company);
          const { isin } = company;
          console.log('Forwarding to company page!');
          this.$router.push({ name: 'company', params: { isin } });
        })
        .catch((e) => {
          console.log(e);
          this.$router.push('foundFirstCompany');
        });
    },

    githubLogin(e) {
      e.preventDefault();

      this.$auth.authenticate('github').then((r) => {
        const token = r.data.key;
        Service.saveToken(token);
        console.log('Token has been saved!');

        this.$bvModal.show('bv-modal-success');
        setTimeout(() => {
          this.$bvModal.hide('bv-modal-success');
          this.forward(token);
        }, 1300);
      }).catch((err) => {
        console.log(err);
        console.log(err.response.data);
      });
    },
  },
};
</script>

<style scoped>

</style>
