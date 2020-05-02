<template>
  <NavbarLoggedIn v-if="loggedIn"/>
  <NavbarNotLoggedIn v-else/>
</template>

<script>
import Service from '@/service/service';
import NavbarLoggedIn from './NavbarLoggedIn.vue';
import NavbarNotLoggedIn from './NavbarNotLoggedIn.vue';

export default {
  name: 'Navbar',
  components: { NavbarNotLoggedIn, NavbarLoggedIn },
  data() {
    return {
      loggedIn: Service.isAuthenticated(),
    };
  },
};
</script>

<style scoped>

</style>
