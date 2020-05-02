<template>
  <div>
    <div v-if="subject === null">Loading...</div>
    <div v-else>
      <Headline :name="subject"/>
      <small>Started: {{started}}</small>


      <b-col
        v-for="m in msgs" v-bind:key="m.id" sm="8"
        :offset-sm="user_id === m.sender.id ? '4' : '0'"
        :align-self="user_id === m.sender.id ? 'start' : 'end'"
      >
        <span class="card card-body bg-light msg">
          <router-link :to="{name: 'profile', params: {id: m.sender.id}}">
            {{m.sender.username}}:
          </router-link>
          <hr>
          <Marked :markdown="m.text"></Marked>
        </span>
      </b-col>

      <b-pagination v-model="page"
                    :total-rows="total"
                    :per-page="size"
                    align="right"
      />

      <MessageReplyForm @replySuccessful="getMessages" :conversationId="conversationId">

      </MessageReplyForm>

    </div>
  </div>
</template>

<script>
import Api from '@/service/api';
import Headline from '@/components/Headline.vue';
import MessageReplyForm from '@/components/social/MessageReplyForm.vue';
import Service from '@/service/service';
import Marked from '@/components/Marked';
import { BCol, BPagination } from 'bootstrap-vue';

/**
   * Displays a single message.
   *
   */
export default {
  name: 'MessageDetail',
  components: {
    MessageReplyForm, Headline, BCol, BPagination, Marked,
  },
  data() {
    return {

      user_id: Service.getCompany().user_id,
      conversationId: this.$route.params.id,
      subject: null,
      started: null,
      msgs: [],

      isBusy: false,
      page: 1,
      size: 10,
      total: 0,

    };
  },
  methods: {
    getMessages() {
      this.$http.get(Api.messageDetail(this.conversationId, this.page, this.size)).then((r) => {
        const { results } = r.data;
        const { conversation } = r.data;

        this.subject = conversation.subject;
        this.started = conversation.created;
        this.msgs = results;
        this.total = r.data.count;
      });
    },
  },
  mounted() {
    this.getMessages();
  },
  watch: {
    page() {
      this.getMessages();
    },
  },
};
</script>

<style scoped>
  .msg {
    margin-top: 10px;
  }


</style>
