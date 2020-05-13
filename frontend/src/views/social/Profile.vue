<template>
  <div>
    <Headline :name="headline"/>

    <b-nav tabs v-if="is_own_profile" class="profile-tabs">
      <b-nav-item :active="!isEdit()" :disabled="!isEdit()" v-on:click="tabClick">Profile
      </b-nav-item>
      <b-nav-item :active="isEdit()" :disabled="isEdit()" v-on:click="tabClick">Edit</b-nav-item>
    </b-nav>

    <b-row v-if="activeTab === 'profile'">
      <b-col cols="3">

        <center>
          <b-avatar src="https://placekitten.com/300/300" size="200px"></b-avatar>
        </center>

        <b-table-simple borderless>

          <b-tbody>
            <b-tr>
              <b-th>Company</b-th>
              <b-th class="text-right">
                <router-link :to="{name: 'company', params: {isin: company.isin}}"
                             v-if="company !== null">
                  {{company.name}}
                </router-link>
              </b-th>
            </b-tr>

            <b-tr>
              <b-th>Age</b-th>
              <b-th class="text-right">{{form.age}}</b-th>
            </b-tr>

          </b-tbody>
        </b-table-simple>

      </b-col>
      <b-col>
        <b-card bg-variant="light">
          <b-card-text>
            <Marked :markdown="form.description"></Marked>
          </b-card-text>
        </b-card>
      </b-col>
    </b-row>
    <b-row v-else>
      <b-col>
        <p class="font-weight-light font-italic">
          Edit your profile and tell the world a little bit about yourself!
        </p>
        <b-form @submit="onSubmit">

          <b-form-group id="group-age" label="Your Age:" label-for="input-age">
            <b-form-input
              id="input-age"
              v-model="form.age"
              required
              placeholder="Enter your age"
            ></b-form-input>
            <b-form-invalid-feedback :state="formFeedback.ageValid">
          {{ formFeedback.ageErrMsg }}
        </b-form-invalid-feedback>
          </b-form-group>

          <b-form-group id="group-description" label="Tell the world about yourself:"
                        label-for="input-description">
            <b-form-textarea
              id="input-description"
              v-model="form.description"
              required
              placeholder="Write something, Mr Schaetzing!"
              rows="6"
              max-rows="6"
            ></b-form-textarea>
            <b-form-invalid-feedback :state="formFeedback.descriptionValid">
          {{ formFeedback.descriptionErrMsg }}
        </b-form-invalid-feedback>
          </b-form-group>

          <b-form-group>
            <b-form-file
              accept=".jpg, .png, .gif"
              v-model="form.companyLogo"
              :state="Boolean(form.companyLogo)"
              placeholder="Choose a file or drop it here..."
              drop-placeholder="Drop file here..."
            ></b-form-file>
            <b-form-invalid-feedback :state="formFeedback.companyLogoValid">
          {{ formFeedback.companyLogoErrMsg }}
        </b-form-invalid-feedback>
          </b-form-group>
          <span v-if="currentLogoUrl !== ''">
            <hr>
            Current company logo: <br/>
            <img :src="currentLogoUrl" alt="company-logo"/>
            <br/>
            <hr>
          </span>

          <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage"/>
          <b-button type="submit" variant="primary" class="btn-submit">Submit</b-button>

        </b-form>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Api from '@/service/api';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';

import Marked from '@/components/Marked';

import {
  BFormGroup, BFormFile, BFormInvalidFeedback, BButton, BCol, BRow, BFormTextarea, BCard, BCardText,
  BTableSimple, BTbody, BTh, BTr, BAvatar, BForm, BFormInput,
} from 'bootstrap-vue';


export default {
  name: 'Profile',
  components: {
    Headline,
    AlertDangerForm,
    BFormGroup,
    BFormFile,
    BFormInvalidFeedback,
    BButton,
    BCol,
    BRow,
    BFormTextarea,
    BCard,
    BCardText,
    BTableSimple,
    BTbody,
    BTh,
    BTr,
    BAvatar,
    BForm,
    BFormInput,
    Marked,
  },
  data() {
    return {
      company: null,
      user: null,
      is_own_profile: false,

      activeTab: 'profile',

      currentLogoUrl: '',

      form: {
        companyLogo: null,
        age: 42,
        description: 'This user prefers to keep an air of mystery about them.',
      },
      formFeedback: {
        ageErrMsg: '',
        ageValid: true,
        companyLogoErrMsg: '',
        companyLogoValid: true,
        descriptionErrMsg: '',
        descriptionValid: true,
        isValid: true,
        errMessage: '',
      },
    };
  },

  computed: {
    headline() {
      if (this.user === null) {
        return '';
      }
      return `${this.user.username}'s Profile`;
    },
  },

  methods: {
    isEdit() {
      return this.activeTab !== 'profile';
    },
    tabClick() {
      if (this.isEdit()) {
        this.activeTab = 'profile';
      } else {
        this.activeTab = 'edit';
      }
    },
    onSubmit(e) {
      e.preventDefault();
      resetFormErrors(this);

      let payload = {
        age: this.form.age,
        description: this.form.description,
      };

      let config = {};

      if (this.form.companyLogo !== null) {
        const formData = new FormData();

        formData.append('age', payload.age);
        formData.append('description', payload.description);
        formData.append('company_logo', this.form.companyLogo);
        payload = formData;
        config = { headers: { 'Content-Type': 'multipart/form-data' } };
      }

      this.$http.put(Api.profile(this.$route.params.id), payload, config).then((r) => {
        const { data } = r;

        this.form.age = data.age;
        this.form.description = data.description;

        // eslint-disable-next-line
        this.currentLogoUrl = data.company_logo;

        this.$bvToast.toast('Your profile has been updated!', {
          title: 'Success',
          autoHideDelay: 5000,
          appendToast: false,
          variant: 'primary',
          id: 'profile-notification',
        });
      }).catch((err) => {
        parseErrorsForm(this, err.response.data);
      });
    },
    fetchData() {
      const { id } = this.$route.params;

      this.$http.get(Api.profile(id)).then((r) => {
        const { data } = r;

        this.company = data.company;
        this.user = data.user;
        this.is_own_profile = data.is_own_profile;
        this.form.age = data.age;
        this.form.description = data.description;

        this.currentLogoUrl = data.company_logo;
      });
    },
  },

  mounted() {
    this.fetchData();
  },
};
</script>

<style scoped>
  .profile-tabs {
    margin-bottom: 10px;
  }
</style>
