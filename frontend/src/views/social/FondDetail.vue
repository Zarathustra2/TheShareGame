<template>
  <div>
    <Headline :name="name"/>
    <span v-if="profile === null">
      Loading...
    </span>
    <span v-else>

      <b-nav tabs class="fonds-tabs" v-if="ownFond()" style="margin-bottom: 15px">
        <b-nav-item :active="detailTab()" :disabled="detailTab()" v-on:click="tabClick">
          Detail
        </b-nav-item>
        <b-nav-item :active="forumTab()" :disabled="forumTab()" v-on:click="tabClick">
          Forum
        </b-nav-item>
        <b-nav-item
          :active="editTab()" :disabled="editTab()"
          v-on:click="tabClick" v-if="isFondLeader"
        >
          Edit
        </b-nav-item>
        <b-nav-item
          :active="applicationsTab()" :disabled="applicationsTab()"
          v-on:click="tabClick" v-if="isFondLeader"
        >
          Applications
        </b-nav-item>
        <b-nav-item :active="leaveTab()" :disabled="leaveTab()" v-on:click="tabClick">
          Leave
        </b-nav-item>
      </b-nav>

      <span v-if="detailTab()">
        <b-row>
          <b-col>
            <div class="card card-body bg-light">
              <h5>Description</h5>
              <hr>
              <Marked :markdown="profile.description"></Marked>
            </div>
          </b-col>
          <b-col>
            <div class="card card-body bg-light">
              <b-row>
                <b-col>
                  <ul>
                    <li>
                      Open for Applications:
                      <span
                        v-if="profile.open_for_application"
                        class="icon-margin-right text-success fas fa-check"
                        />
                        <span
                          v-else
                          class="icon-margin-right text-danger fa fa-times"
                          />
                    </li>
                    <li>Founder:
                      <router-link :to="{name: 'profile', params: {id: founder.id}}">
                        {{founder.username}}
                      </router-link>
                    </li>
                    <li>Members: {{members.length}}</li>
                    <li>Members BV: {{membersBvSum}}</li>
                  </ul>
                </b-col>
                <b-col>
                  <b-img :src="profile.logo"></b-img>
                </b-col>
              </b-row>

            </div>
          </b-col>
        </b-row>
        <b-row style="margin-top: 15px">
          <b-col>
            <b-table
              id="members-table"
              :hover="true"
              :striped="true"
              :small="true"
              :items="members"
              :fields="fields"
              >

              <template v-slot:cell(user)="data">
                <router-link :to="{name: 'profile', params: {id: data.value.id}}">
                  {{data.value.username}}
                </router-link>

              </template>

              <template v-slot:cell(leader)="data">
                <span
                  v-if="data.value"
                  class="icon-margin-right text-success fas fa-check"
                  />
                  <span
                    v-else
                    class="icon-margin-right text-danger fas fa-times"
                    />

              </template>

              <template v-slot:cell(bookvalue)="data">
                {{formatNum(data.item.user.companies_book_value)}}
              </template>

            </b-table>

            <b-pagination
              v-model="page"
              :total-rows="members.length"
              :per-page="size"
              align="right"
              />
          </b-col>
        </b-row>
      </span>
      <span v-else-if="forumTab()">
        <FondForum/>
      </span>
      <span v-else-if="editTab()">
        <FondProfileForm :profile="profile" @profileUpdate="profileUpdate"/>
      </span>
      <span v-else-if="applicationsTab()">
        <FondApplicationsList/>
      </span>
      <span v-else>
        <FondLeaveForm/>
      </span>
    </span>

  </div>

</template>

<script>
import Headline from '@/components/Headline.vue';
import FondProfileForm from '@/components/social/FondProfileForm.vue';
import FondForum from '@/components/social/FondForum.vue';
import FondApplicationsList from '@/components/social/FondApplicationsList.vue';
import FondLeaveForm from '@/components/social/FondLeaveForm.vue';

import Api from '@/service/api';
import { Number } from '@/service/utils';

import Marked from '@/components/Marked';

import {
  BCol, BRow, BTable, BPagination, BImg,
} from 'bootstrap-vue';

export default {
  name: 'FondDetail',
  components: {
    Marked,
    FondLeaveForm,
    FondApplicationsList,
    FondForum,
    FondProfileForm,
    Headline,
    BCol,
    BRow,
    BTable,
    BPagination,
    BImg,
  },
  data() {
    return {
      name: '',
      profile: null,
      members: [],
      founder: null,
      fields: ['user', 'leader', 'bookvalue'],
      page: 1,
      size: 10,
      activeTab: 'detail',
    };
  },
  created() {
    this.$http.get(Api.fond(this.$route.params.id)).then((r) => {
      const { data } = r;
      this.name = data.name;
      this.profile = data.profile;
      this.members = data.members;
      this.founder = data.founder;
    });
  },
  computed: {
    membersBvSum() {
      const sum = this.members.reduce((acc, val) => acc + val.user.companies_book_value, 0);
      return Number.numberWithDollar(sum);
    },
    isFondLeader() {
      return this.$store.getters.isFondLeader;
    },
  },
  methods: {
    formatNum(num) {
      return Number.numberWithDollar(num);
    },
    tabClick(e) {
      let txt = e.target.innerText;

      // Remove leading spaces and newlines as well as subsequent ones.
      // \n is covered by \s.
      // ^\s+ matches every whitespace from the beginning of the line until the first none
      // whitespace character and replaces it with ''.
      // Same for \s+$ but this time it matches everything after the word to the end of the line.
      txt = txt.replace(/^\s+|\s+$/g, '');
      this.activeTab = txt.toLowerCase();
    },
    detailTab() {
      return this.activeTab === 'detail';
    },
    forumTab() {
      return this.activeTab === 'forum';
    },
    editTab() {
      return this.activeTab === 'edit';
    },
    leaveTab() {
      return this.activeTab === 'leave';
    },
    applicationsTab() {
      return this.activeTab === 'applications';
    },

    /**
     * Returns whether the requesting user is a member of the fond hew is visiting.
     *
     */
    ownFond() {
      if (!this.$store.getters.hasFond) {
        return false;
      }

      const fond = this.$store.getters.getFond;

      return `${fond.fond.id}` === `${this.$route.params.id}`;
    },

    /**
     * If the profile gets updated, the child will emit
     * the new profile data back to the parent which is this component.
     * So we set the new profile data.
     *
     */
    profileUpdate(value) {
      this.profile = value;
    },
  },
};
</script>

<style scoped>

</style>
