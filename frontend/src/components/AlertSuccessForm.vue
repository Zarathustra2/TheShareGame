<template>
   <b-row class="justify-content-md-center">
    <b-alert show variant="success"
             v-if="show">{{ msg }}
    </b-alert>
  </b-row>
</template>

<script>

import { BRow, BAlert } from 'bootstrap-vue';

export default {
  components: { BRow, BAlert },
  name: 'AlertSuccessForm',
  props: ['show', 'msg'],
};
</script>

<style scoped>

</style>
