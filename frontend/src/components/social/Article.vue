<template>
  <div class="article">
      <b-card
        footer-tag="footer"
        footer-border-variant="dark"
        :title="headline"
      >

        <b-card-text class="text">
          <Marked :markdown="text"></Marked>
        </b-card-text>

        <template v-slot:footer>

          <em>
            <router-link :to="{name: 'company', params: {isin: author.isin}}" class="author">
              {{author.name}}
            </router-link>
          </em>

          written on: <span class="dateTime">{{ dateTime }}</span>

        </template>
      </b-card>
  </div>
</template>

<script>
import Marked from '@/components/Marked';
import { BCard, BCardText } from 'bootstrap-vue';

export default {
  components: { BCard, BCardText, Marked },
  name: 'Article',
  props: ['headline', 'text', 'author', 'dateTime'],

};
</script>

<style scoped>

  .article {
    margin-top: 15px;
  }

</style>
