import datetime
import os.path
import shutil

import frontmatter
import jinja2
import markdown
import yaml

from markdown_renderer.lib import get_relative_root_path

if __name__ == '__main__':
    SOURCE_DIR = '../docs'  # 여기서 실행
else:
    SOURCE_DIR = 'docs'  # 패키지 설치후 mdr명령어로 사용자 실행

CONFIG_DIR = '.mdr'  # SOURCE_DIR 내부의 config 폴더

# OUTPUT_DIR = '../html'  # 상대경로
OUTPUT_DIR = 'build'  # 빌드는 패키지 내부/build 폴더 -> 패키지설치후 root의 build폴더

# TEMPLATE_DIR = 'md_templates'  # 템플릿도 패키지내부 폴더에서 제공할 것으로 지정
PACKAGE_DIR = os.path.dirname(__file__)  # 패키지 폴더이름 (내/외부 무관)
TEMPLATE_DIR = os.path.join(PACKAGE_DIR, 'md_templates')  # 템플릿도 패키지내부 폴더에서 제공할 것으로 지정
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')


def cli_entry_point():
    print(f"start ")
    # 1) source폴더명이 존재하고 && 그게 진짜 디렉토리라면,
    if not (os.path.exists(SOURCE_DIR) and os.path.isdir(SOURCE_DIR)):
        print(f"'{SOURCE_DIR}' 폴더가 존재하지 않습니다.")
        return

    files_full_path_to_render = get_full_path_of_files_to_render()

    ## build폴더 삭제 미리 해놓기
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    ## Load Config
    # - docs > .mdr > config.yml 읽기. 없으면 설치패키지 내부 폴더에서 가져오기
    config_file_path = os.path.join(SOURCE_DIR, CONFIG_DIR, 'config.yml')
    if not os.path.exists(config_file_path):
        config_file_path = os.path.join(TEMPLATE_DIR, 'default_config.yml')

    # 내부 실행: config_file_path  >> ../docs\.mdr\config.yml
    # 외부 실행: config_file_path  >> docs\.mdr\config.yml

    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        # print(f"config  >> {config}") # config  >> {'title': '상세질환 디자인(외부)'}


    posts = []  #

    post_paths = {}  # 모든 post에 대한 path들을 모은다. TODO: DB에서 검사
    # 4) 랜더할 md file들을 순회하면서, frontmatter 추출
    for file_full_path in files_full_path_to_render:
        with open(file_full_path, 'r', encoding='utf-8') as f:
            post = f.read()
            post = frontmatter.Frontmatter.read(post)  # c = frontmatter.loads(content) # 버전 차이?

            # 5) frontmatter없는 파일은 pass
            # if 'attributes' not in post:
            if post.get('attributes') is None:
                # {'attributes': None, 'body': '', 'frontmatter': '',
                # 'date', 'date_parsed', 'path' : '/blog/nested/post',
                # }
                # raise ValueError('해당파일에 frontmatter가 빠짐: ', file_full_path)
                print(f'🤣 frontmatter가 없는 파일 수정 요망: {file_full_path}')
                continue

            ## front용 path지정(백엔드 달리면 필요 없을 듯)
            # 15-1) path 속성이 있다면, 파일명이 아니라, [path].html로 상대 경로를 지정한다.
            if 'path' in post['attributes']:
                # 15-2) path는 중복이 아니여야 한다. TODO: 현재는 path별 index.html 1개밖에 못만듬.
                if post['attributes']['path'] in post_paths:
                    # raise ValueError(f'중복된 path가 있습니다: {post["path"]}')
                    print(f'🤣 중복된 path를 가진 파일 : {file_full_path}')
                    print(f'post_paths >> {post_paths}')
                    continue
                # 15-3) 중복이 아닌 path는 True로 체크해서 추후 중복이 안되게 한다.
                post_paths[post['attributes']['path']] = True
            else:
                # 15-4) path가 없으면, 파일명 .md ->.html 변경 기존 로직이 적용하는 file_full_path를 나중에 쓰기 위해
                #       file_full_path로 저장해놓는다.
                post['attributes']['file_full_path'] = file_full_path

            # 15-3) 'date' 속성을 검사하여 있다면, 'date_parsed' 속성으로 str -> datetime으로 바꿔 넣어놓는다.
            if 'date' in post['attributes']:
                # 'date': 2023-02-20 -> datetime.date
                # 'date': '2023-02-20' -> string
                if isinstance(post['attributes']['date'], str):
                    post['attributes']['date_parsed'] = datetime.datetime.strptime(post['attributes']['date'],
                                                                                   '%Y-%m-%d')
                else:
                    # q: 아래 값은 datetime.date이다. 이것을 datetime.datetime이면서 '%Y-%m-%d'으로 변환 by combine
                    # post['attributes']['date_parsed'] = post['attributes']['date'] # date
                    post['attributes']['date_parsed'] = datetime.datetime.combine(post['attributes']['date'], datetime.datetime.min.time()) # datetime

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
        prev_post = next_post = None
        # 아직 안끝났으면, next post객체를 넣어놓기
        if i < len(posts) - 1:
            next_post = posts[i + 1]
        # 0번째가 아니면, prev post객체를 넣어놓기
        if i > 0:
            prev_post = posts[i - 1]

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
        post['body'] = markdown.markdown(post['body'])

        # 배포 전, 내부 실행 -> is_test=True -> 내부에서 ../ 갯수 줄이는 것 안함.
        if __name__ == '__main__':
            relative_root_path = get_relative_root_path(relative_path, is_test=True)
        else:
            relative_root_path = get_relative_root_path(relative_path)

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
            f.write(post_html)


    # def render_html(page, config, env, posts, title = 'Home')
    ## render index -> posts 전체 + index페이지 제목을 넘겨준다.
    index = render_html('index.html', config, env, posts, title='상세질환 디자인')
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



    ## copy static files
    # - 외부에서 패키지로 사용시(main X) static도 build폴더>static으로 복사
    if __name__ != '__main__':
        shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))


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


def get_full_path_of_files_to_render():
    full_path_of_files_to_render = []
    files_to_render_ignore = get_filenames_to_ignore()

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

            # 11-2) md파일도 아니면서 .renderignore도 아닌 것 -> pass
            if not file_basename.lower().endswith('.md'):
                print(f'  SOURCE_DIR 폴더에 md파일이 아닌 것이 존재 >> {file_basename}')
                continue

            # 11-3) 파일명이 .renderignore에 포함되어 있다면, pass
            if file_basename in files_to_render_ignore:
                print(f"  제외된 파일 목록 >> {file_basename}")
                continue

            # 3) 파일명이 .md로 끝나는지 확인하고 그렇다면, root + filename을 합쳐서 파일 경로를 저장한다.
            # if filename.lower().endswith('.md'):
            full_path_of_files_to_render.append(full_path)

        print(f"files_to_render  >> {full_path_of_files_to_render}")
    return full_path_of_files_to_render


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
