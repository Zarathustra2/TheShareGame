<template>
  <div>
    <Headline name="Logout"/>
    Use the button below to logout of your account.
    <br/>
    If you log out of your account, you need to login with your username and password again
    to play again!

    <b-form inline>
      <b-button variant="primary" type="submit" v-on:click="logout"
                class="buttonLogout">Logout
      </b-button>
    </b-form>

  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import { BForm, BButton } from 'bootstrap-vue';

export default {
  name: 'Logout',
  components: { Headline, BForm, BButton },
  methods: {
    logout() {
      // Log user out
      localStorage.clear();

      // Redirect to homepage
      this.$router.push('/');
    },
  },
};
</script>

<style scoped>

</style>
