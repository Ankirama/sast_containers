#!/usr/bin/env python3
'''
sast_containers

Copyright 2022 Leboncoin
Licensed under the Apache License
Written by Fabien Martinez <fabien.martinez+github@adevinta.com>
'''
import argparse
from pathlib import Path
import json
import shlex
import subprocess
import logging
import tempfile
import shutil
import distutils.dir_util


BINARY_PATH = "/opt/phpcs_security/vendor/bin/phpcs"
RULESET_PATH = "/opt/phpcs_security/base_ruleset.xml"
IGNORE = [
    "*/tests/*",
    "*/vendor/*"
]
EXTENSIONS = [
    "php" #,cache,lib,...
]
REPORT_FORMAT = "json"
PHPCS_COMMAND = 'php "{binary_path}" --standard="{ruleset_path}" --extensions="{extensions}" --report="{report_format}" --report-file="{report_path}" --ignore="{ignore}" "{repo_path}"'

LOGGER = logging.getLogger('PHPCS')

REPO_PATH = Path("/opt/data/")
REPORT_PATH = Path("/opt/data/report.json")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--include', action='append', help='paths to specificaly include', default=[])
    parser.add_argument('-e', '--exclude', action='append', help='paths to exclude (like vendor and so on', default=[])
    args = parser.parse_args()
    return args


def check_default(repo_path, report_path, include_paths=[], exclude_paths=[]):
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdirname_path = Path(tmpdirname)
            if include_paths:
                for path in include_paths:
                    try:
                        distutils.dir_util.copy_tree(
                            str(repo_path / path),
                            str(tmpdirname_path / path)
                        )
                    except Exception as e:
                        LOGGER.error(f'Unable to copy {path}: {e}')
                        return False
            else:
                try:
                    distutils.dir_util.copy_tree(
                        str(repo_path),
                        str(tmpdirname_path)
                    )
                except Exception as e:
                    LOGGER.error(f'Unable to copy {repo_path}: {e}')
                    return False
                for path in exclude_paths:
                    if (tmpdirname_path / path).is_dir():
                        try:
                            shutil.rmtree((tmpdirname_path / path))
                        except Exception as e:
                            LOGGER.error(f'Unable to remove dir {tmpdirname_path / path}: {e}')
                            return False
                    elif (tmpdirname_path / path).is_file():
                        try:
                            (tmpdirname_path / path).unlink()
                        except Exception as e :
                            LOGGER.error(f'Unable to remove file {tmpdirname_path / path}: {e}')
                            return False
            if not execute_command(tmpdirname_path, report_path):
                return False
            else:
                return clean_report_tmp_path(tmpdirname_path, repo_path, report_path)
    except Exception as e:
        LOGGER.error(f'Unable to create tempdir: {e}', exc_info=True)
        return False


def clean_report_tmp_path(tmp_path, repo_path, report_path):
    try:
        report_content = json.loads(report_path.read_text())
    except Exception as e:
        LOGGER.error(f'Unable to clean report {report_path}: {e}')
        return False
    cleaned_files = {}
    tmp_path_str = str(tmp_path.absolute())
    repo_path_str = str(repo_path.absolute())
    for file_, content in report_content['files'].items():
        cleaned_files[f'{file_.replace(tmp_path_str, repo_path_str)}'] = content
    cleaned_content = {
        'totals': report_content['totals'],
        'files': cleaned_files
    }
    try:
        report_path.write_text(json.dumps(cleaned_content))
    except Exception as e:
        LOGGER.error(f'Unable to write in {report_path}: {e}')
        return False
    return True


def execute_command(repo_path, report_path):
    phpcs_command = PHPCS_COMMAND.format(
        binary_path=BINARY_PATH,
        ruleset_path=RULESET_PATH,
        extensions=",".join(EXTENSIONS),
        ignore=",".join(IGNORE),
        report_format=REPORT_FORMAT,
        report_path=str(report_path.absolute()),
        repo_path=str(repo_path.absolute())
    )
    command_splitted = []
    try:
        command_splitted = shlex.split(phpcs_command)
    except Exception as e:
        LOGGER.error(f'Unable to split command {phpcs_command}: {e}')
        return False
    try:
        subprocess.run(command_splitted)
    except Exception as e:
        LOGGER.error(f'Unable to execute command {command_splitted}: {e}')
        return False
    return True


def main():
    args = get_args()
    include_paths = args.include
    exclude_paths = args.exclude
    if not check_default(
        REPO_PATH,
        REPORT_PATH,
        include_paths,
        exclude_paths
    ):
        try:
            REPORT_PATH.write_text('{}')
        except Exception as e:
            LOGGER.error(f'Unable to create empty report ({REPORT_PATH}): {e}')


if __name__ == '__main__':
    main()
