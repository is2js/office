import sys

import markdown


def print_usage():
    print(f"Usage:")
    print(f"  마크다운으로 사이트를 작성하는 과정")


def cli_entry_point():
    # cli + 옵션(sys.argv[1])으로 폴더를 추가해야하며, 아니라면 끝낸다.
    if len(sys.argv) == 2:
        ...
    else:
        print_usage()


if __name__ == '__main__':
    cli_entry_point()
    # print_usage()
    # print(markdown.markdown('#Hellow markdown'))
