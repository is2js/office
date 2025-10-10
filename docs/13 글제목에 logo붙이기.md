1. h3를 relative로 만들어서 before는 svg그림 / after는 logo이미지를 넣을 것이다.

    - 이 때, overflow: visible로해서 before/after가 h3 block의 높이를 넘어서도 보이게 만든다.

    ```css
    & h3 {
    
        /* 로고 추가 */
        position: relative;
        /*text-align: center;*/
        overflow: visible; /* 중요: ::before가 밖으로 나가도 잘리면 안 됨 */
    
    ```

2. 글자 바로 위에 로고를 띄우려면

    - **abs면서, 로고그림밑에 깔려야하니 가로제한+높이제한이 있어야한다.**

        ```css
        &::before {
            content: '';
            position: absolute;
            height: 4.5em;
            width: 250px;
            @media (max-width: 991px) {
                height: 4em;
                width: 200px;
            }
        ```

    - **h3글자의 바로 위에 띄워저야하니 bottom 100%에서 올리고, 왼쪽을 가운데 정렬한다.**

        ```css
        bottom: 110%; /* h3 바로 위에 붙임 */
        left: 50%;
        transform: translateX(-50%);
        ```

    - **background로 이미지를 미리 정해진 w/h안에 처리해야하며**

        - **logo이미지의 주소를 미리 base.html에 root변수로 넣어놔야 var()로 처리할 수 있다.**
        - **logo는 page마다 상대주소로 처리되어야되어야하므로, jinja로 처리되는 base.html에서 변수로 미리 넣어놓는다.** 

        ```html
        <style>
            :root {
                --logo-url: url("{{ static_path }}/img/logo.png");
            }
        </style>
        ```

        - **underline이미지이므로, `background-position: bottom`으로 밑에서부터 채우며, 반복되지 않는 배경을, `background-size: conatin;`으로 `더 긴 쪽에 맞춰서 들어가게` 만든다.**

        ```css
        background-image: var(--logo-url);
        /*background-position: center;*/
        background-position: bottom;
        background-size: contain;
        background-repeat: no-repeat;
        ```

3. 로고 밑에 밑줄을 SVG로 넣으려고 한다.

    - underline svg를 검색해서 저장하고
    - abs를 w/h제한을 둔다. w/h비율을 svg 크기에 맞게 준다.
    - 밑줄은 top에서 마이너스를 줘서 올라가게 하고, left는 가운데 정렬한다.

    ```css
    /* 로고 그림 밑줄 */
    &::after {
        content: '';
        position: absolute;
        /* 1412 136 */
        width: 141.2px;
        height: 136px;
        /*top: 100%; !* h3 바로 위에 붙임 *!*/
        top: -25%; /* 위에로고가 사람인 경우, 아랫줄을 가림 */
        @media (max-width: 991px) {
            /* 3/4 크기로 줄여줘 */
            width: 105.9px;
            height: 102px;
            top: -40%; /* 위에로고가 사람인 경우, 아랫줄을 가림 */
        }
    
        z-index: 1;
    
        left: 50%;
        transform: translateX(-50%);
    ```

    - **svg를 배경/mask로 넣어서, 메인색을 따라가게 변환한다.**

    ```css
    background-color: var(--theme-primary); /* 색상 적용 */
    background-position: center;
    -webkit-mask-image: url(./img/h3_underline.svg);
    mask-image: url(./img/h3_underline.svg);
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-size: contain;
    mask-size: contain;
    ```

    ![image-20250408080557177](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250408080557177.png)



4. 진하게 strong도 밑줄이 그이게 하려면

    - https://codepen.io/iam_aspencer/pen/qvNPBv
    - svg -> 색은 검은색 안주도록 변경 후 svg파일 저장하고
    - mask처리를 해주돼
    - left, right를 바로 근처까지 줘서 직접 나오게 하고
    - height를 일정하게 준다
    - z-index:-1을 줘서 글자보다 밑에 오게 하고
    - **contain이 아니라 cover로 더 긴 가로만큼 다 차지하게 만들고, strong > em이므로 em(이탤릭)을 안가진 경우 처리되게 만든다.**

    ```css
    &:not(:has(em))::after {
        content: '';
        position: absolute;
        bottom: -0.125rem;
        /*left: -0.5rem;*/
        /*right: -0.5rem;*/
        left: 0.1rem;
        right: 0.1rem;
        height: 0.65rem;
    
        z-index: -1;
    
        background-repeat: no-repeat;
        /*background-image: url('https://s3-us-west-2.amazonaws.com/s.cdpn.io/664131/underline.svg');*/
        /*background-size: cover;*/
        background-color: var(--theme-primary); /* 색상 적용 */
        -webkit-mask-image: url(./img/strong_underline.svg);
        mask-image: url(./img/strong_underline.svg);
        -webkit-mask-repeat: no-repeat;
        mask-repeat: no-repeat;
        -webkit-mask-size: cover;
        mask-size: cover;
    }
    
    ```

    ![image-20250408081441787](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250408081441787.png)







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