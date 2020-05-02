<template>
  <b-breadcrumb class="pb-2 mt-4 mb-2" :items="breadcrumb"/>
</template>

<script>

import { BBreadcrumb } from 'bootstrap-vue';

export default {
  name: 'CompanyBreadCrumb',
  props: ['active', 'companyName'],
  components: { BBreadcrumb },
  data() {
    return {
      breadcrumb: [
        {
          text: this.companyName || 'Company',
          to: { name: 'company', params: { isin: this.$route.params.isin } },
        },
        {
          text: this.active,
          active: true,
        },
      ],
    };
  },
};
</script>

<style scoped>

</style>
