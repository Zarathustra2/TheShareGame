<template>

  <div>
    <Headline name="Fonds"/>

    <b-nav tabs class="fonds-tabs" v-if="!hasFond && isLoggedIn">
      <b-nav-item :active="fondsTab()" :disabled="fondsTab()" v-on:click="tabClick">
        Fonds
      </b-nav-item>
      <b-nav-item :active="newFondTab()" :disabled="newFondTab()" v-on:click="tabClick">
        Found new fond
      </b-nav-item>
    </b-nav>

    <p class="font-weight-light font-italic" style="margin-top: 10px">
    A fond is a group of players who want to share their knowledge with each other.
    Together they can come up with new strategies.
    <br>
    Each fond has their own forum and chat they can use to communicate.
    One player can only be in one forum at a time.
    </p>

    <span v-if="fondsTab() || !isLoggedIn">
      <list :getData="getFonds" :slots="templates" :childFields="fields" id="fonds">
      <template slot="name" slot-scope="data">
        <router-link :to="{name: 'fondDetail', params: {id: data.tbl.item.id}}">
          {{data.tbl.value}}
        </router-link>
      </template>

      <template slot="apply" slot-scope="data" v-if="!hasFond">

        <span v-if="data.tbl.item.profile.open_for_application">
          <router-link :to="{name: 'applicationFond', params: {id: data.tbl.item.id}}">
            Apply now!
          </router-link>

        </span>
        <span v-else>
          Applications closed!
        </span>

      </template>

      </list>
    </span>

    <span v-else>
      <b-form @submit="onSubmit">
        <b-form-group
          id="name"
          label="Name"
          description="Name of the new fond"
          >
          <b-form-input
            id="name-input"
            v-model="form.name"
            required
            size="sm"
            />
            <b-form-invalid-feedback :state="formFeedback.nameValid">
              {{ formFeedback.nameErrMsg }}
            </b-form-invalid-feedback>
        </b-form-group>
        <b-button type="submit" variant="success">Submit</b-button>

        <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">

        </AlertDangerForm>

        </b-form>
    </span>
  </div>

</template>

<script>

import Headline from '@/components/Headline.vue';
import List from '@/components/List.vue';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Api from '@/service/api';
import { Table } from '@/service/utils';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import Service from '@/service/service';
import {
  BForm, BFormGroup, BFormInvalidFeedback, BButton, BFormInput,
} from 'bootstrap-vue';

export default {
  name: 'Fonds',
  components: {
    Headline,
    List,
    AlertDangerForm,
    BForm,
    BFormGroup,
    BFormInvalidFeedback,
    BButton,
    BFormInput,
  },
  data() {
    const fields = [
      {
        key: 'id', label: 'ID', sortable: true, sortDirection: 'desc', class: 'id',
      },
      {
        key: 'name', label: 'Name', sortable: true, sortDirection: 'desc', class: 'name',
      },
      {
        key: 'amount_members', label: 'Members', sortable: false, class: 'members',
      },


    ];

    if (!this.$store.getters.hasFond) {
      fields.push({
        key: 'apply', label: 'Apply', sortable: false, class: 'apply',
      });
    }

    return {
      activeTab: 'fonds',
      templates: [
        { name: 'name', field: 'name' },
        { name: 'apply', field: 'apply' },
      ],
      fields,
      form: {
        name: '',
      },
      formFeedback: {
        isValid: true,
        errMessage: '',
        nameValid: true,
        nameErrMsg: '',
      },
      isLoggedIn: Service.isAuthenticated,
    };
  },
  methods: {
    getFonds(c, ctx) {
      Table.getTableData({
        url: Api.fonds, component: c, page: c.page, size: c.size, ctx,
      });
    },
    fondsTab() {
      return this.activeTab === 'fonds';
    },
    newFondTab() {
      return this.activeTab === 'found-new-fond';
    },
    tabClick(e) {
      const txt = e.target.innerText;
      this.activeTab = txt.toLowerCase().replace(/\s/g, '-');
    },
    onSubmit(e) {
      e.preventDefault();
      resetFormErrors(this);

      const data = {
        name: this.form.name,
      };

      this.$http.post(Api.fonds(0, 0, null), data).then(() => {
        // Reset the fond data in vuex to be undefined so fondData fetches the data again
        // from the backend
        this.$store.commit('setFond', undefined);
        this.$store.dispatch('fondData');
      }).catch((err) => {
        parseErrorsForm(this, err.response.data);
      });
    },
  },
  computed: {
    hasFond() {
      return this.$store.getters.hasFond;
    },

  },
};
</script>

<style scoped>
</style>
