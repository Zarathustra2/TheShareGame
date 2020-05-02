<template>
  <div>
    <ThreadsList :get-threads="getThreads" ref="tableList"/>
    <ThreadForm @forceReload="reloadList" :url="threadFormUrl"/>
  </div>

</template>

<script>

import ThreadsList from '@/components/social/ThreadsList.vue';
import ThreadForm from '@/components/social/ThreadForm.vue';
import Api from '@/service/api';
import { Table } from '@/service/utils';


export default {
  name: 'FondForum',
  components: { ThreadsList, ThreadForm },
  methods: {
    getThreads(c) {
      const url = (page, size) => Api.fondThreads(this.$route.params.id, page, size);
      return Table.getTableData({
        url, component: c, page: c.page, size: c.size,
      });
    },
    reloadList(bool) {
      if (bool) {
        this.$refs.tableList.$refs.table.getExternalData();
      }
    },
  },
  computed: {
    threadFormUrl() {
      return Api.fondThreads(this.$route.params.id, 1, 10);
    },
  },
};
</script>

<style scoped>

</style>
