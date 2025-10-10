1. md파일에서 `redirects: []`를 만들어, 접근할 수 있는 path를 추가한다.

    ```md
    title: 'test4 youtube'
    path: /blog/4
    date: '2025-03-12'
    author: 조재성
    youtube: P_06Nvmunrk
    redirects: [/treatments/1, /treatments/디스크]
    ```

    

2. cli.py에서 post_paths = {} 를 모아 검사하는 것처럼, redirects = []가 존재하면 모아놓고, post_paths랑 중복되면 에러를 낸다.

    - **path가 있는 post에 대해 redirects들도 기존 path와 중복 아니면 post_paths에 등록**

    ```python
    if 'path' in post['attributes']:
        if post['attributes']['path'] in post_paths:
            raise ValueError(f'중복된 path가 있습니다: {post["attributes"]["path"]}')
        post_paths[post['attributes']['path']] = True
    
        # path를 가져 등록되었다면, redirects도 검사해서, 중복이 없으면 post_paths에 등록한다.
        if 'redirects' in post['attributes']:
            for redirect in post['attributes']['redirects']:
                if redirect in post_paths:
                    raise ValueError(f'중복된 redirect가 있습니다: {redirect}')
                post_paths[redirect] = True
    
    ```

    - 확정된 post에 대해서는, tuple로 redirect_path와 기존 path를 넣어놓는다.

    ```python
    posts.append(post)
    #추가가 되는 post에 대해서는, tuple로 redirect_path와 기존 path를 넣어놓는다.
    if 'redirects' in post['attributes']:
        for redirect in post['attributes']['redirects']:
            redirects.append((redirect, post['attributes']['path']))
    ```

    



3. 이제 render하면서 tuple로 모아진 (redirect_path, path)를 순회하며 redirect_path에 `index.html`을 추가하여 문서를 작성한다.

    - 이 때, path처럼 redirect에 대해 상대주소를 만들어줘야한다.
    - target_path는 변수로서 jinja 변수로 render시 넘겨줄 것이다.
    - **redirect.html은 리다이렉트 + 타겟path 2개만 넘겨받아서, js로 자동이동 시킬 것이다.** 

    ```python
    ## render redirects
    for redirect_path, target_path in redirects:
        relative_redirect_path = redirect_path + '/index.html'
        # 상대경로에선, 맨 앞에 '/'를 제거한다.
        if relative_redirect_path.startswith('\\') or relative_redirect_path.startswith('/'):
            relative_redirect_path = relative_redirect_path[1:]
        if target_path.startswith('\\') or target_path.startswith('/'):
            target_path = target_path[1:]
    
        redirect_output_file_full_path = os.path.join(OUTPUT_DIR, relative_redirect_path)
        os.makedirs(os.path.dirname(redirect_output_file_full_path), exist_ok=True)
    
        if __name__ == '__main__':
            relative_root_path = get_relative_root_path(relative_redirect_path, is_test=True)
        else:
            relative_root_path = get_relative_root_path(relative_redirect_path)
    
        redirect_template = env.get_template('redirect.html')
        redirect = redirect_template.render(
            root_path=relative_root_path,
            target_path=target_path,
        )
        with open(redirect_output_file_full_path, 'w') as f:
            f.write(redirect)
    ```

    ```html
    
    You are being <a href="{{root_path}}{{ target_path }}">redirected</a> {{root_path}}
    <script>
    window.location.href = window.location.href + "{{ root_path }}{{ target_path }}";
    </script>
    
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