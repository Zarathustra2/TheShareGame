<template>
  <div class="card card-body bg-light">
    <table class="table borderless" id="data-table">
      <tbody>
      <tr style="border-top: hidden;">
        <td>
          <router-link :to="{name: 'order', params: {isin: isin}}">
            Place Order
          </router-link>
        </td>
        <td>
          <router-link :to="{name: 'orderbook', params: {isin: isin,
           companyName: companyName}}">
            Orderbook
          </router-link>
        </td>
      </tr>
      <tr style="border-top: hidden;">

        <td>
          <router-link :to="{name: 'statementOfAccount', params: {isin: isin,
           companyName: companyName}}">
            Statement of Account
          </router-link>
        </td>
        <td>
          <router-link :to="{name: 'tradesCompany', params: {isin: isin,
          companyName: companyName}}">
            Trades
          </router-link>
        </td>
      </tr>
      <tr style="border-top: hidden;">
        <td v-if="user !== null">
          <router-link :to="{name: 'messages', query: {user_id: user.id}}">
          Message {{user.username}}
          </router-link>
        </td>
        <td>
          <router-link :to="{name: 'articlesCompany', params: {isin: isin,
           companyName: companyName}}">
          Articles
            </router-link>
        </td>
      </tr>
      <tr style="border-top: hidden;">
        <td>
          <router-link :to="{name: 'depot', params: {isin: isin,
           companyName: companyName}}">
            Depot - {{this.depot.length}}
          </router-link>
        </td>
        <td>
          <router-link :to="{name: 'shareholders', params: {isin: isin,
           companyName: companyName}}">
          Shareholders - {{this.shareholders.length}}
          </router-link>
        </td>
      </tr>
      <tr style="border-top: hidden;">
        <td>
          <router-link :to="{name: 'buyerSeller', params: {isin: isin,
          companyName: companyName}}">
            Buyer/Seller
          </router-link>
        </td>
        <td v-if="user !== null">
          CEO:
          <router-link :to="{name: 'profile', params: {id: user.id}}">
            {{user.username}}
          </router-link>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'LinksSheets',
  props: {
    isin: String,
    user: Object,
    companyName: String,
    shareholders: {
      type: Array,
      default() {
        return [];
      },
    },
    depot: {
      type: Array,
      default() {
        return [];
      },
    },

  },
};
</script>

<style scoped>

</style>
