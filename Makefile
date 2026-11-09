.PHONY: test benchmark run lint
run:
	uvicorn naviqra.api:app --reload

test:
	pytest -q

benchmark:
	python benchmarks/run_benchmark.py

lint:
	ruff check naviqra tests benchmarks
