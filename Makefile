install:
	uv sync

project:
	uv run project

run:
	uv run database

lint:
	uv run ruff check .

format:
	uv run ruff format .

build:
	uv build

publish:
	uv publish --dry-run

package-install:
	uv tool install --force dist/*.whl
