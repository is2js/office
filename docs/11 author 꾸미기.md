- https://hostman.com/tutorials/how-to-use-python-markdown-to-convert-markdown-to-html/#troubleshooting-common-issues-during-conversion

![image-20250327085750898](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327085750898.png)





1. blog.html에 include된 components/authors.html을 수정한다.

    ```html
    <div class="authorContent">
        <div class="contentWrapper">
            <div class="textContent">
                <h2 class="medium">무엇이든 궁금한 것을 ,<br>편하게 여쭤보세요.</h2>
                <div class="text-secondary">Our professionals are available to assist you at any moment, <br>whether
                    you need help or are just unsure of where to start.
                </div>
            </div>
        </div>
        <div class="linkBtns">
            <a target="_self" href="mailto:tingstyle1@gmail.com"
               class="emailBtn">
                <div class="content">이메일</div>
            </a>
            <button class="chatBtn">
                <div class="content">카카오톡</div>
            </button>
        </div>
        <img alt="Hostman's Support" title="Hostman's Support Team"
             class="imageAbsoluteBottom--bBq3 lazyLoad isLoaded" style="height:464px;"
             src="https://front.chojaeseong.com/images/png/profile/sub/02.png">
    </div>
    ```

    ```css
    /* authors */
    .authorContent {
        background: #181f38;
        border-radius: 24px;
    
        position: relative;
        align-content: space-between;
        display: grid;
    
        box-sizing: border-box;
        margin: 0;
    
        padding: 72px 78px !important;
        height: 100%;
        gap: 32px;
    
        @media (max-width: 991px) {
            padding: 32px !important;
            gap: 24px;
        }
    
        & .contentWrapper {
            display: grid;
            gap: 16px;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
    }
    ```

    ![image-20250327091920535](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327091920535.png)

    

2. 조금씩 수정해나간다.

    ```css
    /* authors */
    .authorContent {
        /*background: #181f38;*/
        background: var(--green);
    
        border-radius: 24px;
    
        position: relative;
        align-content: space-between;
        display: grid;
    
        box-sizing: border-box;
        margin: 0;
    
        padding: 72px 78px !important;
        height: 100%;
        gap: 32px;
    
        @media (max-width: 991px) {
            padding: 32px !important;
            gap: 24px;
        }
    
        & .contentWrapper {
            display: grid;
            gap: 16px;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
    
            & .medium {
                font-style: normal;
                font-size: 36px;
                line-height: 42px;
                @media (max-width: 991px) {
                    font-size: 24px;
                    line-height: 32px;
                }
                color: #fff;
    
                font-weight: 500;
                letter-spacing: -.8px;
            }
    
            & .paragraph {
                /*color: #78819d;*/
                color: #d5d5da;
                font-weight: 400;
                font-style: normal;
    
                font-size: 19px;
                line-height: 24px;
                letter-spacing: -.5px;
                @media (max-width: 991px) {
                    font-size: 17px;
                    line-height: 22px;
                }
            }
        }
    
        & .linkBtns {
            --transition-all: all 200ms ease-in-out;
            transition: var(--transition-all);
    
            display: flex;
            gap: 8px;
            @media (max-width: 991px) {
                flex-direction: column;
            }
    
            box-sizing: border-box;
            margin: 0;
            padding: 0;
    
            & .emailBtn, & .chatBtn {
                text-decoration: none;
                cursor: pointer;
    
                font-weight: 600;
                color: #fff;
    
                display: flex;
                align-items: center;
                justify-content: center;
    
                border: none;
                border-radius: 12px;
                padding: 0 20px;
    
                font-size: 16px;
                letter-spacing: -.5px;
                line-height: 24px;
                height: 56px;
    
                @media (max-width: 991px) {
                    font-size: 15px;
                    line-height: 22px;
                    height: 48px;
                    padding: 0 16px;
                }
    
                &:hover {
                    opacity: 0.7;
                }
            }
    
            & .emailBtn {
                /*background: #0452f2;*/
                /*background: #181f38;*/
                background: var(--green-bold);;
            }
    
            & .chatBtn {
                /*background: #181f38;*/
                background: #FEE500;
                color: #3A1D1D;
            }
        }
    }
    ```

    ![image-20250327213547480](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327213547480.png)
    ![image-20250327213554610](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327213554610.png)





3. 이제 img를 absolute로 처리한다.

    - **그전에 글자와 para의 max-widht를 70%로 지정해놓고, 이미지는 30%의 width만 가지게 하자.**
        - 모바일말고
    - `.imgAbsoluteBottomRight`클래스로 만든다.

    ```css
        & .contentWrapper {
    
            & .medium {
                /* 모바일이상에선 abs이미지 30% 제외한 길이 제한*/
                @media (min-width: 992px) {
                    max-width: 70%;
                }
            }
    
            & .paragraph {
               /* 모바일이상에선 abs이미지 30% 제외한 길이 제한*/
                @media (min-width: 992px) {
                    max-width: 70%;
                }
    ```

    ```css
        & .imgAbsoluteBottomRight {
            position: absolute;
            bottom: 0;
            right: 0;
    
    		max-width: 30%;
            z-index: 1;
        }
    ```

    ![image-20250327214902508](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327214902508.png)

    ![image-20250327214920362](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250327214920362.png)



