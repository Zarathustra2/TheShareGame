<template>
  <div>
    <header class="masthead text-white text-center">
      <div class="overlay"></div>
      <div class="container">
        <div class="row">
          <div class="col-xl-9 mx-auto">
            <h1 class="mb-5">Sign up now and join tons of other players</h1>
          </div>
          <div class="text-center">
            <div class="row col-lg-12">
              <a href="/register">
                <button type="button" class="btn btn-primary">Register Now!</button>
              </a>

              <a href="/login">
                <button type="button" class="btn btn-primary">Log in</button>
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>

    <section class="features-icons bg-light text-center">
      <div class="container">
        <div class="row">
          <div class="col-lg-4">
            <div class="features-icons-icon d-flex">
              <i class="fa fa-4x fa-building m-auto text-primary"></i>
            </div>
            <h3>Manage your Stock Company</h3>
            <p class="lead mb-0">
              From Marketing, Finance to Investing. You have to do it all
            </p>

          </div>
          <div class="col-lg-4">

            <div class="features-icons-icon d-flex">
              <i class="fa fa-4x fa-handshake m-auto text-primary"/>
            </div>
            <h3>No Pay-To-Win</h3>
            <p class="lead mb-0">
              Money won't help you. Only the smartest will win
            </p>

          </div>
          <div class="col-lg-4">

            <div class="features-icons-icon d-flex">
              <i class="fa fa-4x fa-chart-line m-auto text-primary"/>
            </div>
            <h3>Group up with Players</h3>
            <p class="lead mb-0">
              Chat with others, write newspaper articles or join a fond
            </p>

          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script>
export default {
  name: 'Welcome',
};
</script>

<style scoped>
  body {
    font-family: 'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-family: 'Lato', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-weight: 700;
  }

  header.masthead {
    position: relative;
    background-color: #343a40;
    -webkit-background-size: cover;
    -moz-background-size: cover;
    -o-background-size: cover;
    background-size: cover;
    padding-top: 8rem;
    padding-bottom: 8rem;
  }

  header.masthead .overlay {
    position: absolute;
    background-color: #212529;
    height: 100%;
    width: 100%;
    top: 0;
    left: 0;
    opacity: 0.3;
  }

  header.masthead h1 {
    font-size: 2rem;
  }

  @media (min-width: 768px) {
    header.masthead {
      padding-top: 12rem;
      padding-bottom: 12rem;
    }

    header.masthead h1 {
      font-size: 3rem;
    }
  }

  .showcase .showcase-text {
    padding: 3rem;
  }

  .showcase .showcase-img {
    min-height: 50rem;
    background-size: cover;
  }

  @media (min-width: 768px) {
    .showcase .showcase-text {
      padding: 7rem;
    }
  }

  .features-icons {
    padding-top: 7rem;
    padding-bottom: 7rem;
  }

  .features-icons .features-icons-item .features-icons-icon i {
    font-size: 4.5rem;
  }

  .features-icons .features-icons-item:hover .features-icons-icon i {
    font-size: 5rem;
  }

  .call-to-action .overlay {
    position: absolute;
    background-color: #212529;
    height: 100%;
    width: 100%;
    top: 0;
    left: 0;
    opacity: 0.3;
  }
</style>
