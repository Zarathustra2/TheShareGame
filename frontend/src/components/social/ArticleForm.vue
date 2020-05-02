<template>
  <div>
    <p class="font-weight-light font-italic">
        For formatting your articles you can use Markdown.
        Here is a great
        <a
          href="https://guides.github.com/features/mastering-markdown/"
          target="_blank"
        >article</a>
        about markdown by github.
      </p>
    <b-row>

      <b-col>
        <b-form @submit="onSubmit">

          <b-form-group
            id="headline"
            label="Headline"
            description="Headline of the article"
          >
            <b-form-input
              id="headline-input"
              v-model="form.headline"
              required
              size="sm"
            />
            <b-form-invalid-feedback :state="formFeedback.headlineValid">
              {{ formFeedback.headlineErrMsg }}
            </b-form-invalid-feedback>
          </b-form-group>

          <b-form-group
            id="text"
            label="Text"
            description="Write about your company's strategy or about the market"
          >
            <b-form-textarea
              id="textarea"
              v-model="form.text"
              placeholder="Enter your article"
              rows="15"
              max-rows="25"
            >

            </b-form-textarea>
            <b-form-invalid-feedback :state="formFeedback.textValid">
              {{ formFeedback.textErrMsg }}
            </b-form-invalid-feedback>
          </b-form-group>

          <b-button type="submit" variant="success" id="submitArticleButton">Submit</b-button>

          <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">
          </AlertDangerForm>
          <AlertSuccessForm :show="showSuccess" :msg="successMsg"/>

        </b-form>
      </b-col>
      <b-col>
        Preview:
        <div class="card card-body bg-light" id="preview">
          <Marked :markdown="form.text"/>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script>

import Marked from '@/components/Marked';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Api from '@/service/api';
import AlertSuccessForm from '@/components/AlertSuccessForm.vue';
import Service from '@/service/service';
import { parseErrorsForm } from '@/service/errors';
import {
  BCol, BRow, BForm, BButton, BFormGroup, BFormTextarea, BFormInvalidFeedback, BFormInput,
} from 'bootstrap-vue';

export default {
  name: 'ArticleForm',
  components: {
    AlertSuccessForm,
    AlertDangerForm,
    Marked,
    BCol,
    BRow,
    BForm,
    BButton,
    BFormGroup,
    BFormTextarea,
    BFormInvalidFeedback,
    BFormInput,
  },
  data() {
    return {
      form: {
        text: '',
        headline: '',
      },

      formFeedback: {

        headlineValid: true,
        headlineErrMsg: '',

        textValid: true,
        textErrMsg: '',

        isValid: true,
        errMessage: '',
      },

      showSuccess: false,
      successMsg: '',
    };
  },

  methods: {
    onSubmit(evt) {
      evt.preventDefault();

      const { text, headline } = this.form;
      const { id } = Service.getCompany();

      const data = { text, headline, company_id: id };

      const url = Api.articles(1, 10);

      this.$http.post(url, data).then(() => {
        this.successMsg = 'Your article has been submitted. An admin will review it in the next hours!';
        this.showSuccess = true;
        this.resetForm();
      }).catch((e) => {
        parseErrorsForm(this, e.response.data);
      });
    },

    resetForm() {
      this.form.text = '';
      this.form.headline = '';
    },
  },
};
</script>

<style scoped>

</style>
