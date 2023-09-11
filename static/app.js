const app = new Vue({
    el: '#app',
    data: {
      backgroundImageUrl: 'path/to/GS_bg.jpg', // Adjust the path accordingly
      buttonTexts: ['Sign In', 'Register'],
      buttonRoutes: ['signin', 'register']
    },
    methods: {
      goTo(route) {
        window.location.href = '/' + route;
      }
    },
    template: `
      <div class="centered-container" :style="{ backgroundImage: 'url(' + backgroundImageUrl + ')' }">
          <h1 class="huge-text">Welcome to Grocery Store</h1>
          <div class="button-container">
              <button v-for="(text, index) in buttonTexts" :key="index" class="action-button" @click="goTo(buttonRoutes[index])">{{ text }}</button>
          </div>
      </div>
    `
  });
  