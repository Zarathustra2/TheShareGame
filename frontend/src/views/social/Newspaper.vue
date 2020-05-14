<template>
  <div>

    <Headline name="Newspaper"/>

    <b-nav tabs class="newspaper-tabs" v-show="loggedIn">
      <b-nav-item :active="!isEdit()" :disabled="!isEdit()" v-on:click="tabClick">
        Articles
      </b-nav-item>
      <b-nav-item :active="isEdit()" :disabled="isEdit()" v-on:click="tabClick">
        Submit new Article
      </b-nav-item>
    </b-nav>


    <p class="font-weight-light font-italic" style="margin-top: 10px">
    In the newspaper one can read about the strategies of other companies. CEO's can submit
    articles which then get published by the admins with in the next 8 hours. You may want to
    write about your trading strategy, introduce yourself or
    even inform others about a related topic.
    </p>
    <div v-if="activeTab !== 'articles' && loggedIn">
      <hr>
      <ArticleForm id="articleForm"/>
    </div>

    <div v-else>
      <Articles :url="url"/>

      <b-pagination
        v-model="page"
        :total-rows="total"
        :per-page="size"
        align="right"
        >
      </b-pagination>
    </div>


  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';
import Articles from '@/components/social/Articles.vue';
import ArticleForm from '@/components/social/ArticleForm.vue';
import Service from '@/service/service';
import { BPagination } from 'bootstrap-vue';

export default {
  name: 'Newspaper',
  components: {
    ArticleForm, Articles, Headline, BPagination,
  },
  data() {
    return {
      articles: [],
      page: 1,
      size: 6,
      total: 0,
      loggedIn: Service.isAuthenticated(),
      url: (page, size) => Api.articles(page, size),
      activeTab: 'articles',
    };
  },
  methods: {
    isEdit() {
      return this.activeTab === 'newArticle';
    },
    tabClick(e) {
      e.preventDefault();
      if (this.activeTab === 'newArticle') {
        this.activeTab = 'articles';
      } else {
        this.activeTab = 'newArticle';
      }
    },
  },

};
</script>

<style scoped>
  #articleForm {
    margin-top: 50px;
  }
</style>
