<template>
  <div>
    <Headline name="Register"/>
    <div v-if="authenticated">You are already logged in</div>
    <div v-else>
      <b>Important: </b>If you have an Github account, please click
      <router-link :to="{name: 'login'}">here</router-link> to register.
      <hr>
      <b-form @submit.prevent="onSubmit">

      <b-form-group
        label="Username:"
        label-for="username"
        description="The name of your account"

      >
        <b-form-input
          id="input-1"
          v-model="form.username"
          required
          placeholder="Username"
          ref="usernameInput"
          :state="formFeedback.usernameValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.usernameValid">
          {{ formFeedback.usernameErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group label="E-mail" label-for="email"
                    description="Your E-Mail used for
                    activating your account and resetting your password"
      >
        <b-form-input
          v-model="form.email"
          required
          type="email"
          ref="emailInput"
          :state="formFeedback.emailValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.emailValid">
          {{ formFeedback.emailErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group label="Password" label-for="password"
                    description="Password used to log into your account"
      >
        <b-form-input
          v-model="form.password"
          required
          type="password"
          ref="passwordInput"
          :state="formFeedback.passwordConfirmValid && formFeedback.passwordValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.passwordValid">
          {{ formFeedback.passwordErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

        <b-form-group label="Confirm Password" label-for="password"
                    description="Confirm your password"
      >
        <b-form-input
          v-model="form.passwordConfirm"
          required
          type="password"
          ref="passwordConfirmInput"
          :state="formFeedback.passwordConfirmValid && formFeedback.passwordValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.passwordConfirmValid">
          {{ formFeedback.passwordConfirmErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

        <vue-recaptcha
                  ref="recaptcha"
                  @verify="register"
                  @expired="onCaptchaExpired"
                  size="invisible"
                  :sitekey="recaptchaSiteKey"
                  :loadRecaptchaScript="true"
        >
                </vue-recaptcha>

        <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage"/>

      <b-button variant="primary" type="submit" class="buttonRegister">Submit</b-button>
    </b-form>

    </div>

  </div>
</template>

<script>
import Service from '@/service/service';
import Headline from '@/components/Headline.vue';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import Api from '@/service/api';
import VueRecaptcha from 'vue-recaptcha';
import {
  BForm, BFormGroup, BFormInput, BFormInvalidFeedback, BButton,
} from 'bootstrap-vue';

export default {
  name: 'Register',
  components: {
    Headline,
    AlertDangerForm,
    VueRecaptcha,
    BForm,
    BFormGroup,
    BFormInput,
    BFormInvalidFeedback,
    BButton,
  },
  data() {
    return {
      recaptchaSiteKey: process.env.VUE_APP_RECAPTCHA_KEY || '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
      form: {
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
      },
      formFeedback: {
        usernameValid: true,
        usernameErrMsg: '',
        emailValid: true,
        emailErrMsg: '',
        passwordValid: true,
        passwordErrMsg: '',
        passwordConfirmValid: true,
        passwordConfirmErrMsg: '',
        isValid: true,
        errMessage: '',
      },

      authenticated: Service.isAuthenticated(),
    };
  },
  created() {
    if (this.recaptchaSiteKey === '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI') {
      console.log('Test captcha will always be true!');
    }
  },
  methods: {
    register(recaptchaToken) {
      resetFormErrors(this);

      if (this.form.password !== this.form.passwordConfirm) {
        this.formFeedback.passwordConfirmValid = false;
        this.formFeedback.passwordConfirmErrMsg = 'Passwords did not match!';
        return;
      }

      const data = {
        username: this.form.username,
        email: this.form.email,
        password: this.form.password,

        // eslint-disable-next-line
        recaptcha_token: recaptchaToken
      };

      this.$http.post(Api.register(), data)
        .then((r) => {
          const { token } = r.data;
          Service.saveToken(token);

          console.log('Token has been saved, now forwarding to foundFirstCompany!');

          this.$router.push({ name: 'foundFirstCompany' });
        })
        .catch((e) => {
          console.error(e);
          parseErrorsForm(this, e.response.data);
        });
    },

    onSubmit() {
      this.$refs.recaptcha.execute();
    },
    onCaptchaExpired() {
      this.$refs.recaptcha.reset();
    },

  },
};
</script>

<style scoped>

</style>
