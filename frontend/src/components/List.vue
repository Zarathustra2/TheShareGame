<template>
  <div>
    <b-table
      :id="id"
      :hover="true"
      :striped="true"
      :small="true"
      :items="items"
      :busy.sync="isBusy"
      :fields="fields"
      @sort-changed="sortingChanged"
    >
      <template v-slot:[`cell(${slot.field})`]="row" v-for="slot in slots">
        <slot :name="slot.name" :tbl="row"/>
      </template>
    </b-table>

    <b-pagination v-model="page"
                  :total-rows="total"
                  :per-page="size"
                  align="right"
    />

  </div>
</template>

<script>

import { BPagination, BTable } from 'bootstrap-vue';

export default {
  components: { BPagination, BTable },
  props: {
    getData: Function,
    slots: Array,
    childFields: Array,
    id: String,
  },
  data() {
    return {
      isBusy: false,
      page: 1,
      size: 10,
      total: 0,
      fields: [],
      items: [],
    };
  },
  mounted() {
    this.fields = this.childFields;
    this.getExternalData();
  },

  // extra method so parent components can call it
  // to refresh the table
  methods: {
    getExternalData() {
      this.getData(this);
    },
    sortingChanged(ctx) {
      this.getData(this, ctx);
    },
  },

  watch: {
    page: {
      handler() {
        this.getExternalData();
      },
    },
  },
};
</script>
