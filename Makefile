.PHONY: demo
demo:
	pip install -r requirements.txt && PYTHONPATH=. python3 -m aevion_runtime.demo
