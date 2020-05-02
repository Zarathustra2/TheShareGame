<template>
  <div>
    <Headline name="Edit the profile"></Headline>
    <b-form @submit="onSubmit" style="margin-top: 15px">

      <b-form-group
        id="group-description"
        label="Description"
        label-for="input-description"
        description="You can use markdown to format your text."
      >
        <b-form-textarea
          id="input-description"
          v-model="form.description"
          required
          placeholder="Describe your fond"
          rows="6"
          max-rows="6"
        ></b-form-textarea>
        <b-form-invalid-feedback :state="formFeedback.descriptionValid">
          {{ formFeedback.descriptionErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <hr>
      <b-form-group
        id="group-open-for-application"
        label-for="input-description"
        description="Control whether users can apply or not"
      >

      <b-form-checkbox v-model="form.open_for_application" name="check-button" switch>
        Open for Applications:
        <span
          v-if="form.open_for_application"
          class="icon-margin-right text-success fas fa-check"
        />
        <span
          v-else
          class="icon-margin-right text-danger fa fa-times"
        />
      </b-form-checkbox>
      </b-form-group>

      <hr>

      <b-form-group
        label="Fond Logo"
        label-for="input-logo"
        description="The logo of your fond"
      >
        <b-form-file
          accept=".jpg, .png, .gif"
          v-model="form.logo"
          :state="Boolean(form.logo)"
          placeholder="Choose a file or drop it here..."
          drop-placeholder="Drop file here..."
        ></b-form-file>
        <b-form-invalid-feedback :state="formFeedback.logoValid">
          {{ formFeedback.logoErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage"/>
      <b-button type="submit" variant="primary">Submit</b-button>

    </b-form>
  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import Api from '@/service/api';

import {
  BForm, BButton, BFormGroup, BFormFile, BFormInvalidFeedback, BFormCheckbox, BFormTextarea,
} from 'bootstrap-vue';

export default {
  name: 'FondProfileForm',
  components: {
    Headline,
    AlertDangerForm,
    BForm,
    BButton,
    BFormGroup,
    BFormFile,
    BFormInvalidFeedback,
    BFormCheckbox,
    BFormTextarea,
  },
  props: {
    profile: Object,
  },
  data() {
    return {
      form: {
        logo: null,
        description: this.profile.description,
        open_for_application: this.profile.open_for_application,
      },
      formFeedback: {
        isValid: true,
        errMessage: '',
        logoValid: true,
        logoErrMsg: '',
        descriptionValid: true,
        descriptionErrMsg: '',
      },
    };
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();
      resetFormErrors(this);

      let payload = {
        open_for_application: this.form.open_for_application,
        description: this.form.description,
      };

      let config = {};

      if (this.form.logo !== null) {
        const formData = new FormData();

        formData.append('open_for_application', payload.open_for_application);
        formData.append('description', payload.description);
        formData.append('logo', this.form.logo);
        payload = formData;
        config = { headers: { 'Content-Type': 'multipart/form-data' } };
      }

      this.$http.put(Api.fondProfile(this.$route.params.id), payload, config).then((r) => {
        const { data } = r;

        // Send the profile data back to the parent
        this.$emit('profileUpdate', data);
      }).catch((err) => {
        parseErrorsForm(this, err.response.data);
      });
    },
  },
};
</script>

<style scoped>

</style>
