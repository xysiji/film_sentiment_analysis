<template>
  <v-card
      :loading="loading"
      class="mx-auto my-12 movie-card"
      max-width="374"
      height="550"
  >
    <template slot="progress">
      <v-progress-linear
          color="deep-purple"
          height="10"
          indeterminate
      ></v-progress-linear>
    </template>



    <v-card-title>{{movie.name}}</v-card-title>

    <v-card-text class="pt-4">
      <div class="rating-section mb-3">
        <v-rating
            :value="movie.douban_score/2.0"
            color="amber"
            dense
            half-increments
            readonly
            size="18"
            class="rating-stars"
        ></v-rating>
        <div class="grey--text rating-score mt-1">
          {{movie.douban_score}} 分 ({{movie.douban_votes}}人评价)
        </div>
      </div>

      <div class="my-2 text-subtitle-2 movie-info">
        <strong>类型：</strong>{{movie.genres}}
      </div>

      <div class="my-2 text-subtitle-2 movie-info">
        <strong>地区：</strong>{{movie.regions}}
      </div>

      <div class="my-2 text-subtitle-2 movie-info" v-if="movie.directors">
        <strong>导演：</strong>{{movie.directors}}
      </div>
    </v-card-text>

    <v-divider class="mx-4"></v-divider>

    <v-card-title>介绍</v-card-title>

    <v-card-text>
      <div class="my-4 text-subtitle-2" v-if="movie.actors">
       演员： {{movie.actors.substring(0,20)}}..等
      </div>
      <div class="my-4 text-subtitle-2" v-if="movie.directors">
       导演： {{movie.directors}}
      </div>
      <div class="my-4 text-subtitle-3" v-if="movie.storyline">
        简介： {{movie.storyline.substring(0,50)}}...
      </div>
    </v-card-text>

    <v-card-actions>
      <v-btn
          color="deep-purple lighten-2"
          text
          @click="reserve(movie.douban_id)">
        详情
      </v-btn>

      <v-dialog
          v-model="dialog"
          scrollable
          max-width="900"
      >
        <template v-slot:activator="{ on, attrs }">
          <v-btn
              color="primary"
              text
              v-bind="attrs"
              v-on="on"
              @click="getCommentsByDoubanId(movie.douban_id)"
          >
            影评情感分析
          </v-btn>
        </template>
        <v-card :loading="tableLoading">
          <v-card-title>精选影评</v-card-title>
          <v-divider></v-divider>
          <v-card-text style="height: 500px">
            <v-simple-table >
              <template v-slot:default>
            <thead>
            <tr>
              <th class="text-left">
                头像(avatar)
              </th>
              <th class="text-left">
                用户(user)
              </th>
              <th class="text-left">
                评论(comment)
              </th>
              <th class="text-left">
                情感分类(label)
              </th>
              <th class="text-left">
                概率(prob0)
              </th>
            </tr>
            </thead>
            <tbody>
            <tr
                v-for="(item,index) in comments"
                :key="index"
            >
              <td><img :src="item.douban_user_avatar"/></td>
              <td>{{ item.douban_user_nickname }}</td>
              <td>{{ item.content }}</td>
              <td>
                <div v-if="item.label=='positive'" class="sentiment-tag positive">
                  <v-icon small color="green">mdi-thumb-up</v-icon>
                  <span>好评</span>
                </div>
                <div v-else-if="item.label=='negative'" class="sentiment-tag negative">
                  <v-icon small color="red">mdi-thumb-down</v-icon>
                  <span>差评</span>
                </div>
                <div v-else-if="item.label=='neutral'" class="sentiment-tag neutral">
                  <v-icon small color="grey">mdi-minus</v-icon>
                  <span>中性</span>
                </div>
                <div v-else-if="item.label=='very_positive'" class="sentiment-tag very-positive">
                  <v-icon small color="green darken-2">mdi-thumb-up</v-icon>
                  <span>力荐</span>
                </div>
                <div v-else-if="item.label=='very_negative'" class="sentiment-tag very-negative">
                  <v-icon small color="red darken-2">mdi-thumb-down</v-icon>
                  <span>很差</span>
                </div>
                <div v-else class="sentiment-tag unknown">
                  <v-icon small color="grey">mdi-help-circle</v-icon>
                  <span>未知</span>
                </div>
              </td>
              <td>{{ item.score * 100}}%</td>
            </tr>
            </tbody>
              </template>
            </v-simple-table>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn
                color="teal darken-1"
                text
                @click="dialog = false"
            >
              关闭
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-actions>
  </v-card>
</template>

<script>
import {getComments} from '@/api/movie'

export default {
  name: "movie-card",
  props: {
    movie: Object,
    cardTitle: String
  },
  data: () => ({
    loading: false,
    tableLoading: false,
    selection: -1,
    dialog: false,
    comments: []
    // comments: [{'comment':'这部电影还不错的哦,如果是很多很多字怎么说呢，嗯呢？？？？？‘','label':'positive','score':98.112},
    //   {'comment':'属实不知道该怎么去评价，有点不知所云','label':'negative','score':91.23}],
  }),
  methods: {
    doubanImg(src) {
      let trueSrc = ''
      if(src!=null && src.startsWith("http://localhost:8080"))
        trueSrc = src
      else
        trueSrc = 'https://images.weserv.nl/?url=' + src
      return trueSrc
    },
    reserve (url) {
      url = "https://movie.douban.com/subject/" + url
      this.loading = true
      setTimeout(() => {
            this.loading = false
            window.open(url)
          }
      , 2000)
    },
    getCommentsByDoubanId(id){
      this.tableLoading = true
      // console.log("douban_id", id)
      const form = {"douban_id": id}
      getComments(form).then(res=>{
        // console.log(res.data)
        this.comments = res.data.data
        if(this.comments.length == 0)
          this.$snackbar({content: '暂无影评数据！', top:true, center:true, color:'red',multiLine: true})
        this.tableLoading = false
      })
    }
  },
};
</script>

<style scoped>
.movie-card {
  display: flex;
  flex-direction: column;
}

.movie-card .v-card__text {
  flex: 1;
  overflow: hidden;
}

.movie-card .v-card__actions {
  margin-top: auto;
}

.rating-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.rating-stars {
  margin-left: -4px;
}

.rating-score {
  font-size: 13px;
}

.movie-info {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sentiment-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.sentiment-tag.positive {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.sentiment-tag.negative {
  background-color: #ffebee;
  color: #c62828;
}

.sentiment-tag.neutral {
  background-color: #f5f5f5;
  color: #616161;
}

.sentiment-tag.very-positive {
  background-color: #c8e6c9;
  color: #1b5e20;
}

.sentiment-tag.very-negative {
  background-color: #ffcdd2;
  color: #b71c1c;
}

.sentiment-tag.unknown {
  background-color: #eeeeee;
  color: #9e9e9e;
}
</style>
