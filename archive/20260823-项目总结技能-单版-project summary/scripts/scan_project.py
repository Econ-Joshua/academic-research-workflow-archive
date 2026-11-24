#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_project.py — 扫描项目目录，产出结构化 digest JSON（零 token 采集阶段）。

用法:
  python scan_project.py <项目路径> [-o digest_project.json] [--max-files 8000]

输出 JSON 字段: languages / frameworks / commands / entry_points / top_dirs /
readme / git(recent_commits, hot_files) / notes
仅使用标准库。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

EXCLUDE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env', 'dist',
    'build', '.idea', '.vscode', 'target', '.next', '.cache', 'vendor',
    'site-packages', '.tox', 'coverage', '.pytest_cache', '.mypy_cache',
    'obj', 'bin', '.gradle', '.terraform', 'bower_components',
}
LANG_EXT = {
    '.py': 'Python', '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.ts': 'TypeScript', '.tsx': 'TypeScript', '.jsx': 'JavaScript',
    '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.c': 'C', '.h': 'C header',
    '.cpp': 'C++', '.hpp': 'C++', '.cc': 'C++', '.cs': 'C#', '.rb': 'Ruby',
    '.php': 'PHP', '.sh': 'Shell', '.bash': 'Shell', '.zsh': 'Shell',
    '.ps1': 'PowerShell', '.sql': 'SQL', '.vue': 'Vue', '.svelte': 'Svelte',
    '.kt': 'Kotlin', '.swift': 'Swift', '.r': 'R', '.lua': 'Lua',
}
KNOWN_JS = {
    'react', 'vue', 'next', 'nuxt', 'express', 'koa', 'fastify', 'vite',
    'webpack', 'rollup', 'esbuild', 'electron', 'typescript', 'tailwindcss',
    'antd', 'element-ui', 'element-plus', 'lodash', 'axios', 'jest', 'vitest',
    'playwright', 'puppeteer', 'nestjs', '@nestjs/core',
}
KNOWN_PY = {
    'django', 'flask', 'fastapi', 'scrapy', 'requests', 'httpx', 'pandas',
    'numpy', 'scikit-learn', 'torch', 'tensorflow', 'uvicorn', 'gunicorn',
    'celery', 'sqlalchemy', 'pydantic', 'openai', 'anthropic', 'click',
    'typer', 'streamlit', 'gradio', 'pytest', 'beautifulsoup4', 'bs4',
}
BUILD_MARKERS = {
    'go.mod': 'go modules', 'Cargo.toml': 'cargo', 'pom.xml': 'maven',
    'build.gradle': 'gradle', 'build.gradle.kts': 'gradle', 'Gemfile': 'bundler',
    'composer.json': 'composer', 'CMakeLists.txt': 'cmake', 'setup.py': 'setuptools',
    'setup.cfg': 'setuptools', 'Pipfile': 'pipenv', 'poetry.lock': 'poetry',
}
ENTRY_NAMES = {
    'main.py', 'cli.py', 'app.py', 'server.py', 'manage.py', '__main__.py',
    'index.js', 'index.ts', 'main.go', 'main.rs', 'main.c', 'main.cpp',
    'index.html', 'wsgi.py', 'asgi.py',
}


def safe_read(path, limit=200_000):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(limit)
    except OSError:
        return ''


def git_out(root, *args):
    try:
        r = subprocess.run(
            ['git', '-C', str(root), *args],
            capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=25,
        )
        return r.stdout if r.returncode == 0 else None
    except Exception:
        return None


def iter_files(root, max_files):
    count = Counter()
    files = []
    truncated = False
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            if len(files) >= max_files:
                truncated = True
                return count, files, truncated
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            files.append(rel)
            count[LANG_EXT.get(p.suffix.lower(), p.suffix.lower() or '(无扩展名)')] += 1
    return count, files, truncated


def detect_frameworks(root, files):
    frameworks, managers, notes = [], [], []
    for rel in files:
        name = rel.split('/')[-1]
        if name in BUILD_MARKERS:
            managers.append(BUILD_MARKERS[name])
        if name == 'package.json':
            try:
                data = json.loads(safe_read(root / rel))
                deps = set(data.get('dependencies', {})) | set(data.get('devDependencies', {}))
                hit = sorted(d for d in deps if d in KNOWN_JS or d.split('/')[-1] in KNOWN_JS)
                frameworks.extend('node:' + h for h in hit)
                managers.append('npm')
            except (json.JSONDecodeError, OSError):
                notes.append('package.json 解析失败: ' + rel)
        elif name == 'requirements.txt':
            text = safe_read(root / rel)
            pkgs = {re.split(r'[<>=~!\[]', line.strip(), 1)[0].strip().lower()
                    for line in text.splitlines() if line.strip() and not line.startswith('#')}
            frameworks.extend('py:' + p for p in sorted(pkgs & KNOWN_PY))
            managers.append('pip')
        elif name == 'pyproject.toml':
            text = safe_read(root / rel)
            for pkg in KNOWN_PY:
                if re.search(r'["\']' + re.escape(pkg) + r'["\']', text):
                    frameworks.append('py:' + pkg)
            managers.append('pyproject')
    frameworks = sorted(set(frameworks))
    managers = sorted(set(managers))
    return frameworks[:25], managers[:8], notes


