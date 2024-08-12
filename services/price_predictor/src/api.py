# You can use Flask or FastAPI to create a REST API
from flask import Flask, request, jsonify

from predictor import Predictor

# list of crypto currencies we support for prediction
SUPPORTED_PRODUCT_IDS = ['BTC/USD']

app = Flask(__name__)

# If we want to serve predictions for more than 1 crypto currency, we can load the
# predictor for each one of them and store them in a dictionary
# I moved this code outside of the __name__ == '__main__' block to make sure it
# is executed when running this Flask app behind my gunicorn server
predictors = {
    product_id: Predictor.from_model_registry(product_id=product_id, status='production')
    for product_id in SUPPORTED_PRODUCT_IDS
}

# add an endpoint called health to check if the service is running
@app.route("/health")
def health():
    return "I am healthy!"

# add an endpoint called predict, post method
@app.route("/predict", methods=["POST"])
def predict():
    """
    Generates a prediction using the Predictor object and returns it as a JSON object
    """
    # Get the product_id from the request
    product_id = request.json.get('product_id')

    # # To avoid loading predictor that are not needed, just load them when they are requested and store them in a dictionary
    # # check if the product_id in the request has a predictor. If not, try to load it, and if this faisl return an error
    # if product_id not in predictors:
    #     try:
    #         predictors[product_id] = Predictor.from_model_registry(product_id=product_id, status='production')
    #     except ValueError as e:
    #         return jsonify({'error': str(e)}), 400

    # check if the product_id is supported
    if product_id not in SUPPORTED_PRODUCT_IDS:
        return jsonify({'error': f'Product {product_id} is not supported'}), 400

    # otherwise, we can proceed with the prediction
    predictor = predictors[product_id]

    output = predictor.predict()

    return jsonify(output.to_dict())

if __name__ == "__main__":

    # # If we want to serve predictions for more than 1 crypto currency, we can load the
    # # predictor for each one of them and store them in a dictionary
    # predictors = {
    #     product_id: Predictor.from_model_registry(product_id=product_id, status='production')
    #     for product_id in SUPPORTED_PRODUCT_IDS
    # }
    app.run(
        port=5005, 
        debug=True
        )