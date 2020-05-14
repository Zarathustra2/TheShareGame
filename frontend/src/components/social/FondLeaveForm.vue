<template>
  <div>
    <p class="font-weight-light font-italic">
      If you want to leave the fond, click here.
      This will result in loosing access to the fond forum and so on.
    </p>

    <b-button variant="danger" v-on:click="onClick" class="leave-btn">
      Leave
    </b-button>

  </div>
</template>

<script>
import Api from '@/service/api';

import { BButton } from 'bootstrap-vue';

export default {
  name: 'FondLeaveForm',
  components: { BButton },
  methods: {
    onClick(e) {
      e.preventDefault();
      this.$http.delete(Api.fondsUserData()).then(() => {
        this.$store.commit('setFond', null);
        this.$router.push({ name: 'fonds' });
      }).catch((err) => {
        console.error(err);
      });
    },
  },
};
</script>

<style scoped>

</style>
