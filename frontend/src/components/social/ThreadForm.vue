<template>
  <div>
    <b-form @submit="onSubmit">
      <b-form-group
        id="name"
        label="Name"
        description="Name of the Thread"
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
      <AlertSuccessForm msg="Thread has been created" :show="created"/>

    </b-form>
  </div>
</template>

<script>

import AlertDangerForm from '@/components/AlertDangerForm.vue';
import AlertSuccessForm from '@/components/AlertSuccessForm.vue';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import {
  BForm, BFormGroup, BFormInvalidFeedback, BButton, BFormInput,
} from 'bootstrap-vue';

export default {
  name: 'ThreadForm',
  components: {
    AlertSuccessForm, AlertDangerForm, BForm, BFormGroup, BFormInvalidFeedback, BButton, BFormInput,
  },
  props: {
    url: String,
  },
  data() {
    return {
      form: {
        name: '',

      },

      formFeedback: {
        nameValid: true,
        nameErrMsg: '',
        isValid: true,
        errMessage: '',
      },
      created: false,

    };
  },
  methods: {
    onSubmit(evt) {
      evt.preventDefault();
      resetFormErrors(this);

      const { name } = this.form;

      const data = { name };

      console.log('ThreadForm: ', this.url);

      this.$http.post(this.url, data).then((r) => {
        console.log('ThreadForm: ', r);
        this.created = true;
        this.$emit('forceReload', true);
      }).catch((e) => {
        parseErrorsForm(this, e.response.data);
      });
    },
  },

};
</script>

<style scoped>

</style>
