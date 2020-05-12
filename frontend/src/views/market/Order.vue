<template>
  <div>
    <Headline name="Place Order"></Headline>
     <p class="font-weight-light font-italic">
      Orders are the heart of the game. You can either place a buy or a sell order for a
       company. Of course, you can only place a sell order, if you have the shares in your depot.
       <br>
       Requirements for a buy order is that you have enough money.
    </p>
    <hr>
    <b-row>
      <b-col>
        <b-form @submit.prevent="onSubmit">

      <b-form-group
        label="ISIN:"
        description="The isin of the company you would like to place an order"
      >
        <b-form-input
          id="input-1"
          v-model="form.isin"
          required
          placeholder="isin"
          :state="formFeedback.isinValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.isinValid">
          {{ formFeedback.isinErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        label="Price:"
        description="The price per share"
      >
        <b-form-input
          id="input-2"
          v-model="form.price"
          required
          placeholder="price"
          :state="formFeedback.priceValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.priceValid">
          {{ formFeedback.priceErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        label="Amount:"
        description="The amount of shares"
      >
        <b-form-input
          id="input-3"
          v-model="form.amount"
          required
          placeholder="amount"
          :state="formFeedback.amountValid"
        ></b-form-input>
        <b-form-invalid-feedback :state="formFeedback.amountValid">
          {{ formFeedback.amountErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <b-form-group
        label="Typ:"
        description="The typ of the order: Buy/Sell"
      >
        <b-form-select
          id="input-4"
          v-model="form.typ"
          required
          :options="form.typOptions"
          :state="formFeedback.typValid"
        ></b-form-select>
        <b-form-invalid-feedback :state="formFeedback.typValid">
          {{ formFeedback.typErrMsg }}
        </b-form-invalid-feedback>
      </b-form-group>

      <AlertDangerForm :isValid="this.formFeedback.isValid"
      :errMessage="this.formFeedback.errMessage"></AlertDangerForm>

      <b-button variant="primary" type="submit" class="submit-btn">Submit</b-button>
    </b-form>
      </b-col>
      <b-col>
        <LiqudityOverview/>
      </b-col>
    </b-row>

  </div>
</template>

<script>
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import Headline from '@/components/Headline.vue';
import LiqudityOverview from '@/components/company/LiquidityOverview.vue';

import Api from '@/service/api';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';

import {
  BForm, BButton, BFormGroup, BFormInvalidFeedback, BFormSelect, BFormInput, BCol, BRow,
} from 'bootstrap-vue';


/**
 * Renders an order form which allows users to create new orders.
 */
export default {
  name: 'Order',
  components: {
    LiqudityOverview,
    Headline,
    AlertDangerForm,
    BForm,
    BButton,
    BFormGroup,
    BFormInvalidFeedback,
    BFormSelect,
    BFormInput,
    BCol,
    BRow,
  },
  data() {
    return {
      form: {
        isin: this.$route.params.isin,
        price: this.$route.query.price || '',
        amount: this.$route.query.amount || '',
        typ: this.$route.query.typ || 'Buy',
        typOptions: ['Buy', 'Sell'],

      },
      formFeedback: {
        isinValid: true,
        isinErrMsg: '',
        priceValid: true,
        priceErrMsg: '',
        amountValid: true,
        amountErrMsg: '',
        typValid: true,
        typErrMsg: '',
        isValid: true,
        errMessage: '',
      },
    };
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();
      resetFormErrors(this);

      const {
        isin, price, amount, typ,
      } = this.form;

      const data = {
        order_of_isin: isin,
        price,
        amount,
        typ,
      };

      const url = Api.orders(0, 0);

      this.$http.post(url, data).then(() => {
        this.showToast();
      }).catch((err) => {
        const fieldMapping = {
          order_of_isin: 'isin',
        };

        parseErrorsForm(this, err.response.data, fieldMapping);
      });
    },
    showToast() {
      this.$bvToast.toast(`Price: ${this.form.price}$,
        Amount: ${this.form.amount},
        Value: ${this.form.amount * this.form.price}$,
        Order of: ${this.form.isin}
      `, {
        title: `${this.form.typ}-Order has been created!`,
        autoHideDelay: 5000,
        appendToast: false,
        variant: 'primary',
        id: 'order-notification',
      });
    },
  },
};
</script>

<style scoped>

</style>
