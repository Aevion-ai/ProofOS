.PHONY: demo
demo:
	pip install -r requirements.txt && PYTHONPATH=src python3 -m aevion_runtime.demo
