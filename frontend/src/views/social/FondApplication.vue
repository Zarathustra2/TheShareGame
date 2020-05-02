<template>
  <div>
    <Headline name="Application Fond"/>
    <div v-if="hasFond">
      You are already in a fond! You cannot apply to other fonds before you leave your current fond!
    </div>
    <div v-else-if="this.fond === null">
      Loading...
    </div>
    <div v-else>
      You are currently applying at <span class="text-success">{{fond.name}}</span>!
      <hr>
      <b-form @submit="onSubmit">
        <b-form-group
          id="text"
          label="Text"
          description="Write why the fond should take you"
        >
          <b-form-textarea
            id="textarea"
            v-model="form.text"
            placeholder="Your Application"
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

      </b-form>
    </div>

  </div>

</template>

<script>
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import {
  BForm, BFormGroup, BFormTextarea, BFormInvalidFeedback, BButton,
} from 'bootstrap-vue';

export default {
  name: 'FondApplication',
  components: {
    Headline, AlertDangerForm, BForm, BFormGroup, BFormTextarea, BFormInvalidFeedback, BButton,
  },
  data() {
    return {
      form: {
        text: '',
      },
      formFeedback: {
        textErrMsg: '',
        textValid: true,
        isValid: true,
        errMessage: '',
      },
      fond: null,
    };
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();

      const data = {
        text: this.form.text,

        // eslint-disable-next-line
          fond_id: this.fond.id
      };

      resetFormErrors(this);

      this.$http.post(Api.fondApplication(this.fond.id, 0, 0), data).then(() => {
        this.$bvToast.toast(`Your application to ${this.fond.name} has been submitted`, {
          title: 'Success',
          autoHideDelay: 5000,
          appendToast: false,
          variant: 'success',
        });
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
  created() {
    this.$http.get(Api.fondSlim(this.$route.params.id)).then((r) => {
      const { data } = r;
      this.fond = data;
    });
  },
};
</script>

<style scoped>

</style>
