build:
	docker build -t trade-producer .

run: build
	# Specifies the container name
	# Connects the container to the specified Docker network
	# Sets environment variable for Kafka broker address
	# Sets environment variable for Kafka topic name
	# Sets environment variable for product IDs
	# Sets environment variable to indicate live or historical data
	docker run \
		--name trade_producer_instance \
		--network=redpanda_network \
		-e KAFKA_BROKER_ADDRESS=redpanda-0:9092 \
		-e KAFKA_TOPIC=trade \
		-e PRODUCT_IDS='["BTC/USD"]' \
		-e LIVE_OR_HISTORICAL=live \
		trade-producer  # The name of the Docker image to run

lint:
	poetry run ruff check --fix

format:
	poetry run ruff format .

lint-and-format: lint format