4. 모바일에선 max-width를 조금 낮이고, 데스크에선 그냥 w

    ```css
    /* 모바일이상에선 abs이미지에 대한 길이 제한*/
    & .medium, & .paragraph {
        max-width: 60%;
        @media (max-width: 991px) {
            max-width: 100%;
        }
    }
    
    & .imgAbsoluteBottomRight {
        position: absolute;
        bottom: 0;
        right: 0;
    
        max-width: 30%;
        @media (max-width: 991px) {
            max-width: 40%;
        }
        z-index: 1;
    }
    ```

    




5. 저자가 여러명인 경우는 안되므로, 1명만 쓰도록 바꿔주자.

    - 일단 config파일들에는 email과 kakakotalk을 넣어준다.

    ```yaml
    authors:
      조재성:
        name: 조재성 원장
        comment: 재활, 통계, 프로그래밍을 전공한 수석졸업 한의사입니다.
        email: tingstyle1@gmail.com
        kakaotalk: tingstyle@hanmail.net
      김석영:
    ```

    ```yaml
    authors:
      your_name:
        name: your_name 원장
        comment: 나는 한의사 입니다.
        email: your@mail.com
        kakaotalk: your@kakao.talk
    ```

6. components/authors.html를 복사해서 author.html을 만든다.

    - 기존 for authors문 속 author를 그대로 쓰기 위해, set으로 author변수를 지정하고 시작한다.

    - h2.medium에 원장이름을 적을 경우, 하이라이트 밑줄을 만든다.

        ```css
        & .medium {
        
            & .highlight {
                /*background: linear-gradient(to top, #FFEFC2 15%, transparent 15%);*/
                background: linear-gradient(to top, var(--green-bold) 25%, transparent 25%);
                width: fit-content;
            }
        }
        
        ```

        

    ```html
    {% set author = post['attributes']['author'] %}
    <div class="authorContent">
        <div class="contentWrapper">
            <div class="textContent">
                {% if author in config['authors'] %}
                <h2 class="medium">안녕하세요. <span class="highlight" >{{ config['authors'][author]['name'] }}</span>입니다.<br>
                    무엇이든 편하게 여쭤보세요.
                </h2>
                <div class="paragraph">{{ config['authors'][author]['comment'] }}<br>전문적인 지식을 바탕으로 상담과 의료서비스를 제공해드리겠습니다.
                </div>
                {% else %}
                <h2 class="medium">무엇이든 궁금한 것을,<br>편하게 여쭤보세요.</h2>
                <div class="paragraph">저희 병원은 양질의 서비스를 제공하기 위해 <br>지속적인 연구와 학습, 세미나를 진행하고 있습니다.
                </div>
                {% endif %}
            </div>
        </div>
        {% if author in config['authors'] %}
        <div class="linkBtns">
            <a target="_self" href="mailto:{{ config['authors'][author]['email'] }}"
               class="emailBtn">
                <div class="content">이메일</div>
            </a>
            <a target="_self" href="mailto:{{ config['authors'][author]['kakaotalk'] }}"
               class="chatBtn">
                <div class="content">카카오톡</div>
            </a>
    
        </div>
        <img alt="Hostman's Support" title="Hostman's Support Team"
             class="imgAbsoluteBottomRight"
             src="{{ config['authors'][author]['profileImg'] }}">
        {% endif %}
    </div>
    
    ```

7. post.html에서는 authors가 아니라 author를 확인해서 component내용을 가져온다.

    ```html
    {% if 'author' in post['attributes'] %}
    {% include "components/author.html" %}
    {% endif %}
    
    ```

8. md파일들의 authors들을 author로 바꾼다.

    ![image-20250328084010682](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250328084010682.png)



9. 각 요소들이 있을 때만 나타나게 한다.

    ```html
    {% if author in config['authors'] %}
    <div class="linkBtns">
        {% if 'email' in config['authors'][author] %}
        <a target="_self" href="mailto:{{ config['authors'][author]['email'] }}"
           class="emailBtn">
            <div class="content">이메일</div>
        </a>
        {% endif %}
        {% if 'kakao' in config['authors'][author] %}
        <a target="_self" href="mailto:{{ config['authors'][author]['kakaotalk'] }}"
           class="chatBtn">
            <div class="content">카카오톡</div>
        </a>
        {% endif %}
    </div>
    {% if 'profileImg' in config['authors'][author] %}
    <img alt="Hostman's Support" title="Hostman's Support Team"
         class="imgAbsoluteBottomRight"
         src="{{ config['authors'][author]['profileImg'] }}">
    {% endif %}
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