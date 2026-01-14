const { createApp } = Vue;

createApp({
    data() {
        return {
            view: 'home',
            types: [], // 分类按钮
            currentType: 0, // 当前type_id，默认0为全部
            selectedEpisode: '第1集',
            quality: '1080P 高清',
            activeMovie: null,
            movies: [], // 当前type下的视频
            site: null, // 当前站点名
            isPlaying: false, // 是否正在播放
            currentPlayUrl: '' // 当前播放url
        };
    },
    computed: {
        filteredMovies() {
            return this.movies;
        }
    },
    methods: {
        showDetail(movie) {
            this.activeMovie = movie;
            this.selectedEpisode = '第1集';
            this.isPlaying = false;
            this.currentPlayUrl = '';
            this.view = 'detail';
            window.scrollTo(0, 0);
        },
        filterType(type_id) {
            this.currentType = type_id;
            this.view = 'home';
            this.fetchMovies();
        },
        toggleFavorite(id) {
            const movie = this.movies.find(m => m.id === id);
            if (movie) movie.isFav = !movie.isFav;
        },
        async fetchSite() {
            const res = await fetch('http://localhost:3000/api/site');
            const data = await res.json();
            this.site = data.site;
        },
        async fetchTypes() {
            const res = await fetch(`http://localhost:3000/api/types?site=${this.site}`);
            const data = await res.json();
            this.types = data;
            // 默认currentType为0（全部）
        },
        async fetchMovies() {
            if (!this.site || this.currentType === null) return;
            const res = await fetch(`http://localhost:3000/api/list?site=${this.site}&type_id=${this.currentType}`);
            const data = await res.json();
            // 兼容收藏状态
                this.movies = data.map(item => {
                    // 解析剧集名和链接
                    let episodeList = [];
                    if (item.vod_play_url) {
                        // 按#分割，每段为一集
                        const rawEpisodes = item.vod_play_url.split('#');
                        rawEpisodes.forEach(raw => {
                            const segs = raw.split('$');
                            if (segs.length === 2 && segs[1].trim().startsWith('http')) {
                                // segs[0]为剧集名，segs[1]为链接
                                episodeList.push({
                                    name: segs[0].trim(),
                                    url: segs[1].trim()
                                });
                            }
                        });
                    }
                    return {
                        ...item,
                        id: item.vod_id,
                        title: item.vod_name,
                        poster: item.vod_pic,
                        desc: item.vod_content,
                        isFav: false,
                        episodes: episodeList.length,
                        episodeList
                    };
                });
        },
        // 获取当前选中的剧集url
        // 获取当前选中的剧集url
        getCurrentPlayUrl() {
            if (!this.activeMovie || !this.activeMovie.episodeList) return '';
            const idx = this.activeMovie.episodeList.findIndex(ep => ep.name === this.selectedEpisode);
            return idx >= 0 ? this.activeMovie.episodeList[idx].url : '';
        },
        playVideo() {
            this.currentPlayUrl = this.getCurrentPlayUrl();
            this.isPlaying = true;
            this.$nextTick(() => {
                if (this.$refs.player) {
                    this.$refs.player.play();
                }
            });
        }
    },
        async mounted() {
            await this.fetchSite();
            await this.fetchTypes();
            await this.fetchMovies();
        },
        // 选集切换时自动切换播放
        watch: {
            selectedEpisode() {
                if (this.isPlaying) {
                    this.currentPlayUrl = this.getCurrentPlayUrl();
                    this.$nextTick(() => {
                        if (this.$refs.player) {
                            this.$refs.player.load();
                            this.$refs.player.play();
                        }
                    });
                }
            }
        }
}).mount('#app');
