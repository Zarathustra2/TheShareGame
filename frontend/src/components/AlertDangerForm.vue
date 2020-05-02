<template>
  <b-row class="justify-content-md-center">
    <b-alert show variant="danger"
             v-if="isValid !== null && !isValid">{{ errMessage }}
    </b-alert>
  </b-row>
</template>

<script>

import { BRow, BAlert } from 'bootstrap-vue';

export default {
  name: 'AlertDangerForm',
  components: {
    BRow, BAlert,
  },
  props: ['isValid', 'errMessage'],
};
</script>

<style scoped>

</style>
