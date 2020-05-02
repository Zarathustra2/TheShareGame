<template>
  <div>
    <Headline name="Companies"/>
    <p class="font-weight-light font-italic">
      All companies that are currently active and registered.
    </p>
    <list :getData="getCompanies" :slots="templates" :childFields="fields" id="companies">
      <template slot="name" slot-scope="data">
        <router-link :to="{name: 'company', params: {isin: data.tbl.item.isin}}">
          {{data.tbl.value}}
        </router-link>
      </template>

    </list>


  </div>
</template>

<script>

import List from '@/components/List.vue';
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';
import { Table } from '@/service/utils';

export default {
  name: 'Companies',
  components: { Headline, List },
  data() {
    return {
      templates: [
        { name: 'name', field: 'name' },
      ],
      fields: [
        {
          key: 'isin', label: 'Isin', sortable: true, sortDirection: 'desc', class: 'isin',
        },
        {
          key: 'name', label: 'Name', sortable: true, sortDirection: 'desc', class: 'name',
        },
        {
          key: 'user.username', label: 'Ceo', sortable: true, sortDirection: 'desc', class: 'ceo',
        },
      ],
    };
  },
  methods: {
    getCompanies(c, ctx) {
      Table.getTableData({
        url: Api.companies, component: c, page: c.page, size: c.size, ctx,
      });
    },
  },
};
</script>
