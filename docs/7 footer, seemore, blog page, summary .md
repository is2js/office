###  base.html에서 footer 코드 / main.js 추가

- `#page-container` 내부에 넣는다.

    - #content-wrap .content .layout-center와 다름.

    ```css
    #page-container {
        position: relative;
        min-height: 100vh;
    }
    
    #content-wrap {
        padding-bottom: 5em;
    }
    
    .content {
        & .layout-center {
            /*margin: 1em;*/
            width: 1185px;
            /*margin: 0 auto;*/
            /* 기본 위쪽 여백 추가 */
            margin: 60px auto 0;
        }
    }
    ```



1. .footer는 `config`에 footer > copyright > enabled가 true일때만 copyright > company가 존재한다.

    - 추가적으로 footer > give_credit 가 존재할때만 credit가 존재한다.

    ```html
    <div id="page-container">
    	<!-- ... -->
        <div class="footer">
            {% if config['footer']['copyright']['enabled'] %}
            <div id="copyright">
                Copyright &copy; <span id="year"></span>{{ config['footer']['copyright']['company'] }}
            </div>
            {% endif %}
            {% if config['footer']['give_credit'] %}
            <div id="credit">
                Made with <a href="https://github.com/pagekeytech/markdown-sitegen">MDR</a> from <a
                    href="https://www.pagekeytech.com/">남룡북매</a>
            </div>
            {% endif %}
        </div>
    </div>
    
    ```

2. **추가로 main.js도 base에 추가해주자.**

    ```html
    <script src="{{ static_path }}/main.js"></script>
    {% block extra_js %}{% endblock %}
    </body>
    ```

3. docs > .mdr > config.yml에 footer부분을 추가한다.

    ```yaml
    title: 조재성 원장
    authors:
      조재성:
        name: 조재성 원장
      김석영:
        name: 김석영 원장
        
        
    footer:
      copyright:
        enabled: true
        company: (주) 김석영 주식회사
      give_credit: true
      
    ```

    ```yaml
    title: Your Website
    authors:
      your_name:
        name: Your Name
    
    footer:
      copyright:
        enabled: true
        company: Your Comp
      give_credit: true
    
    ```

    ![image-20250322201934796](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322201934796.png)





#### footer css

1. footer는 absolute로 처리하고, #page-container는 rel이게 된다.

    ```css
    .footer {
        position: absolute;
        bottom: 0;
        height: 5em;
        width: 100%;
    
        background-color: black;
        color: white;
        text-align: center;
    
        display: flex;
        flex-direction: column;
        justify-content: center;
        
        & a {
            color: inherit;
            
        }
        & #credit {
            margin-top: 0.75em;
            font-size: 80%;
        }
    }
    ```

    ![image-20250322202153120](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322202153120.png)







#### main.js에서 .footer 속 #copyright 속 #year span태그의 내용(.innerHTML)에 현재 년도를 입력해주기

```JS
window.addEventListener('load', function(e) {
    document.querySelector('.footer #copyright #year').innerHTML = new Date().getFullYear() + ' ';
});
```

![image-20250322202717597](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322202717597.png)





### index.html -> see more버튼 -> blog 페이지로 이동



#### index.html 의 content 블락에 href="blog"로 a태그 추가

```html
{% extends "base.html" %}
{% block title %}{{title}}{% endblock %}

{% block content %}
<div class="posts-index">
    {% for post in posts[0:5] -%}
    
    
    {% endfor %}
</div>


<a class="btn-seemore" href="blog">See more</a>
{% endblock %}
```

- css추가

```css
.btn-seemore {
    color: white;
    background-color: var(--green);
    margin: 1em auto;
    padding: 1em;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
}
.btn-seemore:hover {
    filter: brightness(85%);
}

```

![image-20250322205252914](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322205252914.png)



- **클릭시 해당 path가 없으면 디렉토리로 뜬다.**

    ![image-20250322205311350](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322205311350.png)

### 버튼눌러가는 href="blog"에 대한 blog.html템플릿 -> blog/index.html을 만들어서 렌더링

