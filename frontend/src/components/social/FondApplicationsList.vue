<template>
  <div v-if="applications.length === 0">
    Nobody has applied yet
  </div>
  <div v-else>
    <b-row>
      <b-col cols="6" v-for="app in applications" v-bind:key="app.id">
        <b-card header-tag="header" footer-tag="footer">

          <template v-slot:header>
            <h6 class="mb-0">
              User:
              <router-link :to="{name: 'profile', params: {id: app.user.id}}">
                {{app.user.username}}
              </router-link>
            </h6>
          </template>

          <b-card-text>{{app.text}}</b-card-text>
          <b-button
            href="#"
            variant="success"
            v-on:click="buttonClick($event, app.id, true, app.user)"
          >
            Accept
          </b-button>
          <b-button
            href="#"
            variant="warning"
            v-on:click="buttonClick($event, app.id, false, app.user)"
          >
            Decline
          </b-button>

          <template v-slot:footer>
            <em>{{app.created}}</em>
          </template>

        </b-card>

      </b-col>
    </b-row>
    <b-pagination
        v-model="page"
        :total-rows="total"
        :per-page="size"
        align="right"
        >
      </b-pagination>
  </div>
</template>

<script>
import Api from '@/service/api';

import {
  BCol, BRow, BPagination, BCard, BCardText, BButton,
} from 'bootstrap-vue';


export default {
  name: 'FondApplicationsList',
  components: {
    BCol, BRow, BPagination, BCard, BCardText, BButton,
  },
  data() {
    return {
      page: 1,
      size: 10,
      total: 0,
      applications: [],
    };
  },
  created() {
    this.$http.get(Api.fondApplication(this.$route.params.id, this.page, this.size)).then((r) => {
      const { data } = r;
      this.applications = data.results;
      this.total = data.count;
    }).catch((err) => {
      console.error(err);
    });
  },
  methods: {
    buttonClick(e, id, accepted, user) {
      const data = {
        accepted,
      };

      this.$http.delete(Api.fondApplicationDelete(this.$route.params.id, id), { data }).then(() => {
        const variant = (accepted) ? 'success' : 'warning';
        const title = (accepted) ? 'Accepted' : 'Declined';
        const msg = (accepted) ? `${user.username} has been accepted`
          : `${user.username} has been declined. A notification has been sent`;

        this.$bvToast.toast(msg, {
          title,
          autoHideDelay: 5000,
          appendToast: false,
          variant,
          id: 'appl-notification',
        });

        this.applications = this.applications.filter((app) => app.id !== id);
      }).catch((err) => {
        console.error(err);
      });
    },
  },

};
</script>

<style scoped>

</style>
