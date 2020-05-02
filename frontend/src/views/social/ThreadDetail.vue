<template>

  <div v-if="!posts">
    <h1>Loading data...</h1>
  </div>

  <div v-else>
    <Headline :name="name"/>

    <b-row v-for="p in posts" v-bind:key="p.id">

      <b-col class="post">
        <b-card
         footer-tag="footer"
         footer-border-variant="dark"
        >
          <b-card-text class="text">
            {{p.text}}
          </b-card-text>

          <template v-slot:footer>

            <em class="author" v-if="p.user !== null">
              {{p.user.username}}
            </em>

            <br/>

            Date: <span class="dateTime">{{ p.date_time }}</span>

          </template>
        </b-card>
      </b-col>


    </b-row>

    <hr>

    <ThreadDetailForm @forceReload="getData"/>

    <b-pagination
      v-model="page"
      :total-rows="total"
      :per-page="size"
      align="right"
    />
  </div>

</template>

<script>
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';
import ThreadDetailForm from '@/components/social/ThreadDetailForm.vue';
import {
  BRow, BCol, BPagination, BCardText, BCard,
} from 'bootstrap-vue';

export default {
  name: 'ThreadDetail',
  components: {
    ThreadDetailForm, Headline, BRow, BCol, BPagination, BCardText, BCard,
  },
  data() {
    return {

      id: this.$route.params.threadId,
      slug: this.$route.params.slug,

      posts: [],

      page: 1,
      size: 10,
      total: 0,
    };
  },
  mounted() {
    this.getData();
  },

  methods: {
    getData() {
      let url = Api.thread(this.id, this.page, this.size);

      const { id } = this.$route.params;

      // If the id is undefined the ThreadDetail component gets accessed
      // from a fond forum.
      // TODO (Dario): id is misleading. Adjust the param to have the name fondID.
      if (id !== undefined) {
        url = Api.fondThread(this.$route.params.id, this.id, this.page, this.size);
      }

      this.$http.get(url).then((r) => {
        const { data } = r;
        this.total = data.count;
        this.posts = data.results;
        this.posts.reverse();
      });
    },
  },

  computed: {
    name() {
      const s = this.slug.replace('-', ' ');
      return s.charAt(0).toUpperCase() + s.slice(1);
    },
  },
  watch: {
    page: {
      handler() {
        this.getData();
      },
    },
  },
};
</script>

<style scoped>

  .post {
    margin-bottom: 5px;
  }

</style>