1. posts들을 돌리기 때문에 index.html을 복사해서 blog.html을 만든다.

    - posts-index > post class 대신  for문안에서 post 1개의 post-preview가 클래스로 잡히고 처리된다.

    - **post.html에 있떤 authors에 대한 내용도 들어가 preview가 된다.**

        - 내용이 길기 때문에 components/authors.html로 빼자

        ![image-20250322210509885](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322210509885.png)

        - post.html

            ```html
            <!-- 작성자 -->
            {% if 'authors' in post['attributes'] %}
            {% include "components/authors.html" %}
            {% endif %}
            ```

    - index에 들어가던 posts  /  post에 들어가던 post내용 + 저작자로 구성된다.

        ```html
        {% extends "base.html" %}
        {% block title %}{{title}}{% endblock %}
        
        {% block content %}
        {% for post in posts[0:5] -%}
        <div class="post-preview">
            <div class="title">
                <a href="{{ post['attributes']['path'] }}">{{ post['attributes']['title']}}</a>
            </div>
            {% if post['attributes'].get('date_parsed') %}
            <div class="date">
                {{ post['attributes']['date_parsed'].strftime('%Y년 %m월 %d일') }}
            </div>
            {% endif %}
            <!-- 작성자 -->
            {% if 'authors' in post['attributes'] %}
            {% include "components/authors.html" %}
            {% endif %}
            <!-- 내용 -->
            <div class="article">
                {{ post['body'] | safe }}
            </div>
        </div>
        {% endfor %}
        
        {% endblock %}
        ```

        

    

    2. 이제 cli.py에서 blog.html 템플릿을 바탕으로 blog/index.html을 만든다.

        ```python
        ## render blog -> posts 전체 + index페이지 제목 + post에 있던 내용들
        blog = render_html('blog.html', config, env, posts, title='블로그')
        os.makedirs(os.path.join(OUTPUT_DIR, 'blog'), exist_ok=True)
        archive_path = os.path.join(OUTPUT_DIR, 'blog', 'index.html')
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(blog)
        ```

    3. base.html의 nav에  blog path 메뉴를 추가해준다.

        ```html
        <li><a href="{{ root_path }}blog">블로그</a></li>
        ```

        ![image-20250322211356119](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322211356119.png)

        

    4. **제목과 date, 저자외 내용이 너무 크게 차지한다. css**

        ```css
        /* blog.html -> blog/index.html */
        .post-preview .title {
            font-size: 2em;
            a {
                color: var(--green);
            }
            
            img {
                max-width: 100%;
            }
        }
        
        ```

        ![image-20250322212014495](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322212014495.png)

    





### blog.html에 보여질 summary를 만드는 절차

1. md에 `<!-- truncate -->` 주석을 넣고, 그 밑으로 잘릴 준비를 한다.

    ![image-20250322222259076](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322222259076.png)



2. post를 markdown.markdown으로 파싱후,  truncate가 포함되어있으면, 그 뒷부분을 잘라서 post 객체의 `summary`로 넣어준다

    ```python
    if '<!-- truncate -->' in post['body']:
        post['summary'] = post['body'].split('<!-- truncate -->')[0]
    ```

3. blog.html에서는 summary가 있을 경우, body 대신 summary로 아니면 body로 나오게 한다.

    ```html
     <!-- 내용 -->
        <div class="article">
            {% if 'summary' in post %}
            {{ post['summary'] | safe }}
            {% else %}
            {{ post['body'] | safe }}
            {% endif %}
        </div>
    ```

    ![image-20250322222942676](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322222942676.png)



4. 예외사항을 처리한다.

    ```python
    TRUNCATE_STRING = ['<!-- truncate -->', '<!--truncate-->']
    if any(truncate_tag in post['body'] for truncate_tag in TRUNCATE_STRING):
        for truncate_tag in TRUNCATE_STRING:
            if truncate_tag in post['body']:
                post['summary'] = post['body'].split(truncate_tag)[0]
                break
    ```

5. 더 고도화

    ```python
    TRUNCATE_STRING = [
        '<!-- truncate -->', '<!--truncate-->', 
        '<!--summary-->', '<!-- summary -->'
        '<!-- TRUNCATE -->', '<!--TRUNCATE-->', 
        '<!--SUMMARY-->', '<!-- SUMMARY -->'
    ]
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