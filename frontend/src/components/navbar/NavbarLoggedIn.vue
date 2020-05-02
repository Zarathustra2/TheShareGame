<template>

  <b-navbar toggleable="lg" type="dark" variant="dark">
    <b-navbar-brand :to="url">TSG</b-navbar-brand>

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

        <b-nav-item-dropdown text="Invest">

          <b-dropdown-item to="/orders/own">
            <span class="icon-margin-right text-primary fas fa-money-check"/>
            Orders
          </b-dropdown-item>

          <b-dropdown-item :to="urlDepot">
            <span class="icon-margin-right text-primary fas fa-chart-pie"/>
            Depot
          </b-dropdown-item>

          <b-dropdown-item :to="urlStatement">
            <span class="icon-margin-right text-primary fas fa-book"/>
            Statement
          </b-dropdown-item>

        </b-nav-item-dropdown>

        <b-nav-item-dropdown text="Social">

          <template v-slot:text v-if="totalUnread > 0">
            Social
            <b-badge variant="danger" class="badge-vertical">{{totalUnread}}</b-badge>
          </template>

          <b-dropdown-item to="/messages">
            <span class="icon-margin-right text-primary fas fa-envelope"/>
            Messages
            <b-badge variant="danger" class="badge-vertical" v-if="unreadMessages > 0">
              {{unreadMessages}}
            </b-badge>
          </b-dropdown-item>

          <b-dropdown-item to="/notifications">
            <span class="icon-margin-right text-primary fas fa-paper-plane"/>
            Alerts
            <b-badge variant="danger" class="badge-vertical" v-if="unreadNotifications > 0">
              {{unreadNotifications}}
            </b-badge>
          </b-dropdown-item>

          <b-dropdown-item to="/chat">
            <span class="icon-margin-right text-primary fas fa-comment"/>
            Chat
          </b-dropdown-item>

          <b-dropdown-item to="/fonds">
            <span class="icon-margin-right text-primary fas fa-users"/>
            Fonds
          </b-dropdown-item>

          <hr>

          <b-dropdown-item :to="`/fonds/${getFond.id}`" v-if="hasFond">
            {{getFond.name}}
          </b-dropdown-item>

        </b-nav-item-dropdown>

        <b-button
          size="sm" class="my-2 my-sm-0" variant="success"
          style="margin-right: 5px" target="_blank"
          href="https://docs.thesharegame.com"
        >
          Docs
        </b-button>

      </b-navbar-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">

        <b-button
          size="sm" class="my-2 my-sm-0" variant="success"
          style="margin-right: 5px" target="_blank"
          href="https://github.com/Zarathustra2/TheShareGame"
        >
          Github
        </b-button>

        <b-button size="sm" class="my-2 my-sm-0" variant="warning">Beta</b-button>

        <b-nav-item-dropdown right>
          <!-- Using 'button-content' slot -->
          <template v-slot:button-content>
            <em>User</em>
          </template>
          <b-dropdown-item :to="urlProfile">
            <span class="icon-margin-right text-primary fas fa-id-badge"/>
            Profile
          </b-dropdown-item>
          <b-dropdown-item to="/logout">
            <span class="icon-margin-right text-primary fas fa-sign-out-alt"/>
            Sign Out
          </b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
    </b-collapse>
  </b-navbar>

</template>

<script>
import Service from '@/service/service';
import { BBadge, BButton } from 'bootstrap-vue';

export default {
  name: 'NavbarLoggedIn',
  components: { BButton, BBadge },
  data() {
    let url = this.$router.resolve({ name: 'foundFirstCompany' }).href;
    let urlStatement = '';
    let urlDepot = '';
    let urlProfile = '';

    if (Service.hasCompany()) {
      // eslint-disable-next-line
      const {isin, user_id} = Service.getCompany();

      url = this.$router.resolve({ name: 'company', params: { isin } }).href;
      urlStatement = this.$router.resolve({ name: 'statementOfAccount', params: { isin } }).href;
      urlDepot = this.$router.resolve({ name: 'depot', params: { isin } }).href;
      urlProfile = this.$router.resolve({ name: 'profile', params: { id: user_id } }).href;
    }

    return {
      url, urlStatement, urlDepot, urlProfile,
    };
  },

  created() {
    // update the amount of unread notifications and messages
    this.$store.dispatch('unread');

    // set the fond data
    this.$store.dispatch('fondData');
  },

  computed: {
    unreadMessages() {
      return this.$store.getters.getUnread.unreadMessages;
    },
    unreadNotifications() {
      return this.$store.getters.getUnread.unreadNotifications;
    },
    totalUnread() {
      return this.$store.getters.getTotalUnread;
    },
    hasFond() {
      return this.$store.getters.hasFond;
    },
    getFond() {
      return this.$store.getters.getFond.fond;
    },
  },
};
</script>

<style scoped>

  .badge-vertical {
    vertical-align: top;
  }

  .icon-margin-right {
    margin-right: 3px;
  }

</style>
