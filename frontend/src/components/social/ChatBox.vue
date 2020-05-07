<template>
  <div>
    <div id="msg-list-div" class="card-body">
      <div id="msg-list" class="list-group">

        <li v-for="m in messages" class="msg" v-bind:key="m.id">
          [{{m.time}}
          <router-link class="text-success"
                       :to="{name: 'profile', params: {id: m.user.id}}">
            {{m.user.username}}</router-link>]: {{m.message}}
        </li>

      </div>

    </div>
    <b-form v-on:submit="send">
      <b-input-group>

        <b-input-group-prepend>
          <b-button variant="primary" v-on:click="send" class="msg-btn">Send</b-button>
        </b-input-group-prepend>

        <b-form-input
          id="chat-msg"
          v-model="form.msg"
          required
          placeholder="Say hello to the world!"
          :state="msgValid"
        />

        <b-form-invalid-feedback id="input-live-feedback">
          Message must be shorter than 100 chars
        </b-form-invalid-feedback>

      </b-input-group>
    </b-form>

  </div>

</template>

<script>
import Service from '@/service/service';
import {
  BButton, BForm, BFormInvalidFeedback, BFormInput, BInputGroup,
} from 'bootstrap-vue';

export default {
  name: 'ChatBox',
  components: {
    BButton,
    BForm,
    BFormInvalidFeedback,
    BFormInput,
    BInputGroup,
  },
  props: ['amount'],
  data() {
    return {
      authenticated: Service.isAuthenticated(),
      form: {
        msg: '',
      },
    };
  },

  methods: {
    send(evt) {
      evt.preventDefault();
      if (!this.authenticated) {
        this.$bvToast.toast('Cannot send chat msg without logging in to your account!', {
          title: 'Error!',
          autoHideDelay: 5000,
          appendToast: false,
          variant: 'danger',
        });

        return;
      }

      const data = {
        message: this.form.msg,
      };

      if (data.message === '') {
        console.log('Message is empty!');
        return;
      }

      this.$store.commit('sendChatMsg', data);
      this.form.msg = '';
    },

  },

  created() {
    this.$store.commit('setMaxMsg', this.amount || 10);
  },

  computed: {
    messages() {
      return this.$store.getters.getMsg;
    },
    msgValid() {
      return this.form.msg.length <= 100;
    },
  },

};
</script>

<style scoped>

  .msg {
    list-style-type: none;
  }

</style>
