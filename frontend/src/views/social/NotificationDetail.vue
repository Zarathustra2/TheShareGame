<template>
  <div v-if="subject === null">Loading...</div>
  <div v-else>
    <Headline :name="subject"/>

    <div class="card card-body bg-light" id="text">
      {{ text }}
    </div>
    <small id="date">Received: {{ date }}</small>
  </div>
</template>

<script>
import Headline from '@/components/Headline.vue';
import Api from '@/service/api';

export default {
  name: 'NotificationDetail',
  components: { Headline },
  data() {
    return {
      subject: null,
      text: null,
      extra: null,
      date: null,
    };
  },
  methods: {
    getNotification() {
      const { id } = this.$route.params;
      this.$http.get(Api.notificationDetail(id)).then((r) => {
        const { data } = r;
        this.text = data.text;
        this.subject = data.subject;
        this.date = data.created;
      }).catch((err) => {
        console.error(err);
      });
    },
  },
  mounted() {
    this.getNotification();
  },
};
</script>

<style scoped>

</style>
