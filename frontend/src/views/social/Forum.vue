<template>
  <div>
    <Headline name="Forum"/>
    <p class="font-weight-light font-italic">
      In the forum you can discuss about all sort of topics. In the
      <a href="/forum/thread/official-news/1">Official News</a> thread you can read
      about the most current updates in the game. If you do not find any thread related
      to the topic you wish to talk about, feel free to create a new thread!
    </p>
    <div>

      <ThreadsList :get-threads="getThreads" ref="tableList"/>

    </div>
    <ThreadForm @forceReload="reloadList" :url="threadFormUrl"/>
  </div>

</template>

<script>
import Headline from '@/components/Headline.vue';
import ThreadForm from '@/components/social/ThreadForm.vue';
import ThreadsList from '@/components/social/ThreadsList.vue';
import Api from '@/service/api';
import { Table } from '@/service/utils';


export default {
  name: 'Forum',
  components: { ThreadsList, ThreadForm, Headline },

  methods: {
    getThreads(c) {
      const url = (page, size) => Api.threads(page, size);
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
      return Api.threads(1, 10);
    },
  },
};
</script>

<style scoped>

</style>
