<template>
  <list :childFields="fields" :getData="getThreads" :slots="templates" ref="table">
    <template slot="name" slot-scope="data">
      <router-link :to="threadDetailUrl(data.tbl.item.id, data.tbl.item.slug)">
        {{data.tbl.value}}
      </router-link>
    </template>

    <template slot="locked" slot-scope="data">
            <span v-if="data.tbl.value">
              <i class="fas fa-check text-success"/>
            </span>
      <span v-else>
              <i class="fas fa-times text-danger"/>
            </span>
    </template>

    <template slot="pinned" slot-scope="data">
            <span v-if="data.tbl.value">
              <i class="fas fa-check text-success"/>
            </span>
      <span v-else>
              <i class="fas fa-times text-danger"/>
            </span>
    </template>

  </list>
</template>

<script>
import List from '@/components/List.vue';

export default {
  name: 'ThreadsList',
  components: { List },
  props: {
    getThreads: Function,
  },
  data() {
    return {
      templates: [
        {
          name: 'name',
          field: 'name',
        },
        {
          name: 'locked',
          field: 'locked',
        },
        {
          name: 'pinned',
          field: 'pinned',
        },
      ],
      fields: [
        {
          key: 'locked',
          label: 'Locked',
          sortable: true,
          sortDirection: 'desc',
          class: 'locked',
        }, {
          key: 'pinned',
          label: 'Pinned',
          sortable: true,
          sortDirection: 'desc',
          class: 'pinned',
        },
        {
          key: 'name', label: 'Name', sortable: true, sortDirection: 'desc', class: 'name',
        },
      ],
    };
  },
  methods: {
    threadDetailUrl(threadId, slug) {
      const { id } = this.$route.params;

      const params = { threadId, slug };

      // If the id is undefined the ThreadDetail component gets accessed
      // from a fond forum.
      // TODO (Dario): id is misleading. Adjust the param to have the name fondID.
      // Comment has been copied from ThreadDetail.vue
      if (id !== undefined) {
        return this.$router.resolve({
          name: 'threadFond',
          params: {
            id,
            ...params,
          },
        }).href;
      }
      return this.$router.resolve({ name: 'thread', params }).href;
    },
  },
};
</script>

<style scoped>

</style>
