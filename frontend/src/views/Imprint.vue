<template>
  <div>
    <Headline name="Imprint"></Headline>

    <p>
      According to § 5 of the teleservice regulations, Dario Heinisch as content provider and
      operator
      of this Internet offer is responsible for its own contents provided for use, in terms of the
      general laws and
      regulations. If you wish to get in contact with Dario Heinisch please write to:
    </p>
    <p>
      <span class="text-primary">Dario Heinisch</span><br><span
      class="text-primary">Tauroggener Str. 16</span><br><span
      class="text-primary">10589 Berlin</span><br>
      <span class="text-primary">Germany</span>
    </p>
    <p>
      Responsible for contents in accordance with § 6 of the German Teleservices Act (TDG): Dario
      Heinisch<br>
    </p>
    <h3>Privacy Policy</h3>
    <p>
      <router-link :to="{name: 'dataProtection'}">
        Data protection
      </router-link>
    </p>

    <h3>No liability for contents:</h3>
    <p>
      Dario Heinisch takes great care to ensure the information made available on this Internet
      presence
      is correct and up-to-date. Nevertheless errors and ambiguities cannot be wholly excluded. For
      this reason
      Dario Heinisch accepts no liability for the quality of the information provided nor that this
      will be
      up-to-date, correct or complete. Except in cases of wilful intent or gross negligence Dario
      Heinisch is not liable for any physical or intangible damage arising directly or indirectly
      from the use or
      non-use of the information provided or the use of faulty or incomplete information. The same
      applies to any
      software
      or documentation made available for download free of charge. Dario Heinisch reserves the right
      to
      modify, expand, delete the Internet offer in whole or in part or to discontinue the
      publication temporarily or
      permanently without the need for any special prior notice.
    </p>

    <h3>No liability for third-party contents:</h3>
    <p>
      Liability for “third-party contents” that, for example, are made available directly or
      indirectly through
      connections (so-called links for example) to other providers assumes among other things
      concrete knowledge of
      illegal or criminal content. The same applies to the private websites of our staff. Dario
      Heinisch
      has no control over “third-party contents” nor has it adopted these contents as its own. Dario
      Heinisch has no knowledge of illegal or indecent contents on the pages of third party
      providers with which
      its
      Internet presence has links. However, should the linked pages of third party providers include
      illegal or
      indecent
      contents, Dario Heinisch expressly distances itself from such.
    </p>

    <h3>No consultation:</h3>
    <p>The information made available on the Internet pages in no way constitutes an individual
      consultation nor can it
      replace such. Our staff is at your disposal and would be glad to arrange individual
      consultations.</p>

    <h3>Copyrights / Terms of Use</h3>
    <p>
      The contents, layout, design of the Internet pages, the graphics used as well as any other
      contents of Internet
      pages are protected by copyright. If not otherwise permitted by law, any copying of the pages
      or their contents
      requires the prior written consent of Dario Heinisch.
    </p>
  </div>
</template>

<script>

  import Headline from "@/components/Headline";

  export default {
    name: 'Imprint',
    components: {Headline}
  };
</script>

<style scoped>
</style>
