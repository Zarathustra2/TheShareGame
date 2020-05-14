<template>
  <div>
    <Headline name="Found Company"/>
    <p>
      Hey there, it seems like this is your first time here!
      To continue, you need to create a new company. Just fill out the form down below and have fun!
    </p>
    <b-form @submit.prevent="newCompany">

      <b-form-group
        label="Name:"
        label-for="name"
        description="The name of your company.
        Please do not choose the name of an existing company.
        The name can later be changed."
      >
        <b-form-input
          id="input-1"
          v-model="form.name"
          required
          placeholder="NameOfYourCompany Inc."
          ref="nameInput"
        />
        <b-form-invalid-feedback :state="formFeedback.nameValid">
          {{ formFeedback.nameErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group label="Country" label-for="country"
                    description="The country of your company.
        Choose a country whose language you speak
        You will be assigned to the chat of this country/language.
        "
      >
        <b-form-select
          v-model="form.country"
          :options="countries"
          required
          ref="countryInput"
        />
        <b-form-invalid-feedback :state="formFeedback.countryValid">
          {{ formFeedback.countryErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group label="Shares" label-for="shares"
                    description="
      The amount of shares your company will give out.
      It does not affect your company value.
      If you choose 200,000 shares the price of a single share
      will be cheaper than compared to 100,000 shares.
      "
      >
        <b-form-select
          v-model="form.shares"
          :options="sharesOption"
          required
          ref="sharesInput"
        />
        <b-form-invalid-feedback :state="formFeedback.sharesValid">
          {{ formFeedback.sharesErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage"/>

      <b-button variant="primary" type="submit" class="submit-btn">Submit</b-button>
    </b-form>

    <b-modal id="bv-modal-founding" centered hide-footer>
    <template v-slot:modal-title>
      <span class="text-primary">Congrats</span>
    </template>
    <div class="d-block text-center">
      You have created a new account! Now you just have to found a new company. Fill out the form,
      and you are ready to go!
    </div>
    <b-button class="mt-3" block @click="$bvModal.hide('bv-modal-founding')">
      Create a company!
    </b-button>
  </b-modal>

  </div>
</template>

<script>
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';
import Service from '@/service/service';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import {
  BForm, BFormGroup, BFormInput, BFormInvalidFeedback, BButton, BFormSelect,
  ModalPlugin,
} from 'bootstrap-vue';

import Vue from 'vue';

Vue.use(ModalPlugin);


export default {
  name: 'FoundFirstCompany',
  components: {
    AlertDangerForm,
    Headline,
    BForm,
    BFormGroup,
    BFormInput,
    BFormInvalidFeedback,
    BButton,
    BFormSelect,
  },
  data() {
    return {
      form: {
        name: '',
        country: 'US',
        shares: 1000000,
      },
      formFeedback: {
        nameValid: true,
        nameErrMsg: '',
        countryValid: true,
        countryErrMsg: '',
        sharesValid: true,
        sharesErrMsg: '',
        isValid: true,
        errMessage: '',
      },
      sharesOption: [10000, 20000, 50000, 1000000],
      countries: ['US', 'GE', 'RU', 'IR'],

    };
  },
  methods: {
    newCompany() {
      const data = {
        name: this.form.name,
        country: this.form.country,
        shares: this.form.shares,
      };

      Service.checkAxiosToken();

      resetFormErrors(this);

      this.$http.post(Api.companies(), data)
        .then((r) => {
          const company = r.data;
          const { isin } = company;
          Service.saveCompany(company);

          this.$router.push({ name: 'company', params: { isin } });
        })
        .catch((e) => {
          console.error(e);
          parseErrorsForm(this, e.response.data);
        });
    },
  },
  mounted() {
    this.$bvModal.show('bv-modal-founding');
  },
};

</script>

<style scoped>

</style>
