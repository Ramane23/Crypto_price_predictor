run-dev:
	source ./setup_credentials.sh && \
	source ./setup_config.sh && \
	poetry run streamlit run src/frontend.py --server.runOnSave true

fetch-offline-data:
	source ./setup_credentials.sh && \
	source ./setup_config.sh && \
	poetry run python src/backend.py --offline

fetch-online-data:
	source ./setup_credentials.sh && \
	source ./setup_config.sh && \
	poetry run python src/backend.py --online

# Challenge: add run command that build and run the docker container
# You can use the same structure as the rest of the services.
# Important! Make sure you expose the port where the Streamlit app is running, so you
# can access it from outside the container.