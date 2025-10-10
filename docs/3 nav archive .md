---
title: 3번째 
date: '2025-03-11'
---





### base.html에 nav 추가하기
<!-- truncate -->
- body내부 전체를 div#page-container로 싸고
    - foot 대비 section을 div.content-wrap으로 싸고
        - div.nav
            - a태그안에 img#logo 추가
                - static/img/logo.png 추가
        - div.content

#### nav 메뉴는 a[href]=에 내가 준 path들 1번째 것들만 나열한다.

```html
<div id="page-container">
    <div id="content-wrap">
        <div class="nav">
            <a id="title" href="{{ root_path }}"><img id="logo" src="{{ static_path }}/img/logo.png"/>{{ config['title'] }}{{ config['title'] }}</a>
            <ul class="links">
                <li><a href="{{ root_path }}">Home</a></li>
                <li><a href="{{ root_path }}blog">Blog</a></li>
                <li><a href="{{ root_path }}archive">Archive</a></li>
            </ul>
        </div>
        <div class="content">
            {% block content %}
            {% endblock %}
        </div>
    </div>
```



- css

```css
@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

html, body {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    font-size: 100%;
    line-height: 1.65;
}


/* base.html */
/* sticky footer */
#page-container {
    position: relative;
    min-height: 100vh;
}

#content-wrap {
    padding-bottom: 5em;
}

.nav {
    background-color: #1ECECB;
    padding: 1em;
    color: white;

    & a {
        color: inherit;
    }

    & a#title {
        font-weight: bold;
        text-decoration: none;
        font-size: 150%;
    }

    & .links {
        display: inline-block;
        list-style-type: none;
        padding-left: inherit;

        & li {
            display: inline-block;
            padding: 0 1em;
        }

        & li a {
            text-decoration: none;
        }
    }
}

.nav, .nav #title {
    display: flex;
    align-items: center;
}

.nav #logo {
    margin-right: 0.4em;
    height: 2em;
}


.content {
    margin: 1em;
}
```









#### path 1번째것이 없이  /blog/nested/post/index.html이라면? /blog nav메뉴는 index.html 없이  `경로가 있다면 디렉토리` or `경로조차 없다면 에러`

```
python -m http.server --directory build
```



```html
<ul class="links">
    <li><a href="../">Home</a></li>
    <li><a href="../blog">Blog</a></li>
    <li><a href="../archive">Archive</a></li>
</ul>
```

![image-20250311123309635](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311123309635.png)



- **해당  nav메뉴 경로 `/blog/aaa/bbb`에 대한 `/blog/aaa/index.html`이 생성이 안되어있다면, `디렉토리`가 표시된다.**

    ![image-20250311123425665](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311123425665.png)

- **`경로조차 없다면`**

    ![image-20250311123637665](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311123637665.png)







### posts[0:5]가 아닌 posts 전체를 모아놓는 archive.html (index.html처럼 template 자체가 html)



1. index.html 복붙해서 archive.html을 생성

    - posts[0:5] -> posts로 순회

    ```html
    {% block content %}
    <div class="posts-index">
        {% for post in posts -%}
    ```

    

2. render_index과정과 비슷하니 메서드로 만들어놓고 다른 부분을 고치게 파라미터로 뺀다.

    ```python
    def render_html(page, config, env, posts, title='Home'):
    
        html_template = env.get_template(page)
    
        if __name__ == '__main__':
            index_relative_root_path = get_relative_root_path(page, is_test=True)
            static_path = os.path.join(index_relative_root_path, 'md_templates', 'static')
        else:
            index_relative_root_path = get_relative_root_path(page)
            static_path = os.path.join(index_relative_root_path, 'static')
    
        html = html_template.render(
            config=config,
            root_path=index_relative_root_path,
            static_path=static_path,
            title=title,
            posts=posts,
        )
        return html
    ```

    

    ```python
    ## render index -> posts 전체 + index페이지 제목을 넘겨준다.
    index = render_html('index.html', config, env, posts, title='상세질환 디자인')
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index)
    ```

    

3. arhive.html도 마찬가지로 렌더링해준다.

    ```python
    ## render archive -> posts 전체 + index페이지 제목을 넘겨준다.
    archive = render_html('archive.html', config, env, posts, title='아카이브')
    archive_path = os.path.join(OUTPUT_DIR, 'archive.html')
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(archive)
    ```

    



4. 실행

    ```
    python setup.py install
    mdr
    
    python -m http.server --directory build
    ```

    

5. **archive는 `/archive`로 접속할텐데 `그곳에 index.html파일로 존재`해야한다.**
   
    - 실행하면 에러 뜬다.





#### 새 페이지라면, 페이지명.html이 아니라 path1개 / index.html로 존재해야한다.

```python
# 새 페이지 -> path1개/index.htmlㅇ이어야한다.
# 새 페이지 -> 경로가 없을 수 있으니 path1개의 경로도 만들어놔야한다.
# archive_path = os.path.join(OUTPUT_DIR, 'archive.html')
os.makedirs(os.path.join(OUTPUT_DIR, 'archive'), exist_ok=True)
archive_path = os.path.join(OUTPUT_DIR, 'archive', 'index.html', title='아카이브')
with open(archive_path, 'w', encoding='utf-8') as f:
    f.write(archive)
```

![image-20250312091953246](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250312091953246.png)








### archive.html 연도별 나열 디자인

1. jinja문으로 

    - **post의 attributes.date_parsed 속성을 기준으로 sort**
        - 지금부터는 date 프론트메터 -> date_parsed가 필수
    - **for문 돌기전에 업뎃변수를 dict로 선언 -> for문 내부에서 prev_year업뎃**
        - **prev_year를 `dict로 for문 내부에서도 업뎃가능`하게  0000부터 시작하여 `최초 업뎃되게 -1 같은 용도`**, 역순포스트의 연도를 **같지않다면 계속 업뎃해서, 2025 -> 2024 계속 가게 만듦. `같다면 업뎃 안되게 유지`**
        - **`if update문 성공` == `달라질 때 연도 코드 작성`**

    ```html
    {% extends "base.html" %}
    {% block title %}{{title}}{% endblock %}
    
    {% block content %}
    
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

