<template>
  <div>
    <Headline name="Notifications"/>
    <list :getData="getCompanies" :slots="templates" :childFields="fields">

      <template slot="read" slot-scope="data">
        <div id="read">
          <span v-if="data.tbl.value" class="fas fa-check text-success"/>
          <span v-else class="fas fa-envelope text-danger"/>
        </div>
      </template>

      <template slot="subject" slot-scope="data">
        <router-link :to="{name: 'notificationDetail', params: {id: data.tbl.item.id}}">
          {{data.tbl.value}}
        </router-link>
      </template>

    </list>

  </div>
</template>

<script>

import List from '@/components/List.vue';
import Api from '@/service/api';
import { Table } from '@/service/utils';
import Headline from '@/components/Headline.vue';

export default {
  name: 'Notifications',
  components: { Headline, List },
  data() {
    return {
      templates: [
        { name: 'read', field: 'read' },
        { name: 'subject', field: 'subject' },
      ],
      fields: [
        {
          key: 'read', label: 'Read', sortable: true, sortDirection: 'desc',
        }, {
          key: 'subject',
          label: 'Subject',
          sortable: true,
          sortDirection: 'desc',
          class: 'subject',
        },
        {
          key: 'created',
          label: 'Received',
          sortable: true,
          sortDirection: 'desc',
          class: 'received',
        },

      ],
    };
  },
  methods: {
    getCompanies(c) {
      return Table.getTableData({
        url: Api.notifications, component: c, page: c.page, size: c.size,
      });
    },
  },
};
</script>
