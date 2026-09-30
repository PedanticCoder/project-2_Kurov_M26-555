install:
	poetry install
	
package-install:
	python3 -m pip install dist/*.whl --force-reinstall
	
build:
	poetry build
	
publish:
	poetry publish --dry-run
	
project:
	poetry run project
	
lint:
	poetry run ruff check .
