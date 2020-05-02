<template>
  <div>
    <CompanyBreadCrumb active="Articles" :companyName="name" v-bind:key="name" />
    <p class="font-weight-light font-italic">
      Int the CompanyArticles view one can view the most recent articles written by this company.
    </p>
    <Articles :url="url"/>
  </div>
</template>

<script>
import Api from '@/service/api';
import Articles from '@/components/social/Articles.vue';
import CompanyBreadCrumb from '@/components/CompanyBreadCrumb.vue';

/**
 * Renders all articles written by this company.
 */
export default {
  name: 'CompanyArticles',
  components: { CompanyBreadCrumb, Articles },
  props: ['companyName'],
  data() {
    return {
      url: (page, size) => Api.articlesCompany(this.$route.params.isin, page, size),
      name: this.companyName,
    };
  },
  mounted() {
    // If this view is accessed over the company view, then the company name is the defined
    // If it is accessed directly, then the name is not defined, hence we have to fetch it.
    if (this.name !== undefined) {
      return;
    }

    console.log('companyNameProps is undefined, fetching name');

    this.$http.get(Api.company(this.$route.params.isin)).then((r) => {
      this.name = r.data.name;
    });
  },
};
</script>

<style scoped>

</style>
