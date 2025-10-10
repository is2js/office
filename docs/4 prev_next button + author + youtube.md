
<!-- truncate -->
<!-- summary -->

### prev, next


1. 현재 post template인 contents.html  -> post.html 로 변경

2. render post시 prev, next도 같이 넘기고 있다.

    ```python
    post_html = content_template.render(
        config=config,
        root_path=relative_root_path,
        static_path=static_path,
    
        post=post_html,
        prev_post=prev_post,
        next_post=next_post,
    
    )
    ```

3. template에서 body외에 title + 이전/다음 post도 사용하자

    - **다만, prev/next_post 객체가 있을 경우**
    - **div 안에**
        - 글자: 이전/다음 post의 path를 a[href]에 / 제목을 내용에

    ```html
    <!-- 이전 post / 다음 post -->
    {% if prev_post %}
    <div>
        이전:
        <a href="{{root_path}}{{ prev_post['attributes']['path'] }}">{{ prev_post['attributes']['title'] }}</a>
    </div>
    {% endif %}
    {% if next_post %}
    <div>
        다음:
        <a href="{{root_path}}{{ next_post['attributes']['path'] }}">{{ next_post['attributes']['title'] }}</a>
    </div>
    {% endif %}
    ```

    ![image-20250313223939995](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250313223939995.png)

4. 테스트를 위해 날짜 + path가 적힌 md를 몇개 만들어보자.

```
---
title: 'test1'
path: /blog/1
date: '2025-03-12'
---


1
```



```
---
title: 'test2'
path: /blog/2
date: '2025-03-12'
---


2
```

```
---
title: 'test3'
path: /blog/3
date: '2025-03-13'
---


3
```

    

    ![image-20250313224226051](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250313224226051.png)

    ![image-20250313224216315](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250313224216315.png)

### post frontmatter에 authors  추가 in config

1. 사용자입력 docs / .mdr / config.yml에 `config.yml`에  authors를 추가한다.

    ```yml
    title: 조재성 원장
    authors:
      조재성:
        name: 조재성 원장
      김석영:
        name: 김석영 원장
    ```

    

2. config.yml과 별개로 md파일에서 frontmatter로 `authors: [ , ]`로 키 들을 입력한다.

    ```md
    ---
    title: 'test2'
    path: /blog/2
    date: '2025-03-12'
    authors: 김석영
    ---
    
    
    2
    ```

3. **post template에 frontmatter authors들을 사용한다.**

    ```html
    {% block content %}
    <!-- 제목 -->
    {{ post['attributes']['title'] }}
    <!-- 작성자 -->
    {% if 'authors' in post['attributes'] %}
    <div>
        {% for author in post['attributes']['authors'] %}
        By {{ author }}
        {% endfor %}
    </div>
    {% endif %}
    ```

    ![image-20250314233151289](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250314233151289.png)

4. **사실은 config에서 명시한 것과 일치하는지 확인하는 절차가 필요하다.**

    - **frontmatter의 authors가 존재하는지 ` | length  > 1` 시에는 `authors`로**
        - **frontmatter에 1개 이하면 `author의 단수`로 나타내야하고**
    - **추가로 frontmatter의 authors가 config의 authors에 포함될 경우, `config의 authors 내부에 value값name`값을 갖다 쓰게 해야한다. 없다면, 그냥 frontmatter의 값들을 쓰게 한다.**

    ```html
    <!-- 작성자 -->
    {% if 'authors' in post['attributes'] %}
    <div>
        <!-- 작성자가 2명 이상인 경우 -->
        {% if (post['attributes']['authors'] | length) > 1 %}
        작성자들:
        {% else %}
        작성자:
        {% endif %}
        <!-- 작성자들이 config의 authors에 포함되어 있다면, config내 name값 아니면 frontmatter 입력값 -->
        {% for author in post['attributes']['authors'] %}
        {% if author in config['authors'] %}
        {{ config['authors'][author]['name'] }}
        {% else %}
        {{ author }}
        {% endif %}
        {% endfor %}
    </div>
    {% endif %}
    ```

    ```
    ---
    title: 'test2'
    path: /blog/2
    date: '2025-03-12'
    authors: [조재성, config미포함작성자]
    ---
    
    
    2
    ```

    ```html
    <div>
        <!-- 작성자가 2명 이상인 경우 -->
        
        작성자들:
        
        <!-- 작성자들이 config의 authors에 포함되어 있다면, config내 name값 아니면 frontmatter 입력값 -->
        조재성 원장
        config미포함작성자
        
        
    </div>
    ```

    ![image-20250314234229866](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250314234229866.png)

### youtube frontmatter

1. youtube 뒤쪽 id를 복사한다.

    ![image-20250315125441651](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315125441651.png)

2. 복사한 아이디를 넣는다.

    ```
    ---
    title: 'test4 youtube'
    path: /blog/4
    date: '2025-03-12'
    authors: [조재성]
    youtube: P_06Nvmunrk
    ---
    
    유튜브
    ```

3. post template에 youtube 매터를 확인 한뒤, **iframe에 `/embed/{{}}`로 집어넣는다.**

    - **기본 100%에 max-width:를 1185 으로 준다.**

    ```html
    <!-- 제목 -->
    <h1>{{ post['attributes']['title'] }}</h1>
    <!-- youtube -->
    {% if 'youtube' in post['attributes'] %}
    <div class="youtube">
        <iframe width="560" height="315"
            src="https://www.youtube.com/embed/{{ post['attributes']['youtube'] }}"
            title="YouTube video player"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
        </iframe>
    </div>
    {% endif %}
    ```

    ![image-20250315125957585](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315125957585.png)





