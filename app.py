from flask import Flask, jsonify, request, abort
import weather_request

app = Flask(__name__)

app.json.sort_keys = False

@app.route('/')
def home_page():
    return 'Weather API for ITEC 2454'

@app.route('/weather/<location>')
def weather_for_location(location):
    # geocode location, return weather for most likely place 
    
    error, forecast = weather_request.forecast(location)
    if forecast:
        return jsonify(forecast)
    else:
        return jsonify({'error': error})

@app.errorhandler(404)
def not_found(error):
    return 'Page not found.', 404