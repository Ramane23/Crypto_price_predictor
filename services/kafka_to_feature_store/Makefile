run-dev:
	@echo "Running with live.env and credentials.env"
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ./setup_credentials.sh && \
	source ./setup_live_config.sh && \
	poetry run python src/main.py
	
run-dev-historical:
	@echo "Running with historical.env and credentials.env"
	KAFKA_BROKER_ADDRESS='localhost:19092' \
	source ./setup_credentials.sh && \
	source ./setup_historical_config.sh && \
	poetry run python src/main.py
	
build:
	docker build -t kafka-to-feature-store .

run: build
	docker run \
		--name kafka_to_feature_store \
		--network=redpanda_network \
		--env KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		--env KAFKA_TOPIC=ohlc \
		--env KAFKA_CONSUMER_GROUP=kafka_to_feature_store \
		--env FEATURE_GROUP_NAME=ohlc_feature_group_1 \
		--env FEATURE_GROUP_VERSION=1 \
		--env CREATE_NEW_CONSUMER_GROUP=true \
		--env HOPSWORKS_PROJECT_NAME=${HOPSWORKS_PROJECT_NAME} \
		--env HOPSWORKS_API_KEY=${HOPSWORKS_API_KEY} \
		kafka-to-feature-store
lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .

lint-and-format: lint format