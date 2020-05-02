<template>
   <div>
    <b-form @submit="onSubmit">
      <b-form-group
        id="text"
        label="Text"
        description="Post something!"
      >
        <b-form-textarea
          id="textarea"
          v-model="form.text"
          placeholder="Your text goes here"
          rows="3"
          max-rows="6"
        />
        <b-form-invalid-feedback :state="formFeedback.textValid">
          {{ formFeedback.textErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>
      <b-button type="submit" variant="success">Submit</b-button>

      <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">
      </AlertDangerForm>

      <AlertSuccessForm msg="Success!" :show="created"/>

    </b-form>
  </div>
</template>

<script>
import Api from '@/service/api';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import AlertSuccessForm from '@/components/AlertSuccessForm.vue';
import { parseErrorsForm } from '@/service/errors';
import {
  BForm, BFormGroup, BFormInvalidFeedback, BFormTextarea, BButton,
} from 'bootstrap-vue';

export default {
  name: 'ThreadDetailForm',
  components: {
    AlertSuccessForm,
    AlertDangerForm,
    BForm,
    BFormGroup,
    BFormInvalidFeedback,
    BFormTextarea,
    BButton,
  },
  data() {
    return {

      countryCode: 'US',
      form: {
        text: '',

      },

      formFeedback: {
        textValid: true,
        textErrMsg: '',
        isValid: true,
        errMessage: '',
      },
      created: false,

    };
  },
  methods: {
    onSubmit(evt) {
      evt.preventDefault();

      const { text } = this.form;

      const { threadId } = this.$route.params;

      const data = { text, thread_id: threadId };

      let url = Api.thread(threadId, 0, 0);

      const { id } = this.$route.params;

      // If the id is undefined the ThreadDetail component gets accessed
      // from a fond forum.
      // TODO (Dario): id is misleading. Adjust the param to have the name fondID.
      // Comment has been copied from ThreadDetail.vue
      if (id !== undefined) {
        url = Api.fondThread(this.$route.params.id, threadId, 0, 0);
      }

      this.$http.post(url, data).then(() => {
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
