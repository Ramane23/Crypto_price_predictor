run-dev:
	@echo "Running with live.env"
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ./setup_live_config.sh && poetry run python src/main.py
	
run-dev-historical:
	@echo "Running with historical.env"
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ./setup_historical_config.sh && poetry run python src/main.py

build:
	docker build -t trade-to-ohlc .

run: build
	docker run \
		--name trade-to-ohlc \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env KAFKA_INPUT_TOPIC=trade \
		--env KAFKA_OUTPUT_TOPIC=ohlc \
		--env KAFKA_CONSUMER_GROUP=trade_to_ohlc_consumer_group \
		--env OHLC_WINDOW_SECS=60 \
		trade-to-ohlc
lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .

lint-and-format: lint format