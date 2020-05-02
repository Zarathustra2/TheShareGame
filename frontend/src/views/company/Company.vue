<template>
  <div>
    <ChatBox amount=5></ChatBox>
    <div v-if="company === null">Loading Data...</div>
    <div v-else id="company">
      <b-row>
        <b-col cols="2" class="d-none d-sm-block">
          <Sidebar></Sidebar>
        </b-col>
        <b-col>
          <div class="text-center">

            <center>
              <h1 id="company_name">
                {{company.name}}
              </h1>

              <h3 class="lead" style="letter-spacing: 3px; margin-top: 1px">
            <span style="font-size: 75%">
                <p class="lead initialism">
                  <i class="language flag-icon flag-icon-ge"/>
                    <span id="isin">ISIN: {{company.isin}}</span>
                    <span v-if="company.user !== null" id="ceo_username">
                      <br>Ceo: {{company.user.username}}
                    </span>
                </p>
            </span>
              </h3>

              <img
                v-if="logo === null"
                src="@/assets/centralbank.jpg"
                class="img-responsive"
                alt=""
              >
              <img v-else :src="logo" class="img-responsive" alt="">
            </center>
            <b-row id="company-info">
              <b-col>
                <Datasheet
                   id="datasheet"
                   :key_figures="company.key_figures"
                   :cash="company.cash"
                   :shares="company.shares"
                   :isin="company.isin"
                />

              </b-col>
              <b-col>
                <LinksSheets
                   :isin="company.isin"
                   :user="company.user"
                   :companyName="company.name"
                   :shareholders="shareholders"
                   :depot="depot"
                />
              </b-col>
            </b-row>

            <hr>
            <div :key="isin">
              <b-row>
                <b-col sm>
                  <LiquidityPieChart/>
                </b-col>
                <b-col sm>
                  <DepotPieChart @depot="depotEmit"/>
                </b-col>
                <b-col sm>
                  <ShareholdersPieChart @shareholders="shareholdersEmit"/>
                </b-col>
              </b-row>

              <hr>
              <b-row>
                <b-col>
                  <KeyFiguresChart></KeyFiguresChart>
                </b-col>
              </b-row>
            </div>

          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import Api from '@/service/api';
import Datasheet from '@/components/company/Datasheet.vue';
import LinksSheets from '@/components/company/LinksSheets.vue';
import LiquidityPieChart from '@/components/company/charts/LiquidityPieChart.vue';
import ShareholdersPieChart from '@/components/company/charts/ShareholdersPieChart.vue';
import DepotPieChart from '@/components/company/charts/DepotPieChart.vue';
import ChatBox from '@/components/social/ChatBox.vue';
import KeyFiguresChart from '@/components/company/charts/KeyFiguresChart.vue';
import Sidebar from '@/components/Sidebar.vue';
import { BRow, BCol } from 'bootstrap-vue';


export default {
  name: 'Company',
  components: {
    Sidebar,
    KeyFiguresChart,
    ChatBox,
    DepotPieChart,
    ShareholdersPieChart,
    LiquidityPieChart,
    LinksSheets,
    Datasheet,
    BRow,
    BCol,
  },
  data() {
    return {
      company: null,
      shareholders: [],
      depot: [],
    };
  },
  methods: {
    getData() {
      this.$http.get(Api.company(this.$route.params.isin))
        .then((r) => {
          this.company = r.data;
        })
        .catch((e) => {
          console.log(e);
          this.$router.push('notFound');
        });
    },
    shareholdersEmit(data) {
      this.shareholders = data;
    },
    depotEmit(data) {
      this.depot = data;
    },
  },
  mounted() {
    this.getData();
  },
  watch: {
    $route: {
      handler() {
        this.getData();
      },
    },
  },
  computed: {
    isin() {
      return this.$route.params.isin;
    },
    logo() {
      if (this.company === null) {
        return null;
      }

      const { logo } = this.company;

      // If we are in developement we dont need to
      // check for https
      if (process.env.NODE_ENV === 'development') {
        console.log('developement logo');
        return logo;
      }

      return (logo) ? logo.replace('http', 'https') : null;
    },
  },

};
</script>

<style scoped>

  #company-info {
    margin-top: 8px;
  }

  #company {
    margin-top: 15px;
  }

</style>
