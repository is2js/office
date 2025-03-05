import os.path

import frontmatter
import markdown


def cli_entry_point():
    SOURCE_DIR = '../docs'  # 상대경로
    OUTPUT_DIR = '../html'  # 상대경로

    # 1) source폴더명이 존재하고 && 그게 진짜 디렉토리라면,
    if os.path.exists(SOURCE_DIR) and os.path.isdir(SOURCE_DIR):

        files_to_render = []

        files_to_render_ignore = []
        # 10) SOURCE_DIR에 .renderignore 파일이 존재하면 읽어서 모아둔다.
        render_ignore = os.path.join(SOURCE_DIR, '.renderignore')
        if os.path.exists(render_ignore):
            with open(render_ignore, 'r', encoding='utf-8') as f:
                files_to_render_ignore = f.read().split('\n')

        # 2) os.walk로 root, 내부dirs, files를 가져온다.
        for root, inner_dirs, file_names in os.walk(SOURCE_DIR):

            # print(root) # ../docs
            # print(inner_dirs)
            # print(file_names)
            # [] # ['1 cli.md']

            # 11) md파일인지 확인하기 전에
            # append될 file(상대경로)과, file의 맨 끝 파일명 file_basename을 이용하여 검사
            for file_name in file_names:
                file = os.path.join(root, file_name)
                file_basename = os.path.basename(file)

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
                files_to_render.append(file)

            print(f"files_to_render  >> {files_to_render}")

        # print(files_to_render) # ['../docs\\1 cli.md']

        # 4) 랜더할 md file들을 순회하면서, frontmatter를 뽑아내고, markdown으로 변환한다.
        for file_to_render in files_to_render:
            with open(file_to_render, 'r', encoding='utf-8') as f:
                content = f.read()
                # c = frontmatter.loads(content) # 버전 차이?
                post = frontmatter.Frontmatter.read(content)

                # 5) frontmatter없는 파일은 pass
                if not post['attributes']:
                    # {'attributes': None, 'body': '', 'frontmatter': ''}
                    print(f'  🤣 frontmatter가 없는 파일 수정 요망: {file_to_render}')
                    continue

                # {
                #   'attributes': {'title': '넣었다'},
                #   'body': '- https://www.youtube.com/wat',
                #   'frontmatter': "\ntitle: '넣었다'\n"
                # }

                # 6) frontmatter가 있는 파일은, markdown으로 변환후 html로 써서 저장한다.
                html = markdown.markdown(post['body'])

                # 7) md파일 경로 그대로, html로 바꿔서 저장
                # ->  OUTPUT_DIRSOURCE_DIR을 공백으로 대체 제거 + md를 html로 교체 2번 replace
                # output_file = os.path.join(OUTPUT_DIR, file_to_render.replace(SOURCE_DIR, '').replace('.md', '.html'))
                output_file = os.path.join(file_to_render.replace(SOURCE_DIR, OUTPUT_DIR).replace('.md', '.html'))

                # 8) 파일경로 + os.path.dirname() 경로를 만들어준다.
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                # 9) html로 변환된 내용을 파일에 쓴다.
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)






    else:
        print(f"'{SOURCE_DIR}' 폴더가 존재하지 않습니다.")


if __name__ == '__main__':
    cli_entry_point()
