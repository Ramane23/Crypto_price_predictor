train:
	source ../../setup_credentials.sh && \
	python src/training.py

predict:
	source ../../setup_credentials.sh && \
	poetry run python src/predictor.py

api:
	source ../../setup_credentials.sh && \
	poetry run python src/api.py

request:
	curl -X POST http://127.0.0.1:5005/predict -H "Content-Type: application/json" -d '{"product_id":"BTC/USD"}'

invalid-request:
	curl -X POST http://127.0.0.1:5005/predict -H "Content-Type: application/json" -d '{"product_id":"ETH/USD"}'

copy-tools:
	cp -r ../../tools .

build: copy-tools
	docker build -t price-predictor-api .

run: build
	docker run \
		--env-file ../../credentials.env \
		-p 5005:80 \
		price-predictor-api

request-production:
	curl -X POST https://price-predictor-plabartabajo-realtimemlsystemcohort-e9f528c7.deployments.quix.io/predict -H "Content-Type: application/json" -d '{"product_id":"BTC/USD"}'