---
title: 2번째 
date: '2025-03-09'
---





### 패키지 재설치
<!--truncate-->
1. 적용이 잘안되면, `외부라이브러리 > mdr-xxx`를 삭제하고

    ![image-20250309121917401](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309121917401.png)

2. `python setup.py install`을 수행한다.

3. `mdr`을 통해 docs폴더의 md를 처리했더니

    ```
    (.venv) PS C:\Users\cho_desktop\PycharmProjects\markdown> mdr                                 
    start 
    '../docs' 폴더가 존재하지 않습니다.
    ```

    - **패키지 내부가 기준으로 main실행될때는 패키지폴더가 루트가 되어서, `../`로 빠져나가야했지만, `패키지 설치 후에는 프로젝트 폴더가 기준`이 된다**



4. 경로를 `패키지내부 build -> (바깥)프로젝트 docs` 찾아가는 것을 `같은 폴더 docs찾아가는 것`으로 바꿔야한다.

    - **build폴더는, 없으면 생성되며, `패키지내부 << 프로젝트루트` 모두 가질 수 있다.**

    ```python
    if __name__ == '__main__':
        SOURCE_DIR = '../docs'  # 여기서 실행
    else:
        SOURCE_DIR = 'docs'  # 패키지 설치후 mdr명령어로 사용자 실행
        
    # OUTPUT_DIR = '../html'  # 상대경로
    OUTPUT_DIR = 'build'  # 빌드는 패키지 내부/build 폴더 -> 패키지설치후 root의 build폴더
    ```

