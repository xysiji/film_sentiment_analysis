import {mapState} from "vuex";

let mixin =  {
  data: ()=>({
    appName : '电影评论情感分析系统',
    appIcon : 'douban'
  }),
  created() {
  },
  mounted() {},
  methods: {
    serverImg(url){
      return "http://localhost:8080/file/download/" + url
    }
  },
  //直接把mapState mixin进去
  computed: {
    ...mapState(['uid','avatar','phone']),
  },
};
export default mixin;
