<template>
  <v-autocomplete
    outlined
    rounded
    :loading="loading"
    dense
    clearable
    :menu-props="{ contentClass: 'transparent-scroll' }"
    :items="combinedItems"
    item-text="title"
    item-value="title"
    color="#4edf93"
    v-model="searchTerm"
    no-data-text="尝试输入电影名..."
    placeholder="输入关键词"
    @change="handleSearch"
  >
    <template #prepend-inner>
      <v-icon size="18" class="mt-1 mr-2">$search</v-icon>
    </template>
    <template #append>
      <v-icon @click="voiceSearch" size="21" class="mr-2">$microphone</v-icon>
      <v-icon @click="handleSearch" size="21" class="text-green">$search</v-icon>
    </template>

    <template #item="{item}" class="mt-12">
      <v-list-item two-line @click="selectItem(item)">
        <v-list-item-content class="text-left">
          <v-list-item-title>
            <span v-if="item.isHistory" class="text-grey">
              <v-icon small left>mdi-history</v-icon>
            </span>
            {{ item.title }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="!item.isHistory">{{ item.type }}</v-list-item-subtitle>
          <v-list-item-subtitle v-else class="text-grey text-xs">历史搜索</v-list-item-subtitle>
        </v-list-item-content>
        <v-list-item-action v-if="item.isHistory">
          <v-icon small @click.stop="removeHistory(item)" class="text-grey">mdi-close</v-icon>
        </v-list-item-action>
      </v-list-item>
    </template>
    
    <template #no-data>
      <div class="pa-4">
        <div v-if="history.length > 0" class="mb-2">
          <div class="text-xs text-grey mb-2">历史搜索</div>
          <v-list>
            <v-list-item v-for="(item, index) in history" :key="index" @click="selectItem(item)">
              <v-list-item-content class="text-left">
                <v-list-item-title>
                  <v-icon small left>mdi-history</v-icon>
                  {{ item.title }}
                </v-list-item-title>
              </v-list-item-content>
              <v-list-item-action>
                <v-icon small @click.stop="removeHistory(item)" class="text-grey">mdi-close</v-icon>
              </v-list-item-action>
            </v-list-item>
          </v-list>
          <v-divider class="my-2"></v-divider>
        </div>
        <div class="text-center text-grey">尝试输入电影名...</div>
      </div>
    </template>
  </v-autocomplete>
</template>

<script>
import {get} from "../api/movie";
import _ from "lodash"

export default {
  name: "search-box",
  data: () => ({
    searchTerm: "",
    loading: false,
    searchItems: [],
    history: [],
  }),
  computed: {
    combinedItems() {
      // 先显示历史记录，再显示搜索结果
      const historyItems = this.history.map(item => ({ ...item, isHistory: true }));
      const searchItems = this.searchItems.map(item => ({ ...item, isHistory: false }));
      return [...historyItems, ...searchItems];
    }
  },
  created() {
    // 从localStorage读取历史记录
    this.loadHistory();
  },
  watch: {
    searchTerm(newVal) {
      if (newVal) {
        this.doSearch()
      } else {
        this.searchItems = [];
      }
    },
  },
  methods: {
    voiceSearch() {},
    doSearch: _.debounce(function(){
      console.log("searchTerm",this.searchTerm)

      if (!this.searchTerm) {
        this.searchItems = [];
        return;
      }
      
      this.loading = true;
      if(this.searchTerm == null)
        return

      get({"keyword": this.searchTerm}).then(res=>{
        this.searchItems = res.data.data.map(item => ({
          title: item.name,
          type: item.genres,
          id: item.id
        }));
        this.$emit('search-movie', res.data.data)
      }).catch(error => {
        console.error('搜索失败:', error);
      }).finally(() => {
        this.loading = false;
      });
    },2000),
    handleSearch() {
      if (this.searchTerm) {
        this.addToHistory(this.searchTerm);
        this.performSearch();
      }
    },
    performSearch() {
      // 立即执行搜索，不使用防抖
      if (!this.searchTerm) {
        this.searchItems = [];
        return;
      }
      
      this.loading = true;
      get({"keyword": this.searchTerm}).then(res=>{
        this.searchItems = res.data.data.map(item => ({
          title: item.name,
          type: item.genres,
          id: item.id
        }));
        this.$emit('search-movie', res.data.data)
      }).catch(error => {
        console.error('搜索失败:', error);
      }).finally(() => {
        this.loading = false;
      });
    },
    selectItem(item) {
      if (item.isHistory) {
        this.searchTerm = item.title;
      } else {
        this.searchTerm = item.title;
      }
      this.handleSearch();
    },
    addToHistory(keyword) {
      // 移除重复的历史记录
      this.history = this.history.filter(item => item.title !== keyword);
      // 添加到历史记录开头
      this.history.unshift({ title: keyword });
      // 限制历史记录数量
      if (this.history.length > 10) {
        this.history = this.history.slice(0, 10);
      }
      // 保存到localStorage
      this.saveHistory();
    },
    removeHistory(item) {
      this.history = this.history.filter(historyItem => historyItem.title !== item.title);
      this.saveHistory();
    },
    saveHistory() {
      localStorage.setItem('searchHistory', JSON.stringify(this.history));
    },
    loadHistory() {
      const savedHistory = localStorage.getItem('searchHistory');
      if (savedHistory) {
        this.history = JSON.parse(savedHistory);
      }
    }
  },
};
</script>

<style>
.transparent-scroll {
  scrollbar-width: thin;
  scrollbar-color: transparent;
}
.transparent-scroll::-webkit-scrollbar {
  width: 6px;
  background-color: transparent;
}
.transparent-scroll::-webkit-scrollbar-thumb {
  background: #d8dcde;
  border-radius: 4.5px;
}
.transparent-scroll::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
