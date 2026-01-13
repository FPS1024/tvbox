const { createApp } = Vue;

createApp({
    data() {
        return {
            view: 'home',
            currentType: '全部',
            selectedEpisode: '第1集',
            quality: '1080P 高清',
            activeMovie: null,
            movies: [                           
                {
                    id: 1,
                    title: '星际穿越',
                    type: '电影',
                    category: '科幻 / 冒险',
                    score: 9.4,
                    region: '美国',
                    year: 2014,
                    poster: 'https://mmecoa.qpic.cn/mmecoa_jpg/nPVOKiaianVyO6Rt6tzPflEZcnPUB56r0Om3aSqkx0BF2ic9dFl4C28p2S0aObfy0X1L85hoRSCoZ0ia4sNb2vbtlA/0?wx_fmt=jpeg',
                    desc: '一组探险者利用虫洞进行星际航行。',
                    isFav: false,
                    episodes: 1
                },
                {
                    id: 2,
                    title: '权力的游戏',
                    type: '电视剧',
                    category: '剧情 / 奇幻',
                    score: 9.3,
                    region: '美国',
                    year: 2011,
                    poster: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23',
                    desc: '维斯特洛大陆的权力斗争。',
                    isFav: false,
                    episodes: 10
                }
            ]
        };
    },
    computed: {
        filteredMovies() {
            if (this.currentType === '全部') return this.movies;
            return this.movies.filter(m => m.type === this.currentType);
        }
    },
    methods: {
        showDetail(movie) {
            this.activeMovie = movie;
            this.view = 'detail';
            window.scrollTo(0, 0);
        },
        filterType(type) {
            this.currentType = type;
            this.view = 'home';
        },
        toggleFavorite(id) { // 收藏按钮逻辑
                    const movie = this.movies.find(m => m.id === id);
                    movie.isFav = !movie.isFav;
                }
    }
}).mount('#app');
