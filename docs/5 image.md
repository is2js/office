---
title: 피부미용
date: '2023-03-12'
---

### os.walk 순회시 사용자입력 docs폴더(SOURCE_DIR)안에 있는 이미지 파일을 > build/static/img로 가져온다

1. os.walk시 image파일들도 같이 모은다.

    - **md파일들 필터링 이전에 모아놔야한다.**

    ```python
    # def get_full_path_of_files_to_render():
    def get_full_path_of_files_to_render_and_images():
        full_path_of_files_to_render = []
        files_to_render_ignore = get_filenames_to_ignore()
    
        full_path_of_image_files = []
        
        for root, inner_dirs, file_names in os.walk(SOURCE_DIR):
    
            for file_name in file_names:
                full_path = os.path.join(root, file_name)
                file_basename = os.path.basename(full_path)
    
                # 11-1) renderignore 파일이면 pass
                if file_basename == '.renderignore':
                    continue
    
                ## 이미지 파일도 복사해놓기 (md파일 필터링 전)
                for image_type in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    if file_basename.lower().endswith(image_type):
                        print(f'  이미지 파일 >> {file_basename}')
                        full_path_of_image_files.append(full_path)
    
                # 11-2) md파일도 아니면서 .renderignore도 아닌 것 -> pass
                if not file_basename.lower().endswith('.md'):
                    print(f'  SOUR
                        
                        
                        
        return full_path_of_files_to_render, full_path_of_image_files
    
    
    def cli_entry_point():
        print(f"start ")
        # 1) source폴더명이 존재하고 && 그게 진짜 디렉토리라면,
        if not (os.path.exists(SOURCE_DIR) and os.path.isdir(SOURCE_DIR)):
            print(f"'{SOURCE_DIR}' 폴더가 존재하지 않습니다.")
            return
    
        # files_full_path_to_render = get_full_path_of_files_to_render_and_images()
        files_full_path_to_render, image_files_full_path = get_full_path_of_files_to_render_and_images()
    ```

    ![image-20250315204411623](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315204411623.png)
    ![image-20250315204419334](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315204419334.png)





### md작성시에 썼던 image 경로 -> re.sub()로 build/static/img로 바꿔서 render되어야한다.

1. docs의 md를 작성할 땐, docs폴더에 추가해놓고 쓴다.

    ```
    title: 'test4 youtube'
    path: /blog/4
    date: '2025-03-12'
    authors: [조재성]
    youtube: P_06Nvmunrk
    ---
    
    유튜브
    
    ![조원장](조원장_증명사진.png)
    ```

    ![image-20250315210704562](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315210704562.png)

    ![image-20250315210722737](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315210722737.png)

2. **하지만, build시에는 docs폴더가 아닌 `build / static / img` + `파일명`으로 받아져야한다.**

    ![image-20250315210901040](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315210901040.png)

    ![image-20250315210852752](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315210852752.png)

3. **그래서 jinja render시 build / static / img 로 빌드조건을 줘야한다.**

    - **내부빌드에서는 사용자입력폴더 docs까지 접근해야하는데, 아예 하지말자.??**
    - **외부빌드에서는 /static/img로 접근해야한다.**
    - **`상대root주소 = build폴더`를 만든 뒤 <-> `markdown 파싱` 전에 넣어주자.**

    ```python
    ## 외부 패키지 render시 이미지 경로 바꿔놓기
    # docs/조원장_증명사진.png ->  (현 blog/4) .. / .. /static/img/조원장_증명사진.png
    # ==> ..(blog) /..(build) / static / img / 조원장_증명사진.png
    if __name__ != '__main__':
        post['body'] = re.sub(
            r"\!\[(.+)\]\((.+)\)",
            f'![\\1]({os.path.dirname(os.path.dirname(relative_root_path))}/static/img/\\2)',
            post['body']
        )
    ```

    ![image-20250315222155532](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315222155532.png)

    ```
    <p><img alt="조원장" src="../../static/img/조원장_증명사진.png" />
    ```

    



4. **(src)부분이 http로 시작하는 경우는 제외시켜야한다.**

    - 2번째 그룹이 http로 안찾아지는 경우 에러가 발생해서 -> chatgpt에게 물어보고 바꿈

    ```python
    if __name__ != '__main__':
        # post['body'] = re.sub(
        #     r"\!\[(.+)\]\((.+)\)",
        #     f'![\\1]({os.path.dirname(os.path.dirname(relative_root_path))}/static/img/\\2)',
        #     post['body']
        # )
        # http로 시작하는 경우는 제외
        post['body'] = re.sub(
            r"!\[(.+)\]\((?!http)([^)]+)\)",
            lambda m: f'![{m.group(1)}]({os.path.dirname(os.path.dirname(relative_root_path))}/static/img/{m.group(2)})' if m.group(2)
            else m.group(0),
            post['body']
        )
    ```

    ```
    <p><img alt="조원장" src="../../static/img/조원장_증명사진.png" />	
    <img alt="김원장" src="https://front.chojaeseong.com/images/png/profile/main/01.png" /></p>
    ```





5. **같은 이미지주소를 가졌다면, 마지막 것만 변경 된다.**

    ![image-20250315230001570](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250315230001570.png)

    ```
    .+ → .+?: Greedy 매칭을 방지하여 정확한 부분만 매칭하도록 변경
    os.path.join() 사용: 경로 조합을 더 명확하게 만듦
    예제 경로 추가: relative_root_path를 예제로 지정하여 실행 가능하게 함
    ```

    ```python
    post['body'] = re.sub(
                    r"!\[(.+?)\]\((?!http)([^)]+)\)",
                    lambda
                        m: f'![{m.group(1)}]({os.path.join(os.path.dirname(os.path.dirname(relative_root_path)), "static/img", m.group(2))})'
                    if m.group(2) else m.group(0),
                    post['body']
                )
    ```

    

6. **md에서 외부 build폴더에 복사되는 `이미지의 이름이 중복`되지 않게 해야한다.**

    ```python
    ## copy static files and images
    # 외부에서 패키지로 사용시에만 == main실행 X:
    if __name__ != '__main__':
        # 1) 패키지실행 속 static(대문자STATIC_DIR) 파일들: build폴더 > static으로 복사
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))
    
        # 2) docs의 image파일들: build폴더> static > img폴더 > 파일명으로 복사
        os.makedirs(os.path.join(STATIC_DIR, 'img'), exist_ok=True)
        # 파일명은 1개만 있어야 한다.
        images_copied = {}
        for image_file_path in image_files_full_path:
            # Make sure the image name is unique
            image_filename = os.path.basename(image_file_path)
            if image_filename in images_copied:
                raise ValueError(
                    '중복된 이름의 이미지 파일이 있습니다: 변경해주세요',
                    image_file_path,
                    images_copied[image_filename])
                else:
                    images_copied[image_filename] = image_file_path
    
                    shutil.copy(image_file_path, os.path.join(OUTPUT_DIR, 'static', 'img', os.path.basename(image_file_path)))
    
    
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