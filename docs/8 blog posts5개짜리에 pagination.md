### path에 pagination 적용

1. blog/ 진입후 **/blog/`page`/1 넣었을 때, /blog/`page`/2 넣었을 때 5개씩 이동**되어야한다.

2. cli.py에서 **render하기 전에 PAGINATION 설정**을 한다

3. **0부터 5개씩 건너뛰는 for문의 i로**

    - blog.html템플릿 바탕으로 -> blog / i / index.html을 만들어줘야한다.
    - **첫번째 0은 그냥으로 만들어줘야한다.**

4. 이 때, 강제로 path를 추가했기 때문에, render_html에서 **static_path**를 한칸 내려줘야하기 때문에 `../`더할 수 있도록 메서드에 장치를 넣어준다. **이 때, root_path도 이동되어야한다. 왜냐면 링크를 걸 때 {{root_path}} /blog /2 형태로 들어가기 때문**

    - move된 갯수만큼 넣어주도록 한다.

    ```python
    def render_html(page, config, env, posts, title='Home', root_path_back_level=0, **others):
        html_template = env.get_template(page)
    
        if __name__ == '__main__':
            index_relative_root_path = get_relative_root_path(page, is_test=True)
            static_path = os.path.join(index_relative_root_path, 'md_templates', 'static')
        else:
            index_relative_root_path = get_relative_root_path(page)
            static_path = os.path.join(index_relative_root_path, 'static')
    
        # 강제로 중간에 path를 추가한다면 ex> pagination으로 blog/1 blog/2 
        # static은 한칸 뒤로, 링크도 {{ root_path }} /원래 path가 연결되려면 현재에서 1칸 뒤로
        if root_path_back_level:
            index_relative_root_path = os.path.join('../' * root_path_back_level, index_relative_root_path)
            static_path = os.path.join('../' * root_path_back_level, index_relative_root_path, 'static')
            
    	# ...
    ```

5. test를 위해 pagination을 3개만 넣는다.

    ```python
        # pagination
        PAGINATION = 3
        for i in range(0, len(posts), PAGINATION):
            target_posts = posts[i:i + PAGINATION]
    
            # i = 0 일 때는 그냥 blog
            if i == 0:
                blog_path = os.path.join(OUTPUT_DIR, 'blog')
                blog = render_html('blog.html', config, env, target_posts, title='블로그',
                                   **pagination,
                                   )
            else:
                blog_path = os.path.join(OUTPUT_DIR, 'blog', f'{i // PAGINATION + 1}')
                # 강제로 중간path를 넣어줬다면, jinja에 쓰일 static도 / root_path도 한칸씩 이동 해야한다.
                blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=1)
    
            os.makedirs(blog_path, exist_ok=True)
            blog_path = os.path.join(blog_path, 'index.html')
            with open(blog_path, 'w', encoding='utf-8') as f:
                f.write(blog)
    ```

    ![image-20250323104825795](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323104825795.png)



6. pagination 갯수를 config.yml에서 설정하게 넣어준다. default에도 넣어주자.

    ```yml
    PAGINATION = config['pagination']
    ```

    ```yml
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
    
    
    pagination: 3
    ```

    



### pagination 버튼 적용

1. cli.py에서 현재 page번호인 `i`에 1뺀것 / 1더한 `prev, next_index`를 만들고, `has_prev, next`를 조건문을 통한 boolean으로 넘겨야한다.

    - **has_next는 페이지번호 x PAGINATION 갯수가, 전체 posts갯수보다 작아야만 존재한다.**
        - ex> 4개 -> 페이지인덱스 1(path번호는 2) -> 1x3 <4로서 다음 페이지 인덱스 1을 가진다.

    ```python
    # pagination
    PAGINATION = config['pagination']
    for i in range(0, len(posts), PAGINATION):
        target_posts = posts[i:i + PAGINATION]
        prev_index = i - 1
        next_index = i + 1
        has_prev = prev_index >= 0
        has_next = next_index * PAGINATION < len(posts)
    ```