5. PACKAGE_DIR이 경로가 바뀐다. **똑같이 패키지폴더를 의미한다( `내부생성 패키지 vs 외부설치 패키지`**

    - main실행시 패키지폴더 -> `설치 실행시, 외부패키지폴더`

    ```
    PACKAGE_DIR  >> C:\Users\cho_desktop\PycharmProjects\markdown\.venv\Lib\site-packages\mdr-1.0.0-py3.11.egg\markdown_renderer
    ```

    





### 홈페이지렌더링시 외부패키지 속 static파일 사용 불가 -> build폴더 내부로 static을  shutil로 복사해줘야한다.

- buiid에서 뒤로갔다 들어가는 template폴더가 아니라
- **외부 패키지로 사용하는 경우, `mdr명령어로 빌드시 build폴더`로 static을 복사해주자.**
    - 일단, 웹페이지를 띄울 땐, 내부패키지 static이 사용 불가다. 접근방법X
    - build에 해주면, 딱히 경로를 뒤로 안가도 되게 된다.

```python
## copy static files
# - 외부에서 패키지로 사용시(main X) static도 build폴더>static으로 복사
if __name__ != '__main__':
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))
```

```shell
python setup.py install
mdr
```



- 기존 삭제도, 내부vs외부를 



- 에러

    ```
    FileNotFoundError: [WinError 3] 지정된 경로를 찾을 수 없습니다: 'C:\\Users\\cho_desktop\\PycharmProjects\\markdown\\.venv\\Lib\\site-packages\\mdr-1.
    0.0-py3.11.egg\\markdown_renderer\\md_templates\\static'
    ```

- **패키지 설치시, static폴더가 외부패키지 폴더에 복사가 안되고 있다.**



1. manifest.in에 하위폴더도 명시한다.

    ```
    recursive-include markdown_renderer/md_templates *
    recursive-include markdown_renderer/md_templates/static *
    ```

2. setup.py의 package_data에서 구조를 바꾼다.

    ```python
    include_package_data=True,  # 중요!
    #   'markdown_renderer': ['md_templates/*']
    package_data={
        'markdown_renderer': ['md_templates/**/*']
    }
    ```

    ```
    python setup.py install
    mdr
    
    
    # gpt 명령어
    python setup.py sdist bdist_wheel
    pip install .
    ```

    

    ![image-20250309131542645](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309131542645.png)









### 이제 base.html에 쓰이던 packge_root_path도, 내부실행(../md_templates/static) vs 외부설치(build(./)>static)에 따라 다르게 뽑혀야한다.

- 내부 실행하여 필드한 것처럼 주소가 진행되어있음.

    ![image-20250309131849235](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309131849235.png)

- get_package_root_path -> get_root_path로 바꾼다.

    ```python
    relative_root_path = get_relative_root_path(relative_path)
    
    content = content_template.render(
        # static_dir='../md_templates/static',  # build폴더 path없는 것 기준 static 상대주소 경로
        root_path=relative_root_path,
    ```

    ```html
    <link rel="stylesheet" href="{{ root_path }}md_templates/static/style.css">
    ```

    - **내부빌드일때만, md_templates가 필요해서 서로 다르다.**

    ```python
    # 내부/외부 달라서
    # - 내부 package_dir > template_dir > static_dir은 패캐지파일복사 절대경로라 X
    # - 외부 build_dir > static
    if __name__ == '__main__':
    	static_path = os.path.join(relative_root_path, 'md_templates', 'static')
        print(f"내부 빌드 static_path  >> {static_path}")
    
    else:
    	static_path = os.path.join(relative_root_path, 'static')
    	print(f"외부 빌드 static_path  >> {static_path}")
    ```

    ```python
    content = content_template.render(
        # static_dir='../md_templates/static',  # build폴더 path없는 것 기준 static 상대주소 경로
        root_path=relative_root_path,
        static_path=static_path,
    
    ```

    ```html
    <link rel="stylesheet" href="{{ static_path }}/style.css">
    ```

    

    - 결과

    ```
    내부 빌드 static_path  >> ../md_templates\static
    ```

    ```html
    <link rel="stylesheet" href="C:\Users\cho_desktop\PycharmProjects\markdown\markdown_renderer\md_templates\static/style.css">
    
    ```

    

    

    ```
    post_relative_path.split('/')  >> ['2 cli 고쳐 프로젝트build + http.server 로 띄우기.html']
    num_dirs  >> 1
    외부빌드 static_path  >> ../static
    
    
    post_relative_path.split('/')  >> ['blog', 'nested', 'post', 'index.html']
    num_dirs  >> 4
    외부빌드 static_path  >> ../../../../static
    ```

    ```html
    <link rel="stylesheet" href="../static/style.css">
    ```

    

- **외부필드시에는, 한단계 뒤로갈 필요가 없다. build가 root가 되어야하므로 `파일1개` -> `root ../ (X)`가 되어야하므로 외부에서는 root를 build로 잡자.**

    ```
    post_relative_path.split('/')  >> ['1 cli.html']
    num_dirs  >> 1
    post_relative_path.split('/')  >> ['2 cli 고쳐 프로젝트build + http.server 로 띄우기.html']
    num_dirs  >> 1
    post_relative_path.split('/')  >> ['blog', 'nested', 'post', 'index.html']
    num_dirs  >> 4
    post_relative_path.split('/')  >> ['about', 'index.html']
    num_dirs  >> 2
    post_relative_path.split('/')  >> ['index.html']
    num_dirs  >> 1
    ```

- **외부패키지 렌더링시에는 `../`갯수가 1개 줄게 만들자.**

    - **외부파일이므로, nam main으로 판단 불가 -> 파라미터 주도록 바꾼다.**

    ```python
    def get_relative_root_path(post_relative_path):
    
        result = ''
        # Get the number of slashes
        num_dirs = len(list(filter(lambda x: len(x) > 0, post_relative_path.split('/'))))
    
        # 외부일때는 파일1개 index.html -> ../ 필요없이 그자리가 root
        # - 그자리 build폴더가 웹서버의 중심디렉토리가 될 것이기 때문.
        # 내부일 때는 파일1개 index.html -> ../ 의 build 바깥 md_templates 폴더가 root
        if __name__ != '__main__':
            num_dirs -= 1
    
        for i in range(num_dirs):
            result += '../'
    
        return result
    
    ```

    ```python
    def get_relative_root_path(post_relative_path, is_test=True):
        """
        외부 배포 말고, 내부에서 빌드할 때 is_test가 들어가서 ../ 갯수 1개 줄이기 
        """
        result = ''
        # Get the number of slashes
        num_dirs = len(list(filter(lambda x: len(x) > 0, post_relative_path.split('/'))))
    
        # 외부일때는 파일1개 index.html -> ../ 필요없이 그자리가 root
        # - 그자리 build폴더가 웹서버의 중심디렉토리가 될 것이기 때문.
        # 내부일 때는 파일1개 index.html -> ../ 의 build 바깥 md_templates 폴더가 root
        if not is_test:
            num_dirs -= 1
        #...
    ```

    

    ![image-20250309134657036](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309134657036.png)

    ![image-20250309134702815](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309134702815.png)
    - css 작동중







### build 디렉토리를 중심으로 기본웹서버 띄우기

```shell
python -m http.server --directory build
```

- 크롬창에 `localhost:8000`

    ![image-20250309134958765](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309134958765.png)

- index.html의 path링크도 잘 타지는 것 같다.

    ![image-20250309134850989](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309134850989.png)

    ![image-20250309134843909](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309134843909.png)







- md파일은 style.css까지 경로가 맞는데, 기본 index.html은 다르다.

    - **md -> post들은 상대경로로 root를 만들었지만, `index.html -> jinja렌더링 index.html`은 상대경로가 **
    - **template이 그대로 렌더링 될 때, 또 외부/내부 경로가 `./static`으로 동일함.**

    ![image-20250309135632502](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309135632502.png)

    



- **상대 루트경로가 현재폴더일 땐, `./`가 반환되도록 바꿔주고**

    ```python
    def get_relative_root_path(post_relative_path):
    
        result = ''
        # Get the number of slashes
        num_dirs = len(list(filter(lambda x: len(x) > 0, post_relative_path.split('/'))))
    
        # 외부일때는 파일1개 index.html -> ../ 필요없이 그자리가 root
        # - 그자리 build폴더가 웹서버의 중심디렉토리가 될 것이기 때문.
        # 내부일 때는 파일1개 index.html -> ../ 의 build 바깥 md_templates 폴더가 root
        if __name__ != '__main__':
            num_dirs -= 1
    
        for i in range(num_dirs):
            result += '../'
    
        # 현재위치일 땐 `./`으로 반환해주기
        if len(result) == 0:
            result = './'
            
        return result
    ```

    

- **index렌더링시 index.html 자체의 루트 + static(내부/외부동일)을 건네주자**

    ```python
    ## render index -> posts 전체 + index페이지 제목을 넘겨준다.
    index_template = env.get_template('index.html')
    
    # index.html의 루트 -> 내부/외부 동일하여 따로 작성하여 넘겨줌
    index_relative_root_path = get_relative_root_path('index.html')
    # print(f"index_relative_root_path  >> {index_relative_root_path}")
    # index_relative_root_path  >> ./
    
    index = index_template.render(
        root_path=index_relative_root_path,
        static_path=os.path.join(index_relative_root_path, 'static'),
        title='상세질환정보 디자인',
        posts=posts,
    )
    ```

    ![image-20250309140015713](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309140015713.png)

    ![image-20250309140028400](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309140028400.png)









### config 설정 for base.html 의 title태그 or nav(root)

1. **`docs`인 SOURCE_DIR에 ` .mdr > config.yml`을 읽어보고 -> 없으면 `패키지 내부 > template폴더 default_config.yml`을 사용하게 한다.**

2. 패키지 > md_templates > `default_config.yml`을 만든다.

    - 일단 title만 작성해놓는다.

    ![image-20250309222002987](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309222002987.png)

2. 사용자가 입력하는 `docs`에 **숨김폴더 `.mdr`폴더 > `config.yml`을 만들어놓는다.**

    ![image-20250309222302944](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309222302944.png)





3. 외부 유저입력 docs > .mdr > config.yml부터 읽고 아니면 내부껏을 읽게 코드를 짠다.

    ```python
    CONFIG_DIR = '.mdr'  # SOURCE_DIR 내부의 config 폴더
    
    ## Load Config
    # - docs > .mdr > config.yml 읽기. 없으면 설치패키지 내부 폴더에서 가져오기
    config_file_path = os.path.join(SOURCE_DIR, CONFIG_DIR, 'config.yml')
    if not os.path.exists(config_file_path):
        config_file_path = os.path.join(TEMPLATE_DIR, 'default_config.yml')
    
    print(f"config_file_path  >> {config_file_path}")
    # 내부 실행: config_file_path  >> ../docs\.mdr\config.yml
    # 외부 실행: config_file_path  >> docs\.mdr\config.yml
    
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        # print(f"config  >> {config}")
        # config  >> {'title': '상세질환 디자인(외부)'}
    ```

    

4. base의 title태그에 들어가니 **모든 template.render()에 다 넘겨줘야한다.**

    ```python
    content = content_template.render(
                config=config, 
    
    index = index_template.render(
        config=config,
        root_path=index_relative_root_path,
        static_path=os.path.join(index_relative_root_path, 'static'),
        title='상세질환정보 디자인',
        posts=posts,
    )
    ```

    ```html
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{{ static_path }}/style.css">
        <title>{% block title %}{% endblock %} | {{ config['title'] }}</title>
    </head>
    ```

    





5. base.html에  div 및 nav클래스 추가

    - root_path, config 사용 

    ```html
    <div class="nav">
        <a href="{{ root_path }}">{{ config['title'] }}</a>
    </div>
    <div>
        {% block content %}
        {% endblock %}
    </div>
    ```

    

6. **각 post들 뿐만 아니라, 인덱스도 동일하게, root_path + static_path를 계산해줘서 넘겨준다. **

    ```python
        # index.html의 루트 -> 내부/외부 동일하여 따로 작성하여 넘겨줌
        if __name__ == '__main__':
            index_relative_root_path = get_relative_root_path('index.html', is_test=True)
            static_path = os.path.join(index_relative_root_path, 'md_templates', 'static')
        else:
            index_relative_root_path = get_relative_root_path('index.html')
            static_path = os.path.join(index_relative_root_path, 'static')
    
    
    
        index = index_template.render(
            config=config,
            root_path=index_relative_root_path,
            static_path=static_path,
    ```

    





### index.html 꾸미기

- ul + for li 대신 div + for div  들로 가고, date를 추가한다.
- **index에서는 jinja에서도 인덱싱`[0:5]`로 5개만 돌아준다.**

```html
{% extends "base.html" %}

{% block content %}
<div class="posts-index">
	{% for post in posts[0:5] -%}
    <div class="post">
        <div class="title">
            <a href="{{ post['attributes']['path'] }}">{{ post['attributes']['title']}}</a>
        </div>
        <div class="date">
            {{ post['attributes']['date'] }}
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```



![image-20250309225812720](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250309225812720.png)



```css
/* index.html */
.posts-index {
    & .post {
        padding: 0.5em 0;
    }

    & .post .title {
        font-size: 150%;
    }
}
```

![image-20250311085305626](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311085305626.png)















### contents.html 꾸미기 (없음, 구조만)

```html
{% extends "base.html" %}

{% block title %}{{ post['attributes'].get('title', None) }}{% endblock %}

{% block content %}
{{ post['body'] | safe }}
{% endblock content %}
```





### cf) 

#### jinja2에서 sort: {% set 정렬데이터 = 데이터|sort(attribute='',reverse=True) %} -> 다시 순회

![image-20250311090346996](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311090346996.png)