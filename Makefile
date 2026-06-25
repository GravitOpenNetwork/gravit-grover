# Makefile
.PHONY: install test clean run-cluster

install:
	pip install -e .[dev]

test:
	pytest tests/ -v

run-cluster:
	python cli/run_network.py --nodes 3 --port 50051

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info

notebook:
	jupyter notebook experiments/notebooks/
