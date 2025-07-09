import re
import os
import subprocess
import inspect
from importlib.util import find_spec
from pathlib import Path as _Path
from typed.mods.types.base  import Str, Bool

def _install(lib, venv=None):
    """
    1. Find a .venv in some parent directory.
    2. Install a lib in runtime in the .venv if it is not
       already installed
    """
    if find_spec(lib) is not None:
        return

    if venv is None:
        current = _Path.cwd()
        found = False
        for parent in [current] + list(current.parents):
            possible = parent / '.venv'
            if possible.exists() and (possible / 'bin' / 'python').exists():
                venv = str(possible)
                found = True
                break
        if not found:
            return 'Error: No virtual environment found (.venv not located in parent directories)'

    if os.name == 'nt':
        pip_executable = os.path.join(venv, 'Scripts', 'pip.exe')
    else:
        pip_executable = os.path.join(venv, 'bin', 'pip')

    if not os.path.isfile(pip_executable):
        return f"Error: pip not found in the virtual environment at '{venv}'."

    try:
        subprocess.check_call([pip_executable, 'install', lib, '-q'])
        return f"'{lib}' has been installed in venv: {venv}"
    except subprocess.CalledProcessError as e:
        return f"Error installing '{lib}' in venv: {venv}. Detail: {str(e)}"

def _is_pure_markdown(content: Str) -> Bool:
    """
    Checks if a string is a pure markdown string, without a frontmatter.
    """
    _install('markdown')
    from markdown import markdown
    try:
        html = markdown(content)
        return True
    except Exception as e:
        return RuntimeError(f"Markdown could not be compiled: content={content}, error={e}")

def _is_markdown(content: Str) -> Bool:
    """
    Checks if a string is a markdown string, allowing and validating frontmatter.
    """
    _install('markdown')
    _install('pyyaml')
    from markdown import markdown
    import yaml

    frontmatter_pattern = re.compile(r'^\s*---\s*\n(?P<frontmatter>.*?)\n---\s*\n(?P<markdown_content>.*)', re.DOTALL)

    frontmatter_text = None
    markdown_body = content.strip()

    match = frontmatter_pattern.match(content)
    if match:
        frontmatter_text = match.group('frontmatter')
        markdown_body = match.group('markdown_content').strip()

        if frontmatter_text is not None:
            try:
                yaml.safe_load(frontmatter_text)
            except Exception as e:
                raise RuntimeError(f"Frontmatter could not be compiled: frontmatter={frontmatter_text}, error={e}")

    try:
        return markdown(markdown_body)
    except Exception as e:
        raise RuntimeError(f"Markdown body could not be compiled: content={markdown_body}, error={e}")
