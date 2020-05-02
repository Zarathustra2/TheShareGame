<template>
  <b-navbar toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand to="#">TSG</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"/>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-item-dropdown text="Secruities">
          <b-dropdown-item to="/bonds">
            <span class="icon-margin-right text-primary fas fa-chart-line"/>
            Bonds
          </b-dropdown-item>
        </b-nav-item-dropdown>
        <b-nav-item-dropdown text="Market">
          <b-dropdown-item to="/live-orders">
            <span class="icon-margin-right text-primary fas fa-clock"/>
            Live-Orders
          </b-dropdown-item>
          <b-dropdown-item to="/trades">
            <span class="icon-margin-right text-primary fas fa-exchange-alt"/>
            Trades
          </b-dropdown-item>
          <b-dropdown-item to="/companies">
            <span class="icon-margin-right text-primary fas fa-building"/>
            Companies
          </b-dropdown-item>
          <b-dropdown-item to="/newspaper">
            <span class="icon-margin-right text-primary fas fa-newspaper"/>
            Newspaper
          </b-dropdown-item>
          <b-dropdown-item to="/forum">
            <span class="icon-margin-right text-primary fas fa-comments"/>
            Forum
          </b-dropdown-item>
        </b-nav-item-dropdown>

        <b-nav-item to="/login">Login</b-nav-item>
        <b-nav-item to="/register">Register</b-nav-item>

        <b-button
          size="sm" class="my-2 my-sm-0" variant="success"
          style="margin-right: 5px" target="_blank"
          href="https://docs.thesharegame.com"
        >
          Docs
        </b-button>


      </b-navbar-nav>

    </b-collapse>
  </b-navbar>
</template>

<script>
import {
  BButton, BDropdownItem, BCollapse,
} from 'bootstrap-vue';

export default {
  name: 'NavbarNotLoggedIn',
  components: {
    BButton, BDropdownItem, BCollapse,
  },
};
</script>

<style scoped>

</style>
