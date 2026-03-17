<template>
  <v-card
    :ripple="false"
    :style="genShadow(song.color)"
    :color="song.color"
    rounded="xl"
    min-height="400"
    max-height="450"
  >
    <v-card-title>
      <v-icon class="music-playing-icon">movie</v-icon>
      <v-icon class="dots-music-card">$dots-vertical</v-icon>
    </v-card-title>
    <v-card-text class="font-bold-medium" v-once>{{ cardTitle }}</v-card-text>
    <v-img
      class="mx-auto card-image"
      :src="doubanImg(song.image)"
      max-width="160"
      min-height="200"
      max-height="90%"
    ></v-img>
    <span class="rate-text" v-once>{{ cardTitle }}</span>
  </v-card>
</template>

<script>
export default {
  name: "music-card",
  props: {
    song: Object,
    cardTitle: String
  },
  methods: {
    genShadow(color) {
      return `-webkit-box-shadow: 0px 10px 35px -8px ${color};
              box-shadow: 0px 10px 35px -8px ${color};
              -moz-box-shadow: 0px 10px 35px -8px ${color};`;
    },
    doubanImg(src) {
      let trueSrc = ''
      if(src.startsWith("http://localhost:8080"))
        trueSrc = src
      else
        trueSrc = 'https://images.weserv.nl/?url=' + src
      return trueSrc
    },
  },
};
</script>

<style scoped>
.music-playing-icon {
  position: absolute;
  top: 20px;
  left: 20px;
}
.dots-music-card {
  position: absolute;
  top: 20px;
  right: 20px;
}
.font-bold-medium {
  position: relative;
  font-weight: 900 !important;
  color: white !important;
  font-size: 25px !important;
}

.d-hidden {
  opacity: 0;
}
.card-image {
  border-radius: 0 !important;
  position: absolute;
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%);
  -o-transform: translateX(-50%);
  -ms-transform: translateX(-50%);
  -moz-transform: translateX(-50%);
  -webkit-transform: translateX(-50%);
}

.rate-text {
  position: absolute;
  bottom: 5%;
  left: 0;
}
</style>