#### div.content > layout-center으로 가운데 정렬해서, youtube는 w100% 높이 반응형

- **원래는 모바일을 위해서는 `767`까지 모바일이었는데 더블모니터를 위해 `991`까지로 바꿈**

1. section에 쓰던 layout-center옵션을 여기 넣어서 가운데 정렬되게 한다

    - 모바일에선 w100임.

    ```css
    .content {
        & .layout-center {
            /*margin: 1em;*/
            width: 1185px;
            /*margin: 0 auto;*/
            /* 기본 위쪽 여백 추가 */
            margin: 60px auto 0;
    
    	/*@media (max-width: 767px) {*/
            @media (max-width: 991px) {
                margin: 0;
                width: 100%;
                /* w100%에  추가로 padding을 주면, box-sizing: border-box 안주면 가로스크롤이 생긴다.*/
                /* -> 여기선 bootstrap reboot에서 처리해줘서 생략했다.*/
                box-sizing: border-box;
                /* header 모바일 패딩과 동일한 값 */
                /*padding: 0 15px 0 ;*/
                /* 모바일에서 section mt까지 대체 */
                /* 특히 section-border도 반영하려면, margin대신 padding으로 */
                padding: 20px;
            }
        }
    }
    ```

    

2. **iframe embed 유튜브영상의 높이가 반응형이 적용안되서 검색해서 적용한다. **

    - div에 youtube를 추가하고 크기조정 옵션은 뻰다

    ```html
    {% if 'youtube' in post['attributes'] %}
    <div class="youtube">
        <!--<iframe width="100%" style="aspect-ratio: 16 / 9;"-->
        <iframe
                src="https://www.youtube.com/embed/{{ post['attributes']['youtube'] }}"
                title="YouTube video player"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
        </iframe>
    </div>
    {% endif %}
    ```

    

3. height를 자동조절하도록 참고해서 작성한다.

    - https://bobosszone.tistory.com/entry/%EC%9C%A0%ED%8A%9C%EB%B8%8C-iframe-height-%EC%9E%90%EB%8F%99-%EC%A1%B0%EC%A0%88

    - https://erim1005.tistory.com/entry/Youtube-iframe-width-100-height-auto

    - **iframe부모 태그div.youtube에는 `pos:rel을 주고, height 0 overflow hidden`을 준 다음, `pb를 %로 크기 조정`한다.**

        - **내부 영상은 `pos:abs + top0tleft0`에서 `w100 h100`으로 조절한다.**

        ```css
        /* post.html */
        .youtube {
            position: relative;
            height: 0;
            overflow: hidden;
            /* 영상 크기 조절 */
            padding-bottom: 56.25%;
            /*padding-top: 30px;*/
        
            & iframe, object, embed {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
        
                /* 꾸미기 */
                border-radius: 1em;
                background-color: lightgray;
            }
        }
        ```

        ![image-20250315163349271](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315163349271.png)







4. **영상을 다 채우지말고 abs가운데 정렬후 여백주기**

    ```css
    & iframe, object, embed {
        position: absolute;
        /*top: 0;*/
        /*left: 0;*/
        /* 가운데 정렬*/
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        height: 90%;
    
        @media (max-width: 991px) {
            width: 95%;
            height: 95%;
        }
    ```

    



5. 최종

    - 반응형 적용

    ```css
    /* post.html */
    .youtube {
        position: relative;
        height: 0;
        overflow: hidden;
        /* 영상 크기 조절 */
        padding-bottom: 50%;
        @media (max-width: 991px) {
            padding-bottom: 56.25%;
        }
        /*padding-top: 30px;*/
    
        & iframe, object, embed {
            position: absolute;
            /*top: 0;*/
            /*left: 0;*/
            /* 가운데 정렬*/
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 83%;
            height: 90%;
            @media (max-width: 991px) {
                width: 99%;
                height: 95%;
            }
    
            /* 꾸미기 */
            border-radius: 1em;
            background-color: lightgray;
        }
    }
    ```

    





### 명령어

```
python setup.py install
mdr

python -m http.server --directory build
```



### jinja참고

#### jinja2에서 sort: {% set 정렬데이터 = 데이터|sort(attribute='',reverse=True) %} -> 다시 순회

![image-20250311090346996](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311090346996.png)



#### 속성이 여러개면 `a.b`로 정렬 + for문 내부 업뎃을 위해, dict로 변수 없뎃 + if문 내부에 문서들은 endif끝내기 전에 if update문 성공시에 연도 표시(달라지면 작성)

```html
<div class="archive">
    {% set posts_sorted = posts | sort(attribute='attributes.date_parsed', reverse=True) %}
    {% set prev_year = {'value': '0000'} %}
    {% for post in posts_sorted -%}
    {% set curr_year = post['attributes']['date_parsed'].strftime('%Y') %}
    {% if curr_year != prev_year['value'] %}
    {% if prev_year.update({'value': curr_year}) %}{% endif %}
    <div class="year">
        <h3>{{ curr_year }}년</h3>
    </div>
    {% endif %}


    <div class="post">
        <div class="title">
            {{ post['attributes']['date_parsed'].strftime('%b, %m월') }}: <a href="{{ post['attributes']['path'] }}">{{
            post['attributes']['title']}}</a>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```





### 코딩 참고

- https://strftime.org/

