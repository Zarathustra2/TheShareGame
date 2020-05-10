<template>
  <div>
    <Headline name="Bonds"/>
    <p class="font-weight-light font-italic">
      One can buy bonds here. The basic principe of a bond:
      <ul>
        <li>Your company lends the system money for x days</li>
        <li>After x days you will get your money guaranteed back plus rates</li>
      </ul>
      So if you invest in bonds you cannot lose money. Effectively bonds are inflating the system
      as the system gives each company more money back than it get previously from it.
      The rate is based on how many companies have invested in bonds:
      The more company invest in bonds, the lower the rate.
    </p>
    <BondsRateChart/>

    <hr>
    <h1>Buy Bonds</h1>

    <div v-if="isAuthenticated">

      <b-row>
        <b-col cols="6">
          <b-form @submit.prevent="submit">

            <b-form-group
              label="Value:"
              label-for="value"
              description="The Value of a single bond you would like to buy"
            >
              <b-form-input
                id="input-1"
                v-model="form.value"
                required
                placeholder="100000"
                ref="valueInput"
              />
              <b-form-invalid-feedback :state="formFeedback.valueValid">
                {{ formFeedback.valueErrMsg }}
              </b-form-invalid-feedback>
            </b-form-group>

            <b-form-group label="Amount" label-for="amount"
                          description="The amount of the bonds you would like to buy"
            >
              <b-form-select
                v-model="form.amount"
                :options="amountOption"
                required
                ref="amountInput"
              />
              <b-form-invalid-feedback :state="formFeedback.amountValid">
                {{ formFeedback.amountErrMsg }}
              </b-form-invalid-feedback>
            </b-form-group>

            <b-form-group label="Runtime" label-for="runtime"
                          description="The runtime in days for the bonds"
            >
              <b-form-select
                v-model="form.runtime"
                :options="runtimeOption"
                required
                ref="runtimeInput"
              />
              <b-form-invalid-feedback :state="formFeedback.runtimeValid">
                {{ formFeedback.runtimeErrMsg }}
              </b-form-invalid-feedback>
            </b-form-group>

            <AlertDangerForm :isValid="formFeedback.isValid" :errMessage="formFeedback.errMessage">
            </AlertDangerForm>

            <b-button variant="primary" type="submit" class="buttonBond">Submit</b-button>
          </b-form>
        </b-col>
        <b-col cols="6">
          <LiquidityOverview/>
        </b-col>
      </b-row>

    </div>

    <div v-else>
      You need an account to buy bonds!
    </div>

  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import AlertDangerForm from '@/components/AlertDangerForm.vue';
import BondsRateChart from '@/components/charts/BondsRateChart.vue';
import LiquidityOverview from '@/components/company/LiquidityOverview.vue';
import Service from '@/service/service';
import { parseErrorsForm, resetFormErrors } from '@/service/errors';
import Api from '@/service/api';
import { Number } from '@/service/utils';
import {
  BFormGroup, BButton, BFormInput, BForm, BFormSelect, BFormInvalidFeedback, BRow, BCol,
} from 'bootstrap-vue';

/**
 * Renders the rate of the bond chart and a bond form.
 * The form allows users to buy now bonds with the current rate.
 */
export default {
  name: 'Bonds',
  components: {
    AlertDangerForm,
    BondsRateChart,
    Headline,
    BFormGroup,
    BButton,
    BFormInput,
    BForm,
    BFormSelect,
    BFormInvalidFeedback,
    LiquidityOverview,
    BRow,
    BCol,
  },
  data() {
    return {
      isAuthenticated: Service.isAuthenticated(),
      form: {
        value: 100000,
        amount: 1,
        runtime: 1,
      },
      formFeedback: {
        valueValid: true,
        valueErrMsg: '',
        amountValid: true,
        amountErrMsg: '',
        runtimeValid: true,
        runtimeErrMsg: '',
        isValid: true,
        errMessage: '',
      },
      amountOption: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
      runtimeOption: [1, 2, 3],
    };
  },
  methods: {
    submit() {
      const data = {
        value: this.form.value,
        amount: this.form.amount,
        runtime: this.form.runtime,
      };

      resetFormErrors(this);

      const { isin } = Service.getCompany();

      this.$http.post(Api.bondsCompany(isin, 0, 0), data)
        .then(() => {
          this.showToast();
        })
        .catch((e) => {
          parseErrorsForm(this, e.response.data);
        });
    },

    showToast() {
      const h = this.$createElement;

      const msg = h(
        'ul',
        { class: ['', 'mb-0'] },
        [
          h('li', `Value per Bond: ${Number.formatNumber(this.form.value)}$`),
          h('li', `Amount: ${this.form.amount}`),
          h('li', `Total value: ${Number.formatNumber(this.form.amount * this.form.value)}$`),
          h('li', `Runtime: ${this.form.runtime} day`),
        ],
      );

      let title = '1 bond has been bought!';
      if (this.form.amount > 1) {
        title = `${this.form.amount} bonds have been bought!`;
      }

      this.$bvToast.toast([msg], {
        title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: 'primary',
      });
    },

  },

};

</script>

<style scoped>

</style>
