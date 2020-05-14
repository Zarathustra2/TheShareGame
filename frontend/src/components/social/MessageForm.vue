<template>
  <div>
    <b-form @submit="onSubmit">
      <b-form-group
        id="subject"
        label="Subject"
        description="Subject of the message"
      >
        <b-form-input
          id="subject-input"
          v-model="form.subject"
          required
          size="sm"
        />
        <b-form-invalid-feedback :state="formFeedback.subjectValid">
          {{ formFeedback.subjectErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
      id="receivers"
        label="Receivers"
        description="The users you'd like to message"
        >
        <b-form-tags
          id="receivers-input"
          v-model="form.tags"
          tag-variant="primary"
          tag-pills
          size="lg"
          separator=" "
          placeholder="Enter receivers, use enter to save a receiver"
          class="mb-2"
          :input-attrs="{list: 'receivers-datalist'}"
          :tag-validator="receiverValidator"
          @input.native="updateDatalist($event)"
          invalid-tag-text="No user exists with the name"
        >

        </b-form-tags>
        <b-form-invalid-feedback :state="formFeedback.receiversValid">
          {{ formFeedback.receiversErrMsg }}
        </b-form-invalid-feedback>

        <datalist id="receivers-datalist">
          <option v-for="u in datalist.users" v-bind:key="u.id">{{u.username}}</option>
        </datalist>
      </b-form-group>

      <br>
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

      <b-button type="submit" variant="success">Submit</b-button>

      <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">

      </AlertDangerForm>

    </b-form>
  </div>
</template>

<script>
import Api from '@/service/api';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import {
  BForm, BFormGroup, BButton, BFormTextarea, BFormInvalidFeedback, BFormTags, BFormInput,
} from 'bootstrap-vue';

export default {
  name: 'MessageForm',
  components: {
    AlertDangerForm,
    BForm,
    BFormGroup,
    BButton,
    BFormTextarea,
    BFormInvalidFeedback,
    BFormTags,
    BFormInput,
  },
  data() {
    return {
      form: {
        subject: '',
        tags: [],
        receivers: [],
        text: '',
      },
      formFeedback: {
        subjectValid: true,
        subjectErrMsg: '',
        receiversValid: true,
        receiversErrMsg: '',
        textValid: true,
        textErrMsg: '',
        isValid: true,
        errMessage: '',
      },
      datalist: {
        users: [],
      },
    };
  },
  methods: {

    receiverValidator(tag) {
      return this.datalist.users.some((u) => u.username === tag);
    },

    onSubmit(evt) {
      evt.preventDefault();

      resetFormErrors(this);

      const { subject, receivers, text } = this.form;

      // eslint-disable-next-line
      const receivers_id = receivers.map(obj => obj.id);

      const data = {
        receivers_id,
        subject,
        message_text: text,
      };

      this.$http.post(Api.messages(0, 10), data).then(() => {
        // let the parent component Messages know that the message creation
        // was successful, so it updates the displayed messages
        this.$emit('forceReload', true);
      }).catch((e) => {
        parseErrorsForm(this, e.response.data);
      });
    },

    updateDatalist(event) {
      const explicitOriginalTarget = { event };
      if (explicitOriginalTarget === undefined) {
        return;
      }

      const receiver = explicitOriginalTarget.value;
      if (receiver !== '' && receiver !== null) {
        this.$http.get(Api.userLookup(receiver)).then((r) => {
          this.datalist.users = r.data;
        }).catch((err) => {
          console.error(err);
        });
      }
    },

  },

  watch: {

    /**
     * If a tag get added to the tags, update the receivers list.
     *
     * Respectively if a tag gets deleted from the tags list, delete
     * the receiver also from the receivers list.
     */
    'form.tags': function handler() {
      const { tags, receivers } = this.form;

      if (tags.length > receivers) {
        // A new tag got added.
        // It will be the last element in the list.
        const username = tags[tags.length - 1];
        const { users } = this.datalist;

        for (let i = 0; i < users.length; i++) {
          const u = users[i];
          if (u.username === username) {
            this.form.receivers.push(u);
          }
        }
      } else {
        // A tag got removed
        this.form.receivers = receivers.filter((u) => u.username in tags);
      }
    },

  },

  mounted() {
    const userId = this.$route.query.user_id;

    // If it gets accessed over an url such as /message/1/?user_id=2
    // It means that a user wants to send a message to the user with the id 2,
    // so we retrieve the data for this user and add him to the receivers
    if (userId !== undefined) {
      this.$http.get(Api.user(userId)).then((r) => {
        this.form.receivers.push(r.data);
      }).catch((err) => {
        console.error(err);
      });
    }
  },
};
</script>

<style scoped>
  #receiverButton {
    margin-right: 10px;
  }
</style>
