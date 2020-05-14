<template>
  <div>
    <Headline name="Chat!"></Headline>
    <ChatBox amount=100></ChatBox>
  </div>

</template>

<script>
import Headline from '@/components/Headline.vue';
import ChatBox from '@/components/social/ChatBox.vue';

export default {
  name: 'Chat',
  components: { ChatBox, Headline },
};
</script>

<style scoped>
</style>
