<template>
  <div>

    <Headline name="Messages"/>
    <p class="font-weight-light font-italic">
      In the Messages view one can view the most recent conversations with other users or
      start a new conversation with an another CEO.
    </p>

    <b-nav tabs class="msg-tabs">
      <b-nav-item :active="!newMsgTab()" :disabled="!newMsgTab()" v-on:click="tabClick">
        Messages
      </b-nav-item>
      <b-nav-item :active="newMsgTab()" :disabled="newMsgTab()" v-on:click="tabClick">
        Write new Message
      </b-nav-item>
    </b-nav>

    <list
      v-if="!newMsgTab()"
      :getData="getMessages"
      :slots="templates"
      :childFields="fields"
      ref="table"
    >
      <template slot="subject" slot-scope="data">
        <router-link :to="{name: 'messageDetail', params: {id: data.tbl.item.id}}">
          {{data.tbl.value}}
        </router-link>
      </template>

      <template slot="read" slot-scope="data">
        <div id="read">
          <span v-if="data.tbl.value" class="fas fa-check text-success"/>
          <span v-else class="fas fa-envelope text-danger"/>
        </div>
      </template>

    </list>

    <div v-else class="new-message">
      <h3>Write a new Message!</h3>
      <b-col sm="12">
        <MessageForm @forceReload="reloadList"/>
      </b-col>
    </div>

  </div>
</template>

<script>

import List from '@/components/List.vue';
import { Table } from '@/service/utils';
import Api from '@/service/api';
import MessageForm from '@/components/social/MessageForm.vue';
import Headline from '@/components/Headline.vue';
import { BCol } from 'bootstrap-vue';

/**
   * Displays all messages of the user. Users can create new messages with multiple
   * other users.
   *
   */
export default {
  name: 'MessagesList',
  components: {
    MessageForm, List, Headline, BCol,
  },
  data() {
    return {
      templates: [
        {
          name: 'subject',
          field: 'subject',
        },
        {
          name: 'read',
          field: 'read',
        },
      ],
      fields: [
        {
          key: 'read', label: 'Read', sortable: true, sortDirection: 'desc', class: 'read',
        },
        {
          key: 'subject',
          label: 'Subject',
          sortable: true,
          sortDirection: 'desc',
          class: 'subject',
        },
        {
          key: 'created',
          label: 'Date',
          sortable: true,
          sortDirection: 'desc',
          class: 'lastMessage',
        },

      ],
      activeTab: 'messages',
    };
  },
  methods: {
    getMessages(c) {
      return Table.getTableData({
        url: Api.messages, component: c, page: c.page, size: c.size,
      });
    },
    reloadList(bool) {
      if (bool) this.$refs.table.getExternalData();
    },
    newMsgTab() {
      return this.activeTab !== 'messages';
    },
    tabClick(e) {
      e.preventDefault();
      if (this.newMsgTab()) {
        this.activeTab = 'messages';
      } else {
        this.activeTab = 'new-msg';
      }
    },
  },
};
</script>

<style scoped>
  .new-message {
    margin-top: 35px;
  }
</style>
