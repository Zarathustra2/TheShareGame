<template>
   <div>
    <b-table small :fields="fields" :items="shareholders" responsive="sm">

      <template v-slot:cell(index)="data">
        {{ data.index + 1 }}
      </template>

      <template v-slot:cell(depot_of)="data">
        <router-link :to="{name: 'company', params: {isin: data.value.isin}}">
          {{ data.value.name }}
        </router-link>
      </template>

    </b-table>
  </div>
</template>

<script>

import { Number } from '@/service/utils';
import { BTable } from 'bootstrap-vue';

export default {
  name: 'ShareholdersTable',
  props: ['shareholders'],
  components: { BTable },
  data() {
    return {
      fields: [
        { key: 'index', label: '' },
        { key: 'depot_of', label: 'Company', class: 'company' },
        {
          key: 'amount', label: 'Shares', formatter: Number.formatNumber, class: 'amount',
        },
        {
          key: 'value', label: 'Value', formatter: Number.numberWithDollar, class: 'value',
        },
      ],
    };
  },
};
</script>

<style scoped>

</style>
