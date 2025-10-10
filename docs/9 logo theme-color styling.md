

### logo

1. `div.nav`와 `자식인 a#title`은 flex로 수직정렬 align-items center로 한다

    ```html
    <div class="nav">
        <a id="title" href="{{ root_path }}">
            <img id="logo" src="{{ static_path }}/img/logo.png"/>{{ config['title'] }}
        </a>
        <ul class="links">
            <li><a href="{{ root_path }}">Home</a></li>
            <li><a href="{{ root_path }}blog">블로그</a></li>
            <li><a href="{{ root_path }}archive">Archive</a></li>
        </ul>
    </div>
    ```

    

    ```css
    .nav {
        display: flex;
        align-items: center;
    
        & a#title {
            display: flex;
            align-items: center;
        }
    ```

2. a#title안에 있는 로고 + 글자 조합에서 로고에는 mr를 줘서 글자와 벌린다.

    - logo는 높이를 직접 준다.

    ```css
    .nav {
        display: flex;
        align-items: center;
    
        & a#title {
            display: flex;
            align-items: center;
        }
    
        & img#logo {
            height: 2em;
            margin-right: 0.4em;
        }
    ```

    

    ![image-20250325085040412](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250325085040412.png)







### config에서 theme 색 정해주기

1. config에서 `theme`아래 `primary` 등으로 색을 정해준다.

    - **그전에 사용하던 색들의 색을 확인한다.**

    ```css
    :root {
        /*  */
        --greyf1: #f1f3f6;
        --greyf2: #f2f2f2;
    
        /* font */
        --grey3c: #3c3c3c;
        --main: #1ECECB;
        --green: #00b5b2;
        --submain: #FC5230;
        --submain-25: rgba(252, 82, 48, 0.25);
        --purple6f: #6f49fa;
    }
    ```

2. `docs/.mdr`의 config.yml에 붙혀넣어서 수정한다.

    ```yml
    theme:
      primary: "#1ECECB"
      secondary: "#FC5230"
    ```

    - template의 default_confg.yml에도 넣어준다.

    

3. `base.html`에서는 `style태그 + :root { }`로 `--theme-primary`를 config에서 받아서 넣어준다.

    - 각 css link보다 더 위에 style태그를 root로 넣어주자.

    ```css
    <style>
        :root {
            --theme-primary: {{ config['theme']['primary'] }};
            --theme-secondary: {{ config['theme']['second'] }};
        }
    </style>
    ```

    

![image-20250325090109550](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250325090109550.png)



4. 이제 기본색main, submain을 썼던 css로 가서, primary, second로 바꿔준다.

    ```css
    .nav {
        display: flex;
        align-items: center;
    
    
        /*background-color: var(--main);*/
        background-color: var(--theme-primary);
    ```

    ```css
        :not(pre) > code {
            letter-spacing: 1px;
    
            font-weight: 700;
            padding: 0 0.25em;
            /*color: var(--submain);*/
            color: var(--theme-secondary);
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



- regex101.com
- 