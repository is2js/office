document.addEventListener('alpine:init', () => {
    Alpine.data('ads', () => ({
        activeSection: 1,
        isPaused: false,
        autoSlideInterval: null,
        autoResumeTimeout: null,
        scrollToSection(index) {
            const el = document.getElementById(`section-${index}`);
            if (el) el.scrollIntoView({behavior: 'smooth'});
        },
        increaseActiveSection(index) {
            this.activeSection = (index % this.slides.length) + 1;
        },
        isActiveSection(index) {
            return this.activeSection === index + 1;
        },
        hasActiveSectionTitle() {
            const currentSlide = this.slides[this.activeSection - 1];
            return currentSlide && currentSlide.title;
        },
        startAutoSlide() {
            this.autoSlideInterval = setInterval(() => {
                if (!this.isPaused) {
                    this.activeSection = (this.activeSection % this.slides.length) + 1;
                    this.scrollToSection(this.activeSection - 1);
                }
            }, this.autoPlayDuration);
        },
        init() {

            // YouTube API가 로드되면 플레이어 객체 초기화(unMute를 위해 필수)
            // window.onYouTubeIframeAPIReady = () => this.initYouTubePlayers();

            // ✅ window 함수 바인딩
            window.initYouTubePlayers = this.initYouTubePlayers.bind(this);
            window.onYouTubeIframeAPIReady = () => {
                console.log('iframe API ready');
                window.initYouTubePlayers();
            };


            // 사용자 상호작용 이벤트 감지 등록

            if (this.isAutoPlay) {
                this.startAutoSlide();
            }

            this.registerUserInteraction();

            // fullscreen 이벤트 인식
            document.addEventListener('fullscreenchange', () => {
                this.fullScreenChangeHandler.bind(this);
            });
        },
        fullScreenChangeHandler() {
            this.isFullScreen = !!document.fullscreenElement;
        },

        registerUserInteraction() {
            ['click', 'keydown', 'touchstart'].forEach(event =>
                window.addEventListener(event, () => {
                    this.userInteracted = true;
                    console.log('✅ 사용자 상호작용 등록됨 (Alpine 내부)');
                }, {once: true})
            );
        },

        stopAutoSlide() {
            clearInterval(this.autoSlideInterval);
            this.autoSlideInterval = null;
        },


        controlVideoSection(index) {
            // 현재 activeSection의 슬라이드가, userInteract후 & 전체음소거가 아니면, 소리를 켜고,  나머지 슬라이드는 일시정지한다.

            if (this.players.length > 0) {
                console.log('activeSection', this.activeSection);

                this.players.forEach((p, idx) => {
                    if (p && typeof p.playVideo === 'function') {
                        if (idx === index) {
                            p.playVideo();
                            if (this.userInteracted && !this.isMutedAll) {
                                console.log('🔊 unMute 시도 (사용자 상호작용 이후)');
                                p.unMute();
                            } else {
                                console.log('🔇 사용자 상호작용 전이라 mute 유지');
                                p.mute();
                            }
                        } else {
                            p.pauseVideo();
                        }
                    }
                });
            }
        },

        togglePause() {
            if (!this.isAutoPlay) {
                this.isAutoPlay = true;
                this.isPaused = false;
                this.init();
            } else {
                this.isPaused = !this.isPaused;
            }


            //  ✅ 현재 activeSection의 슬라이드가 YouTube 영상이고 isMute가 아닌 경우, unMute
            // - 첫번재 영상이 mute로 시작되고 있을 때, 자동재생 눌러서 unMute가 되도록
            this.unMuteActiveSectionForFirstUnmuteVideoSection();
        },
        unMuteActiveSectionForFirstUnmuteVideoSection() {
            const index = this.activeSection - 1;
            const currentSlide = this.slides[index];
            const player = this.players[index];

            if (!this.isMutedAll && currentSlide && currentSlide.youtubeId && !currentSlide.isMute && player && typeof player.unMute === 'function') {
                try {
                    console.log('🔊 unMuting current video (section:', index, ')');
                    player.unMute();
                } catch (e) {
                    console.warn('⚠️ unMute 실패:', e);
                }
            }
        },


        pauseOnInteraction() {
            const wasPlaying = !this.isPaused; // 인터랙션 이전 상태가 재생 중이었는지 체크

            this.isPaused = true;

            // 자동재생 모드이면서, 이전 상태가 재생 중이었을 때만 재시작 타이머 설정
            if (this.isAutoPlay && wasPlaying) {
                clearTimeout(this.pauseTimeout); // 기존 타이머 제거

                this.pauseTimeout = setTimeout(() => {
                    this.isPaused = false;
                }, this.pauseTimeoutDuration); // 예: 10000ms
            }
        },


        userInteracted: false,
        players: [], // YouTube 플레이어 객체 저장용
        initYouTubePlayers() {
            this.slides.forEach((slide, i) => {
                if (slide.youtubeId && !slide.isMute) {
                    const iframe = document.querySelector(`#yt-${i}`);
                    console.log('iframe', iframe);
                    if (iframe) {
                        this.players[i] = new YT.Player(iframe, {
                            events: {
                                'onReady': (event) => {
                                    // // activeSection - 1 (현재 활성 슬라이드면 unmute + play)
                                    // if (i === this.activeSection - 1) {
                                    //  console.log('playVideo by onReady', i);
                                    //     event.target.unMute();
                                    //     event.target.playVideo();
                                    // } else {
                                    //     event.target.mute();
                                    //     event.target.pauseVideo();
                                    // }
                                    // // ✅ 추가된 로직: 첫 번째 섹션이고 아직 activeSection 초기화 안 됐을 수 있는 경우
                                    // if (i === 0 && this.activeSection === 1 ) {
                                    //     console.log('playVideo by onReady', i);
                                    //     event.target.unMute();
                                    //     event.target.playVideo();
                                    // }
                                }
                            },
                        });
                    }
                }
            });
        },

        isMutedAll: false,
        toggleMuteAll() {
            this.isMutedAll = !this.isMutedAll;
            console.log(this.isMutedAll ? '🔇 전체 음소거됨' : '🔊 전체 음소거 해제');

            this.players.forEach(p => {
                if (p && typeof p.mute === 'function') {
                    try {
                        this.isMutedAll ? p.mute() : (this.userInteracted && p.unMute());
                    } catch (e) {
                        console.warn('🔁 mute/unMute 실패:', e);
                    }
                }
            });
        },

        isFullScreen: false,
        toggleFullScreen() {
            const ads = this.$refs.ads;

            if (!document.fullscreenElement) {
                this.isFullScreen = true;
                if (ads.requestFullscreen)  return ads.requestFullscreen();
                if (ads.mozRequestFullScreen) return ads.mozRequestFullScreen();
                if (ads.webkitRequestFullscreen)  return ads.webkitRequestFullscreen();
                if (ads.msRequestFullscreen) return ads.msRequestFullscreen();
            } else {
                this.isFullScreen = false;
                if (document.exitFullscreen) return document.exitFullscreen();
                if (document.mozCancelFullScreen) return document.mozCancelFullScreen();
                if (document.webkitExitFullscreen) return document.webkitExitFullscreen();
                if (document.msExitFullscreen) return document.msExitFullscreen();
            }

            this.isMutedAll = !this.isMutedAll;
            console.log(this.isMutedAll ? '🔇 전체 음소거됨' : '🔊 전체 음소거 해제');

            this.players.forEach(p => {
                if (p && typeof p.mute === 'function') {
                    try {
                        this.isMutedAll ? p.mute() : (this.userInteracted && p.unMute());
                    } catch (e) {
                        console.warn('🔁 mute/unMute 실패:', e);
                    }
                }
            });
        },

    }))
});