<template>
  <b-row>
        <div v-if="articles.length === 0">
          <b-col>No Articles have been written yet!</b-col>
        </div>
        <div v-else>
          <b-col lg="6" v-for="article in articles" v-bind:key="article.id">
          <Article
            :headline="article.headline"
            :text="article.text"
            :author="article.author"
            :dateTime="article.created"
          >
          </Article>
        </b-col>
        </div>
    </b-row>
</template>

<script>
import Article from '@/components/social/Article.vue';
import { BRow, BCol } from 'bootstrap-vue';

export default {
  name: 'Articles',
  components: { Article, BRow, BCol },

  // Url should be a function which accepts two more parameters
  // the page and the size of the page as the articles are paginated
  // by the api
  props: {
    url: Function,
  },
  data() {
    return {
      articles: [],
      page: 1,
      size: 6,
      total: 0,
    };
  },

  beforeMount() {
    this.getData();
  },

  methods: {
    getData() {
      if (this.url === undefined) {
        console.error('Url is undefined!');
        return;
      }

      const url = this.url(this.page, this.size);

      this.$http.get(url).then((r) => {
        const { data } = r;

        this.total = data.count;
        this.articles = data.results;
      });
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

</style>
