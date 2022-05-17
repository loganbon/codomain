import argparse
import bottle
import frontmatter, markdown
import logging
import os
import shutil

from jinja2 import Environment, FileSystemLoader
from paste import httpserver

_BUILD_DIR = '_build'

DEV = 'DEV'
PROD = 'PROD'

LOGGING_MODE_TO_LEVEL = {
    DEV: logging.DEBUG,
    PROD: logging.INFO
}


app = bottle.default_app()
logger = logging.getLogger(__name__)

def gen_files(in_dir: str, out_dir: str, jinja_env: Environment, verbose: bool):
    for loc in os.listdir(in_dir):
        sub_path = os.path.join(in_dir, loc)
        if os.path.isfile(sub_path):
            out_path = os.path.join(out_dir, loc)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            if sub_path.endswith('.md'):
                if verbose:
                    logging.info(f'[Codomain] Processing {sub_path}')
                page = frontmatter.load(sub_path)
                parsed_contents = markdown.markdown(page.content)
                template = jinja_env.get_template(page.metadata['layout'] + '.html')
                html = template.render(content=parsed_contents, **page.metadata)

                with open(out_path.replace('.md', '.html'), 'w') as fw:
                    fw.write(html)
            else:
                if verbose:
                    logging.info(f'[Codomain] Copying {sub_path}')
                shutil.copyfile(sub_path, out_path)
        else:
            gen_files(sub_path)

def build(input_dir: str, verbose: bool):
    logging.info('[Codomain] Building site ...')
    if os.path.exists(_BUILD_DIR):
        shutil.rmtree(_BUILD_DIR)
    jinja_env = Environment(loader=FileSystemLoader('layouts/'))
    gen_files(input_dir, _BUILD_DIR, jinja_env, verbose)
    logging.info('[Codomain] Site built')

def start(port: int, mode: str, hostname: str = '0.0.0.0'):
    logging.info(f'[Codomain] Server booting in mode {mode}...')
    if mode.upper() == PROD:
        httpserver.serve(app, host=hostname, port=port)
    else:
        bottle.run(app, host=hostname, port=port, debug=True)


Commands = {
    'build': build,
    'start': start,
}

def cli():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    build_parser = subparsers.add_parser('build')
    build_parser.add_argument('-i', '--input-dir', type=str, default='site')
    build_parser.add_argument('-v', '--verbose', action='store_true')

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('-p', '--port', type=int, default=8080)
    start_parser.add_argument('-m', '--mode', type=str, default='prod', choices=('dev', 'prod'))

    return parser.parse_args()


@app.route('/')
@app.route('/<filepath:path>')
def serve_static(filepath='index.html'):
    return bottle.static_file(f'{filepath}.html', root=_BUILD_DIR)


def main():
    args = cli()
    log_mode = args.mode.upper() if 'mode' in args else DEV
    logging.basicConfig(level=LOGGING_MODE_TO_LEVEL[log_mode])
    filtered_args = {k:v for k, v in args.__dict__.items() if k != 'command'}
    Commands[args.command](**filtered_args)


if __name__ == '__main__':
    main()
