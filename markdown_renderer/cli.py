import datetime
import os.path
import re
import shutil
from pathlib import Path
from typing import Any

import frontmatter
import jinja2
import markdown
import yaml
from pygments.formatters.html import HtmlFormatter

from markdown_renderer.custom_table_extensions import CustomTableExtension
from markdown_renderer.lib import get_relative_root_path
from markdown_renderer.md_extensions import AlberandTagsExtension
from markdown_renderer.youtube_extentions import YouTubeEmbedExtension

if __name__ == '__main__':
    SOURCE_DIR = '../docs'  # 여기서 실행
else:
    SOURCE_DIR = 'docs'  # 패키지 설치후 mdr명령어로 사용자 실행

CONFIG_DIR_NAME = '.mdr'  # SOURCE_DIR 내부의 config 폴더

# OUTPUT_DIR = '../html'  # 상대경로
OUTPUT_DIR_NAME = 'build'  # 빌드는 패키지 내부/build 폴더 -> 패키지설치후 root의 build폴더
# 삭제
OUTPUT_DIR = OUTPUT_DIR_NAME

# TEMPLATE_DIR = 'md_templates'  # 템플릿도 패키지내부 폴더에서 제공할 것으로 지정

PACKAGE_DIR = os.path.dirname(__file__)  # 패키지 폴더이름 (내/외부 무관)
# 변경
# PACKAGE_DIR = Path(__file__).resolve().parent  # 패키지 폴더 절대경로(resolve)
# 추가
# OUTPUT_DIR = os.path.join(PACKAGE_DIR.parent, OUTPUT_DIR_NAME)

TEMPLATE_DIR = os.path.join(PACKAGE_DIR, 'md_templates')  # 템플릿도 패키지내부 폴더에서 제공할 것으로 지정
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')


################
# github actions 용 #
################
print(f"__name__  >> {__name__}")
print(f"SOURCE_DIR  >> {SOURCE_DIR}")
print(f"CONFIG_DIR  >> {CONFIG_DIR_NAME}")
print(f"PACKAGE_DIR  >> {PACKAGE_DIR}")
print(f"TEMPLATE_DIR  >> {TEMPLATE_DIR}")
print(f"OUTPUT_DIR  >> {OUTPUT_DIR}")
print(f"STATIC_DIR  >> {STATIC_DIR}")




TRUNCATE_STRING = [
    '<!-- truncate -->', '<!--truncate-->',
    '<!--summary-->', '<!-- summary -->',
    '<!-- TRUNCATE -->', '<!--TRUNCATE-->',
    '<!--SUMMARY-->', '<!-- SUMMARY -->'
]


