<template>
  <div>
    <div class="card card-body bg-light">
      <table class="table borderless" id="data-table">
        <tbody>
          <tr style="border-top: hidden;">
            <td id="sell_button">
              <b class="text-danger">Bid:</b>
              <br>
              <span>
                <span v-if="key_figures.bid === null">N/A</span>
                <span v-else> {{ key_figures.bid.price }}$ </span>
                <span class="text-danger">
                  <router-link
                      v-if="key_figures.bid !== null"
                      :to="{name: 'order', params: {isin: isin},
                                       query:{price:key_figures.bid.price,
                                       amount:key_figures.bid.total_amount, typ: 'Sell'}}">
                    Sell
                  </router-link>

                  <router-link
                      v-else
                    :to="{name: 'order', params: {isin: isin}, query:{price:
                         key_figures.share_price, typ: 'Sell'}}">
                    Sell
                  </router-link>


                </span>
                <br>
                <small>
                  <small>
                    <span v-if="key_figures.bid === null">N/A </span>
                    <span v-else> {{ key_figures.bid.total_amount }} </span>
                    Shares
                  </small>
                </small>
              </span>
            </td>
            <td>
              <b class="text-primary">Share Price:</b>
              <br>
              <span id="share_price">
                {{ this.share_price }}
              </span>
              <br>
            </td>
            <td id="buy_button">
              <b class="text-success">Ask:</b><br>
              <span>
                <span v-if="key_figures.ask === null">N/A</span>
                <span v-else> {{ key_figures.ask.price }}$ </span>
                <span class="text-success">
                  <router-link v-if="key_figures.ask !== null"
                  :to="{name: 'order', params: {isin: isin},
                                    query:{price:key_figures.ask.price,
                                    amount:key_figures.ask.total_amount,
                                    typ: 'Buy'}}">
                    Buy
                  </router-link>
                  <router-link v-else
                               :to="{name: 'order', params: {isin: isin},
                                    query:{price:key_figures.share_price,
                                    typ: 'Buy'}}">
                    Buy
                  </router-link>

                </span>
                <br>
                <small>
                  <small>
                    <span v-if="key_figures.ask === null">N/A </span>
                    <span v-else> {{ key_figures.ask.total_amount }} </span>
                    Shares
                  </small>
                </small>
              </span>
            </td>
          </tr>
          <tr style="border: 5px;">
            <td><b>BV/S <a href="#" onclick="return false;" id="bv-s-tooltip">?</a></b><br>
              <span id="bv-s">
                {{ this.bookvalue_share }}
              </span>
            </td>
            <td><b>BV <a href="#" onclick="return false;" id="bv-tooltip">?</a></b><br>
              <span id="bv">
                {{ this.bookvalue }}
              </span>
            </td>
            <td>
              <b>Activity
                <a href="#" onclick="return false;" id="activity-tooltip">?</a>
              </b><br>
              <span id="activity">{{this.key_figures.activity}}%</span>
            </td>
          </tr>
          <tr style="border-top: hidden;">
            <td>
              <b class="text-info">TC/S
                <a href="#" onclick="return false;" id="tc-tooltip">?</a>
              </b><br>
              <span id="tc_share">{{ this.ttoc_share }}</span>
            </td>
            <td>
              <b class="text-info">CDGR
                <a href="#" onclick="return false;" id="cdgr-tooltip">?</a>
              </b><br>
              <span id="cdgr">{{ this.key_figures.cdgr }}%</span>
            </td>
            <td>
              <b class="text-info">MC
                <a href="#" onclick="return false;" id="mc-tooltip">?</a></b>
              <br>
              <span id="market_cap">{{ this.market_cap }}</span>
            </td>
          </tr>
          <tr style="border-top: hidden;">
            <td>
              <b class="text-warning">Free-Float
                <a href="#" onclick="return false;" id="ff-tooltip">?</a>
              </b><br>
              <span id="free_float">{{ this.key_figures.free_float }}%</span>
            </td>
            <td>
            </td>
            <td>
              <b class="text-warning">Shares
                <a onclick="return false;" href="#" id="shares-tooltip">?</a>
              </b><br>
              <span id="quant_shares">{{ this.a_shares }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <b-tooltip target="mc-tooltip">
      The market capitalization refers to the value of the company on the market.
      It is calculated by multiplying the share price with the amount of shares.
    </b-tooltip>

    <b-tooltip target="shares-tooltip">
      The amount of shares that are available of this company.
    </b-tooltip>

    <b-tooltip target="ff-tooltip">
      The free float indicates how equal the shares are distributed over the shareholders.
    </b-tooltip>

    <b-tooltip target="cdgr-tooltip">
      The compound daily growth rate. It is a measurement for the daily growth of a company.
    </b-tooltip>

    <b-tooltip target="tc-tooltip">
      Total Turnover Capital stands for how much cash this company could get immediately
      if it sells everything.
    </b-tooltip>

    <b-tooltip target="activity-tooltip">
      How active a company trades.
    </b-tooltip>

    <b-tooltip target="bv-tooltip">
      The book value is the sum of all its assets: Simply adding Depot + Cash + Bonds.
    </b-tooltip>

    <b-tooltip target="bv-s-tooltip">
      The same as book value but per share.
    </b-tooltip>

  </div>
</template>

<script>
import { Number } from '@/service/utils';

import Vue from 'vue';
import { TooltipPlugin } from 'bootstrap-vue';

Vue.use(TooltipPlugin);

export default {
  name: 'Datasheet',
  props: ['key_figures', 'cash', 'shares', 'isin'],

  computed: {
    bookvalue() {
      return Number.numberWithDollar(this.round(this.key_figures.book_value));
    },
    bookvalue_share() {
      const num = this.key_figures.book_value / this.shares;
      return Number.numberWithDollar(this.round(num));
    },
    ttoc_share() {
      const num = this.key_figures.ttoc / this.shares;
      return Number.numberWithDollar(this.round(num));
    },
    share_price() {
      return Number.numberWithDollar(this.round(this.key_figures.share_price));
    },
    a_shares() {
      // recursion
      return Number.formatNumber(this.shares);
    },
    market_cap() {
      const total = this.shares * this.key_figures.share_price;
      return Number.numberWithDollar(this.round(total));
    },
  },
  methods: {
    round(num) {
      return Math.round(num * 100) / 100;
    },
  },
};

</script>

<style scoped>

</style>
