from distutils.core import setup

setup(
    name='mdr',
    version='1.0.0',
    description='Markdown Renderer',
    author='JaeSeong Cho',
    author_email='tingstyle1@gmail.com',
    packages=['markdown_renderer'],
    entry_points={
        'console_scripts': [
            'mdr = markdown_renderer.cli:cli_entry_point'
        ],
    },
    install_requires=[
        'markdown',
        'frontmatter',
    ],
)