def cli_entry_point():
    print(f"start ")
    # 1) source폴더명이 존재하고 && 그게 진짜 디렉토리라면,
    if not (os.path.exists(SOURCE_DIR) and os.path.isdir(SOURCE_DIR)):
        print(f"'{SOURCE_DIR}' 폴더가 존재하지 않습니다.")
        return

    # files_full_path_to_render = get_full_path_of_files_to_render_and_images()
    files_full_path_to_render, image_files_full_path = get_full_path_of_files_to_render_and_images()

    ## build폴더 삭제 미리 해놓기
    clear_output_dir()

    ## Load Config
    # - docs > .mdr > config.yml 읽기. 없으면 설치패키지 내부 폴더에서 가져오기
    config_file_path = os.path.join(SOURCE_DIR, CONFIG_DIR_NAME, 'config.yml')
    if not os.path.exists(config_file_path):
        config_file_path = os.path.join(TEMPLATE_DIR, 'default_config.yml')

    # 내부 실행: config_file_path  >> ../docs\.mdr\config.yml
    # 외부 실행: config_file_path  >> docs\.mdr\config.yml

    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        # print(f"config  >> {config}") # config  >> {'title': '상세질환 디자인(외부)'}

    posts = []  #
    post_paths = {}  # 모든 post에 대한 path들을 모은다. TODO: DB에서 검사
    redirects = []  # 기본paht외 추가로 갈 수 있는 path들을 모은다.

    categories = set()  # 1번째 path를 카테고리를 모아놓는다.
    # 4) 랜더할 md file들을 순회하면서, frontmatter 추출
    for file_full_path in files_full_path_to_render:
        with open(file_full_path, 'r', encoding='utf-8') as f:
            post = f.read()
            post = frontmatter.Frontmatter.read(post)  # c = frontmatter.loads(content) # 버전 차이?

            attributes = post.get('attributes')
            # 5) frontmatter없는 파일은 pass
            # if 'attributes' not in post:
            # if post.get('attributes') is None:
            if attributes is None:
                # {'attributes': None, 'body': '', 'frontmatter': '',
                # 'date', 'date_parsed', 'path' : '/blog/nested/post',
                # }
                # raise ValueError('해당파일에 frontmatter가 빠짐: ', file_full_path)
                # print(f'🤣 frontmatter가 없는 파일 수정 요망: {file_full_path}')  TODO: 임시로 출력 막음
                continue

            # print(f"attributes  >> {attributes}") TODO: 임시로 출력 막음


            ## front용 path지정(백엔드 달리면 필요 없을 듯)
            # 15-1) path 속성이 있다면, 파일명이 아니라, [path].html로 상대 경로를 지정한다.
            # if 'path' in post['attributes']:
            if 'path' in attributes:
                # 15-2) path는 중복이 아니여야 한다. TODO: 현재는 path별 index.html 1개밖에 못만듬.
                if attributes['path'] in post_paths:
                    # print(f'🤣 중복된 path를 가진 파일 : {file_full_path}')
                    # print(f'post_paths >> {post_paths}')
                    # continue
                    raise ValueError(f'중복된 path가 있습니다: {attributes["path"]}')
                # 15-3) 중복이 아닌 path는 True로 체크해서 추후 중복이 안되게 한다.
                post_paths[attributes['path']] = True


                ## 1번째 path를 카테고리로 모아놓기
                # path가 존재하고 "/" 단독이 아닌 경우 처리
                path = attributes.get('path')
                if path and path != "/":
                    path_parts = path.strip("/").split("/")  # 슬래시 제거 후 분할
                    if path_parts:
                        categories.add(path_parts[0])  # 첫 번째 요소를 카테고리로 추가

                # path를 가져 등록되었다면, redirects도 검사해서, 중복이 없으면 post_paths에 등록한다.
                if 'redirects' in attributes:
                    for redirect in attributes['redirects']:
                        if redirect in post_paths:
                            raise ValueError(f'중복된 redirect가 있습니다: {redirect}')
                        post_paths[redirect] = True


            else:
                # 15-4) path가 없으면, 파일명 .md ->.html 변경 기존 로직이 적용하는 file_full_path를 나중에 쓰기 위해
                #       file_full_path로 저장해놓는다.
                post['attributes']['file_full_path'] = file_full_path

            # 15-3) 'date' 속성을 검사하여 있다면, 'date_parsed' 속성으로 str -> datetime으로 바꿔 넣어놓는다.
            # if 'date' in post['attributes']:
            if 'date' in attributes:
                # 'date': 2023-02-20 -> datetime.date
                # 'date': '2023-02-20' -> string
                if isinstance(attributes['date'], str):
                    post['attributes']['date_parsed'] = datetime.datetime.strptime(attributes['date'], '%Y-%m-%d')
                else:
                    # q: 아래 값은 datetime.date이다. 이것을 datetime.datetime이면서 '%Y-%m-%d'으로 변환 by combine
                    # post['attributes']['date_parsed'] = post['attributes']['date'] # date
                    post['attributes']['date_parsed'] = datetime.datetime.combine(
                        attributes['date'],
                        datetime.datetime.min.time()
                    )  # datetime

                # 15-4) 근데, 발행날짜가 미래면, 무시하도록 한다.
                # 오늘 00시 발행법: datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
                # >> datetime.datetime(2025, 3, 8, 0, 0)
                if post['attributes']['date_parsed'] > datetime.datetime.combine(
                        datetime.date.today(),
                        datetime.datetime.min.time()
                ):
                    print(f'🤣 미래 날짜의 파일 : {file_full_path}')
                    continue

            posts.append(post)
            # 추가가 되는 post에 대해서는, tuple로 redirect_path와 기존 path를 넣어놓는다.
            if 'redirects' in post['attributes']:
                for redirect in post['attributes']['redirects']:
                    redirects.append((redirect, post['attributes']['path']))



    print(f"list(categories)  >> {list(categories)}")


    ## Render markdown to html
    # {
    #   'attributes': {'title': '넣었다'},
    #   'body': '- https://www.youtube.com/wat',
    #   'frontmatter': "\ntitle: '넣었다'\n"
    #   'date': 2025-03-20 <선택>
    #   'date_parsed': datetime <선택>
    # }
    # 12) 순회하며 f.read()할텐데, 그 전에, jinja2 env파일을 만들고, env.get_template()을 이용하여 채울 템플릿을 가져온다.
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
    content_template = env.get_template('post.html')

    # 16) render하기 전, post를 date_parsed로 정렬. 속성 없을 수도 있으니, .get()으로 가져온다.
    sorted(
        posts,
        key=lambda x: x['attributes'].get('date_parsed', datetime.datetime.min),
        reverse=True,
    )

    ## render post
    for i, post in enumerate(posts):
        # 17-1) init prev/next
        next_post, prev_post = process_init_prev_and_next_post(i, posts)

        # 18) 'path': /blog/nested/post 가 있으면, path + '/index.html'을 붙힌 상대주소를 만든다.
        if 'path' in post['attributes']:
            relative_path = post['attributes']['path'] + '/index.html'
        else:
            relative_path = post['attributes']['file_full_path'].replace(SOURCE_DIR, '').replace('.md', '.html')

        # 상대경로에선, 맨 앞에 '/'를 제거한다.
        if relative_path.startswith('\\') or relative_path.startswith('/'):
            relative_path = relative_path[1:]

        # print(f"relative_path  >> {relative_path}")
        # relative_path  >> 1 cli.html
        # relative_path  >> blog/nested/post/index.html

        # 19) root의 OUTPUT_DIR + [(/path/들)/index.html or 파일명.html] 상대경로 -> 폴더 없으면 생성까지
        # 폴더 없으면 만들어주기 for path
        output_file_full_path = os.path.join(OUTPUT_DIR, relative_path)
        os.makedirs(os.path.dirname(output_file_full_path), exist_ok=True)

        # print(f"  output_file >> {output_file_full_path}")
        #   output_file >> build\1 cli.html
        #   output_file >> build\blog/nested/post/index.html

        # 20) render template
        # html = markdown.markdown(post['body'])

        # 배포 전, 내부 실행 -> is_test=True -> 내부에서 ../ 갯수 줄이는 것 안함.
        if __name__ == '__main__':
            relative_root_path = get_relative_root_path(relative_path, is_test=True)
        else:
            relative_root_path = get_relative_root_path(relative_path)

        ## 외부 패키지 render시 이미지 경로 바꿔놓기
        # docs/조원장_증명사진.png ->  (현 blog/4) .. / .. /static/img/조원장_증명사진.png
        # ==> ..(blog) /..(build) / static / img / 조원장_증명사진.png
        if __name__ != '__main__':
            # post['body'] = re.sub(
            #     r"\!\[(.+)\]\((.+)\)",
            #     f'![\\1]({os.path.dirname(os.path.dirname(relative_root_path))}/static/img/\\2)',
            #     post['body']
            # )

            # http로 시작하는 경우는 제외
            post['body'] = re.sub(
                r"!\[(.+?)\]\((?!http)([^)]+)\)",
                lambda
                    m: f'![{m.group(1)}]({os.path.join(os.path.dirname(os.path.dirname(relative_root_path)), "static/img", m.group(2))})'
                if m.group(2) else m.group(0),
                post['body']
            )

        # post['body'] = markdown.markdown(post['body']
        #                                  , extensions=['fenced_code', 'codehilite'],
        #                                  extension_configs={
        #                                      'mdx_math': {
        #                                          'enable_dollar_delimiter': True,
        #                                      },
        #                                  },
        #                                  )

        MARKDOWN_EXTENSIONS = {
            # 'extensions': [AlberandTagsExtension(), 'extra', 'toc'], # extra 넣어야 테이블 가능.
            # 'extensions': ['extra', 'toc', 'fenced_code', 'codehilite'],  # extra 넣어야 테이블 가능.
            # 'extensions': [YouTubeEmbedExtension(), 'extra', 'toc', 'fenced_code', 'codehilite'],  # extra 넣어야 테이블 가능.
            'extensions': [YouTubeEmbedExtension(), CustomTableExtension(), 'extra', 'toc', 'fenced_code', 'codehilite'],  # extra 넣어야 테이블 가능.
            'extension_configs': {
                'markdown.extensions.extra': {},
                'markdown.extensions.meta': {},
            },
            'output_format': 'html5',
        }

        post['body'] = markdown.markdown(post['body'],
                                         **MARKDOWN_EXTENSIONS,
                                         )

        if any(truncate_tag in post['body'] for truncate_tag in TRUNCATE_STRING):
            for truncate_tag in TRUNCATE_STRING:
                if truncate_tag in post['body']:
                    post['summary'] = post['body'].split(truncate_tag)[0]
                    break

        # 내부/외부 달라서
        # - 내부 package_dir > template_dir > static_dir은 패캐지파일복사 절대경로라 X
        #   build 이후의 것이니, 상대경로로 static을 찾아야 한다.
        # - 외부 build_dir > static
        if __name__ == '__main__':
            static_path = os.path.join(relative_root_path, 'md_templates', 'static')
            # 내부 빌드 static_path  >> ../md_templates\static
        else:
            static_path = os.path.join(relative_root_path, 'static')
            print(f"외부빌드 static_path  >> {static_path}")
            # 외부빌드 static_path  >> ../static

        post_html = content_template.render(
            config=config,

            # static_dir='../md_templates/static',  # build폴더 path없는 것 기준 static 상대주소 경로
            root_path=relative_root_path,
            static_path=static_path,

            post=post,
            prev_post=prev_post,
            next_post=next_post,

            # title=post['attributes'].get('title', None),
            # subtitle=post['attributes'].get('subtitle', None),
            # date=post['attributes'].get('date', None),
        )
        with open(output_file_full_path, 'w', encoding='utf-8') as f:
            print(f" post 당첨 >> output_file_full_path")

            f.write(post_html)

    # def render_html(page, config, env, posts, title = 'Home')
    ## render index -> posts 전체 + index페이지 제목을 넘겨준다.
    index = render_html('index.html', config, env, posts, title='main')
    # print(f"config  >> {config}")
    # config  >> {'title': '조재성 원장', 'logoImg': 'http://hani.chojaeseong.com/images/logo.png', 'theme': {'primary': '#FC5230', 'sec
    # ondary': '#1ECECB'}, 'authors': {'조재성': {'name': '조재성 원장', 'comment': '재활, 통계, 프로그래밍을 전공한 수석졸업 한의사입니
    # 다.', 'email': 'tingstyle1@gmail.com', 'kakaotalk': 'tingstyle@hanmail.net', 'profileImg': 'https://front.chojaeseong.com/images/p
    # ng/profile/sub/02.png'}, '김석영': {'name': '김석영 원장', 'comment': '20년이상 저와 가족, 지인들에게 한약을 통한 치료를 제공해온
    # 한의사입니다.', 'email': 'daisykim88@gmail.com', 'kakaotalk': 'tingstyle@hanmail.net'}}, 'ads': {'isAutoPlay': False, 'autoPlayDur
    # ation': '1500,', 'pauseTimeoutDuration': '3000,', 'contents': {'광고1': {'type': 'image', 'url': 'https://front.chojaeseong.com/im
    # ages/png/profile/sub/02.png', 'title': '첫번째 영상', 'subtitle': 'ㅋㅋㅋㅋ'}, '광고2': {'type': 'video', 'youtubeId': '2Q0vX1r7g4
    # E', 'title': '조재성 원장', 'subtitle': '조재성 원장', 'isMute': False}, '광고3': {'url': 'https://front.chojaeseong.com/images/pn
    # g/profile/sub/02.png', 'title': None, 'subtitle': None}, '광고4': {'type': 'video', 'youtubeId': '2Q0vX1r7g4E', 'title': '조재성
    # 원장', 'subtitle': '조재성 원장', 'isMute': True}}}, 'footer': {'copyright': {'enabled': True, 'company': '(주) 김석영 주식회사'},
    #  'give_credit': True}, 'blog': {'titleLogoImg': 'https://front.chojaeseong.com/images/png/profile/sub/02.png'}, 'pagination': 5}
    # Serving HTTP on :: port 7777 (http://[::]:7777/)

    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index)

    ## render archive -> posts 전체 + index페이지 제목을 넘겨준다.
    archive = render_html('archive.html', config, env, posts, title='아카이브')
    # 새 페이지 -> path1개/index.htmlㅇ이어야한다.
    # 새 페이지 -> 경로가 없을 수 있으니 path1개의 경로도 만들어놔야한다.
    # archive_path = os.path.join(OUTPUT_DIR, 'archive.html')
    os.makedirs(os.path.join(OUTPUT_DIR, 'archive'), exist_ok=True)
    archive_path = os.path.join(OUTPUT_DIR, 'archive', 'index.html')
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(archive)

    ## render blog -> posts 전체 + index페이지 제목 + post에 있던 내용들

    # blog = render_html('blog.html', config, env, posts, title='블로그')
    # blog_path = os.path.join(OUTPUT_DIR, 'blog')
    # os.makedirs(blog_path, exist_ok=True)
    # blog_path = os.path.join(OUTPUT_DIR, 'blog', 'index.html')
    # with open(blog_path, 'w', encoding='utf-8') as f:
    #     f.write(blog)

    # pagination
    PAGINATION = config['pagination']
    for i in range(0, len(posts), PAGINATION):
        # i = 0, 4, 7 ...
        target_posts = posts[i:i + PAGINATION]
        prev_index = i - 1
        next_index = i + 1
        has_prev = prev_index >= 0
        has_next = next_index * PAGINATION < len(posts)
        pagination = {
            'prev_index': prev_index + 1,  # jinja에서는 1이 첫페이지
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
            # blog_path = os.path.join(OUTPUT_DIR, 'blog', f'{i // PAGINATION + 1}')
            # 이대로 가면 /blog/4 post와 /blog/4 페이지네이션이 똑같아져버린다.
            blog_path = os.path.join(OUTPUT_DIR, 'blog', 'page', f'{i // PAGINATION + 1}')
            # 강제로 중간path를 넣어줬다면, jinja에 쓰일 static도 / root_path도 한칸씩 이동 해야한다.
            # blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=1,
            blog = render_html('blog.html', config, env, target_posts, title='블로그', root_path_back_level=2,
                               **pagination,
                               )

        os.makedirs(blog_path, exist_ok=True)
        blog_path = os.path.join(blog_path, 'index.html')
        with open(blog_path, 'w', encoding='utf-8') as f:
            f.write(blog)

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


    ## render ads
    ads = render_html('ads.html', config, env, posts, title='아카이브')
    # 새 페이지 -> path1개/index.htmlㅇ이어야한다.
    # 새 페이지 -> 경로가 없을 수 있으니 path1개의 경로도 만들어놔야한다.
    # ads_path = os.path.join(OUTPUT_DIR, 'ads.html')
    os.makedirs(os.path.join(OUTPUT_DIR, 'ads'), exist_ok=True)
    ads_path = os.path.join(OUTPUT_DIR, 'ads', 'index.html')
    with open(ads_path, 'w', encoding='utf-8') as f:
        f.write(ads)

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

        ## codehiligt css를 pygments 모듈에서 가져와서 새로쓰기 (외부 전용ㄴ)
        formatter = HtmlFormatter()
        code_highlight_css = formatter.get_style_defs()
        with open(os.path.join(OUTPUT_DIR, 'static', 'code-highlights.css'), 'w') as f:
            f.write(code_highlight_css)


def clear_output_dir():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    # os.makedirs(OUTPUT_DIR)  # 폴더 다시 생성


def process_init_prev_and_next_post(i: int, posts: list[Any]) -> tuple[Any, Any]:
    prev_post = next_post = None
    # 아직 안끝났으면, next post객체를 넣어놓기
    if i < len(posts) - 1:
        next_post = posts[i + 1]
    # 0번째가 아니면, prev post객체를 넣어놓기
    if i > 0:
        prev_post = posts[i - 1]
    return next_post, prev_post


def render_html(page, config, env, posts, title='Home', root_path_back_level=0, **others):
    html_template = env.get_template(page)

    if __name__ == '__main__':
        # is_test=True -> 내부에서 ../ 갯수 줄이는 것 안함.
        index_relative_root_path = get_relative_root_path(page, is_test=True)
        static_path = os.path.join(index_relative_root_path, 'md_templates', 'static')
    else:
        index_relative_root_path = get_relative_root_path(page)
        static_path = os.path.join(index_relative_root_path, 'static')

        # 외부 빌드라도, root index는 상대주소가 default ../ + ../static이 아니라 ./ + ./static이 되어야 한다.
        # 지금 서버 띄울 땐 --directory build처리된 상태로 겉만 일케 띄워졌지만, 파일들 입장에선 build -> 루트 -> static으로 들어간다.
        # BUT github에선 아예 build폴더가 존재하지 않기 때문에 index.html에서 ../static이 되면 안된다. ./static이 되어야 한다.
        # 그래서 조건에 github actions용 환경변수로 판단해서 index.html일 때는 ../를 붙이지 않도록 한다.
        GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
        full_repo_name = os.getenv('GITHUB_REPOSITORY', '') # user/repo
        repo_name_only = full_repo_name.split('/')[-1] # repo
        if GITHUB_ACTIONS:
            if page == 'index.html':
                index_relative_root_path = './' # 강제로 build폴더없이 루트가 되는 상황이니 ./로 지정
                print(f"깃헙액션 index root_path >> {index_relative_root_path}")
            else:
                index_relative_root_path = os.path.join(repo_name_only, index_relative_root_path)
                static_path = os.path.join(index_relative_root_path, 'static')

                print(f"깃헙액션 not index root_path >> {index_relative_root_path}")







    print(f"page  >> {page}")
    print(f"index_relative_root_path  >> {index_relative_root_path}")
    print(f"static_path  >> {static_path}")

    # 강제로 중간에 path를 추가한다면 ex> pagination으로 blog/1 blog/2
    # static은 한칸 뒤로, 링크도 {{ root_path }} /원래 path가 연결되려면 현재에서 1칸 뒤로
    if root_path_back_level:
        index_relative_root_path = os.path.join('../' * root_path_back_level, index_relative_root_path)
        static_path = os.path.join('../' * root_path_back_level, index_relative_root_path, 'static')

    html = html_template.render(
        config=config,
        root_path=index_relative_root_path,
        static_path=static_path,
        title=title,
        posts=posts,
        **others if others else {}
    )
    return html


# def get_full_path_of_files_to_render():
def get_full_path_of_files_to_render_and_images():
    full_path_of_files_to_render = []
    files_to_render_ignore = get_filenames_to_ignore()

    full_path_of_image_files = []

    # 2) os.walk로 root, 내부dirs, files를 가져온다.
    for root, inner_dirs, file_names in os.walk(SOURCE_DIR):
        # print(root) # ../docs
        # print(inner_dirs)
        # print(file_names)
        # [] # ['1 cli.md']

        # 11) md파일인지 확인하기 전에
        # append될 file(상대경로)과, file의 맨 끝 파일명 file_basename을 이용하여 검사
        for file_name in file_names:
            full_path = os.path.join(root, file_name)
            file_basename = os.path.basename(full_path)

            # 11-1) renderignore 파일이면 pass
            if file_basename == '.renderignore':
                continue

            ## 이미지 파일도 복사해놓기 (md파일 필터링 전)
            for image_type in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                if file_basename.lower().endswith(image_type):
                    # print(f'  이미지 파일 >> {file_basename}') TODO: 임시로 출력 막음
                    full_path_of_image_files.append(full_path)

            # 11-2) md파일도 아니면서 .renderignore도 아닌 것 -> pass
            if not file_basename.lower().endswith('.md'):
                # print(f'  SOURCE_DIR 폴더에 md파일이 아닌 것이 존재 >> {file_basename}') TODO: 임시로 출력 막음
                continue

            # 11-3) 파일명이 .renderignore에 포함되어 있다면, pass
            if file_basename in files_to_render_ignore:
                # print(f"  제외된 파일 목록 >> {file_basename}") TODO: 임시로 출력 막음
                continue

            # 3) 파일명이 .md로 끝나는지 확인하고 그렇다면, root + filename을 합쳐서 파일 경로를 저장한다.
            # if filename.lower().endswith('.md'):
            full_path_of_files_to_render.append(full_path)

        # print(f"files_to_render  >> {full_path_of_files_to_render}") TODO: 임시로 출력 막음
    return full_path_of_files_to_render, full_path_of_image_files


def get_filenames_to_ignore():
    filenames_in_renderignore = []
    # 10) SOURCE_DIR에 .renderignore 파일이 존재하면 읽어서 모아둔다.
    render_ignore = os.path.join(SOURCE_DIR, '.renderignore')
    if os.path.exists(render_ignore):
        with open(render_ignore, 'r', encoding='utf-8') as f:
            filenames_in_renderignore = f.read().split('\n')
    return filenames_in_renderignore


if __name__ == '__main__':
    cli_entry_point()