2. **이제 render_html에 pagination여부도 적어주고 -> TRUE면 인자를 추가해서 `인덱스2, 여부2`를 모두 넘겨줘야한다.**

    - otehrs None파라미터 -> 객체로 넘겨주고, **있다면 풀어헤쳐지도록 하자**
    - 외부에서는 `\*\*dict`형태로 집어넣으면 메서드 내부에는 파리미터들로 들어오는데 그대로 풀어헤치자.
    - **`jinja에서 사용될 prev_index와 next_index는 +1된 값`이며 jinja에서 1일 경우가 첫페이지다.**

    ```python
    def render_html(page, config, env, posts, title='Home', static_path_move=0, **others):
    	#...
        html = html_template.render(
            config=config,
            root_path=index_relative_root_path,
            static_path=static_path,
            title=title,
            posts=posts,
            **others if others else {}
        )
    ```

    ```python
    pagination = {
        'prev_index': prev_index - 1, # jinja에서는 1이 첫페이지
        'next_index': next_index + 1,
        'has_prev': has_prev,
        'has_next': has_next,
    }
    
    # i = 0 일 때는 그냥 blog
    if i == 0:
        blog_path = os.path.join(OUTPUT_DIR, 'blog')
        blog = render_html('blog.html', config, env, target_posts, title='블로그',
                           **pagination,
                          )
        else:
            blog_path = os.path.join(OUTPUT_DIR, 'blog', f'{i // PAGINATION + 1}')
            # 강제로 중간path를 넣어줬다면, jinja에 쓰일 static도 / root_path도 한칸씩 이동 해야한다.
            blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=1,
                               **pagination,
                              )
    ```

    

3. blog.html에서 테스트

    ```html
    {% endfor %}
    {{prev_index}}
    {{next_index}}
    {{has_prev}}
    {{has_next}}
    {% endblock %}
    ```

    ![image-20250323113356129](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323113356129.png)

    

    ```
    http://localhost:8000/blog/2/
    ```

    ![image-20250323113406974](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323113406974.png)





4. html 꾸미기

    - has_prev를 가졌는데 **이전 index가 1이라면, path가 그냥 `/blog`으로 가야하고**
    - has_next를 가졌다면 해당 index로 가면 된다.

    ```html
    {% if  has_prev %}
     {% if prev_index == 1 %}
    <a class="btn-seemore" href="{{root_path}}blog/">최신 POST</a>
    
     {% else %}
    <a class="btn-seemore" href="{{root_path}}blog/{{prev_index}}">최신 POST</a>
    
     {% endif %}
    {% endif %}
    
    {% if  has_next %}
    <a class="btn-seemore" href="{{root_path}}blog/{{next_index}}">이전 POST</a>
    {% endif %}
    
    {% endblock %}
    ```

    ![image-20250323140244984](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323140244984.png)

    ![image-20250323140236488](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323140236488.png)





### 버그 수정

- /blog/4 포스트와  /blog/page/4 페이지가 같아져버림. 뒤늦게 렌더링되는 페이지네이션 페이지가 post를 덮어버린다.

1. ㅁㄴㅇㄹ

    ```python
    # i = 0 일 때는 그냥 blog
    if i == 0:
        blog_path = os.path.join(OUTPUT_DIR, 'blog')
        blog = render_html('blog.html', config, env, target_posts, title='블로그',
                           **pagination,
                           )
    else:
        # blog_path = os.path.join(OUTPUT_DIR, 'blog', f'{i // PAGINATION + 1}')
        # 이대로 가면 /blog/4 post와 /blog/4 페이지네이션이 똑같아져버린다.
        blog_path = os.path.join(OUTPUT_DIR, 'blog', 'page', f'{i // PAGINATION + 1}')
        # 강제로 중간path를 넣어줬다면, jinja에 쓰일 static도 / root_path도 한칸씩 이동 해야한다.
        # blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=1,
        blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=2,
                           **pagination,
                           )
    ```

    ```html
    {% if  has_prev %}
    {% if prev_index == 1 %}
    <a class="btn-seemore" href="{{root_path}}blog/">최신 POST</a>
    
    {% else %}
    <a class="btn-seemore" href="{{root_path}}blog/page/{{prev_index}}">최신 POST</a>
    
    {% endif %}
    {% endif %}
    
    {% if  has_next %}
    <a class="btn-seemore" href="{{root_path}}blog/page/{{next_index}}">이전 POST</a>
    {% endif %}
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