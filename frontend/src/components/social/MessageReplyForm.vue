<template>
  <div>
    <b-form @submit="onSubmit">
      <b-form-group
        id="text"
        label="Text"
        description="The message you'd like to send"
      >
        <b-form-textarea
          id="textarea"
          v-model="form.text"
          placeholder="Enter your message here"
          rows="6"
          max-rows="6"
        >

        </b-form-textarea>
        <b-form-invalid-feedback :state="formFeedback.textValid">
          {{ formFeedback.textErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-button type="submit" variant="success" id="replySubmitButton">Submit</b-button>

      <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">

      </AlertDangerForm>

    </b-form>
  </div>
</template>

<script>

import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Api from '@/service/api';
import { parseErrorsForm } from '@/service/errors';
import {
  BButton, BForm, BFormTextarea, BFormGroup, BFormInvalidFeedback,
} from 'bootstrap-vue';

export default {
  name: 'MessageReplyForm',
  components: {
    AlertDangerForm, BButton, BForm, BFormTextarea, BFormGroup, BFormInvalidFeedback,
  },
  props: ['conversationId'],
  data() {
    return {
      form: {
        text: '',
      },
      formFeedback: {
        isValid: true,
        errMessage: '',
        textValid: true,
        textErrMsg: '',
      },
    };
  },
  methods: {
    onSubmit(evt) {
      evt.preventDefault();

      const data = {
        text: this.form.text,
        conversation_id: this.conversationId,
      };

      this.$http.post(Api.messageDetail(this.conversationId, this.page, this.size), data)
        .then((r) => {
          console.log('Reply successful!', r);
          this.$emit('replySuccessful', true);
          this.resetData();
        }).catch((e) => {
          parseErrorsForm(this, e.response.data);
        });
    },

    resetData() {
      this.form.text = '';
      this.formFeedback = {
        isValid: true,
        errMessage: '',
        textValid: true,
        textErrMsg: '',
      };
    },

  },

};
</script>

<style scoped>

</style>