def extract_commands(root, files):
    commands = []
    for rel in files:
        name = rel.split('/')[-1]
        if name == 'package.json':
            try:
                data = json.loads(safe_read(root / rel))
                for k, v in list(data.get('scripts', {}).items())[:20]:
                    commands.append({'name': 'npm run ' + k, 'source': rel, 'cmd': str(v)[:120]})
            except (json.JSONDecodeError, OSError):
                pass
        elif name in ('Makefile', 'makefile', 'GNUmakefile'):
            text = safe_read(root / rel)
            for m in re.finditer(r'^([a-zA-Z0-9._/-]+):(?!=)', text, re.M):
                t = m.group(1)
                if t not in ('.PHONY', '.DEFAULT', '.SUFFIXES') and not t.startswith('.'):
                    commands.append({'name': 'make ' + t, 'source': rel, 'cmd': ''})
            if len(commands) > 40:
                commands = commands[:40]
        elif rel.startswith('.github/workflows/'):
            commands.append({'name': 'CI: ' + Path(rel).stem, 'source': rel, 'cmd': ''})
        elif name in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml'):
            commands.append({'name': 'docker compose up', 'source': rel, 'cmd': ''})
        elif name == 'Dockerfile':
            commands.append({'name': 'docker build', 'source': rel, 'cmd': ''})
    return commands[:40]


def entry_points(files):
    out = []
    for rel in files:
        if rel.split('/')[-1] in ENTRY_NAMES:
            out.append(rel)
    return out[:15]


def readme_info(root, files):
    for rel in files:
        name = rel.split('/')[-1].lower()
        if name in ('readme.md', 'readme.rst', 'readme.txt', 'readme') and rel.count('/') <= 1:
            text = safe_read(root / rel, 60_000)
            if not text:
                continue
            headings = re.findall(r'^#{1,3}\s+(.{1,80})', text, re.M)[:15]
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith('#')]
            summary = (lines[0][:300] if lines else '')
            return {'file': rel, 'headings': headings, 'summary': summary}
    return None


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description='扫描项目目录，产出结构化 digest JSON')
    ap.add_argument('project', help='项目根目录路径')
    ap.add_argument('-o', '--out', default=None, help='输出 JSON 文件路径（默认打印到 stdout）')
    ap.add_argument('--max-files', type=int, default=8000)
    args = ap.parse_args()

    root = Path(args.project).resolve()
    if not root.is_dir():
        print('错误: 不是有效目录: %s' % root, file=sys.stderr)
        sys.exit(2)

    count, files, truncated = iter_files(root, args.max_files)
    rel_files = files
    frameworks, managers, notes = detect_frameworks(root, rel_files)

    top_dirs = Counter(rel.split('/')[0] for rel in rel_files if '/' in rel)
    hot_files, recent_commits = [], []
    log = git_out(root, 'log', '--name-only', '--pretty=format:', '-n', '400')
    if log:
        fc = Counter(l.strip() for l in log.splitlines() if l.strip())
        hot_files = [{'file': f, 'changes': c} for f, c in fc.most_common(15)]
    oneline = git_out(root, 'log', '--oneline', '-n', '30')
    if oneline:
        recent_commits = [l[:100] for l in oneline.splitlines() if l.strip()][:30]
    if truncated:
        notes.append('文件数超过上限，结果为部分扫描')

    digest = {
        'schema': 'scan_project/1',
        'root': str(root),
        'file_count': len(rel_files),
        'languages': count.most_common(10),
        'frameworks': frameworks,
        'package_managers': managers,
        'commands': extract_commands(root, rel_files),
        'entry_points': entry_points(rel_files),
        'top_dirs': top_dirs.most_common(12),
        'readme': readme_info(root, rel_files),
        'git': {
            'is_repo': log is not None,
            'recent_commits': recent_commits,
            'hot_files': hot_files,
        },
        'notes': notes[:10],
    }
    text = json.dumps(digest, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print('已写入 %s (%d 文件, %d 语言)' % (args.out, len(rel_files), len(count)))
    else:
        print(text)


if __name__ == '__main__':
    main()
