from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import joblib
import os
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the trained model
MODEL_PATH = "flight_delay_model.joblib"

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print("❌ Model file not found. Please train the model first by running the training script.")
    model = None

@app.route('/')
def home():
    """Serve the frontend HTML"""
    # Read the HTML content (you'll need to save the HTML as a template)
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flight Delay Predictor</title>
        <!-- Include the CSS from the HTML artifact here -->
        <style>
            /* Copy the CSS from the HTML artifact */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            /* ... rest of CSS ... */
        </style>
    </head>
    <body>
        <!-- Copy the HTML body from the artifact -->
        <!-- Update the JavaScript to make actual API calls -->
        <script>
            document.getElementById('prediction-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result-container').classList.remove('show');
                
                const formData = new FormData(e.target);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = parseFloat(value) || value;
                }
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (result.error) {
                        alert('Error: ' + result.error);
                    } else {
                        showResult(result.prediction, result.probability);
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error connecting to server: ' + error.message);
                }
            });
            
            function showResult(prediction, probability) {
                const container = document.getElementById('result-container');
                const title = document.getElementById('result-title');
                const prob = document.getElementById('result-probability');
                
                if (prediction === 1) {
                    container.className = 'result-container result-delayed show';
                    title.textContent = '⚠️ Flight Likely to be Delayed';
                    prob.textContent = `Delay Probability: ${(probability * 100).toFixed(1)}%`;
                } else {
                    container.className = 'result-container result-ontime show';
                    title.textContent = '✅ Flight Likely On-Time';
                    prob.textContent = `On-Time Probability: ${((1 - probability) * 100).toFixed(1)}%`;
                }
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html_content)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    if model is None:
        return jsonify({'error': 'Model not available. Please train the model first.'}), 500
    
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'month', 'carrier', 'airport', 'arr_flights',
            'carrier_delay', 'weather_delay', 'nas_delay', 
            'security_delay', 'late_aircraft_delay'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create DataFrame with the input data
        input_data = pd.DataFrame([{
            'month': int(data['month']),
            'carrier': str(data['carrier']),
            'airport': str(data['airport']),
            'arr_flights': float(data['arr_flights']),
            'carrier_delay': float(data['carrier_delay']),
            'weather_delay': float(data['weather_delay']),
            'nas_delay': float(data['nas_delay']),
            'security_delay': float(data['security_delay']),
            'late_aircraft_delay': float(data['late_aircraft_delay'])
        }])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1]  # Probability of delay
        
        # Return results
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'delay_status': 'Delayed' if prediction == 1 else 'On-Time',
            'confidence': f"{probability * 100:.1f}%" if prediction == 1 else f"{(1-probability) * 100:.1f}%"
        })
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if model is None:
        return jsonify({'error': 'Model not available'}), 500
    
    try:
        # Get model information
        model_type = type(model.named_steps['classifier']).__name__
        feature_names = []
        
        # Try to get feature names and importances
        if hasattr(model.named_steps['classifier'], 'feature_importances_'):
            preprocessor = model.named_steps['preprocessor']
            numerical_features = ['month', 'arr_flights', 'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
            categorical_features = ['carrier', 'airport']
            
            try:
                cat_names = list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))
                feature_names = numerical_features + cat_names
                importances = model.named_steps['classifier'].feature_importances_
                
                # Create feature importance list
                feature_importance = [
                    {'feature': name, 'importance': float(imp)} 
                    for name, imp in zip(feature_names, importances)
                ]
                feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            except:
                feature_importance = []
        else:
            feature_importance = []
        
        return jsonify({
            'model_type': model_type,
            'feature_count': len(feature_names),
            'top_features': feature_importance[:10] if feature_importance else [],
            'status': 'Model loaded and ready'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting model info: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'message': 'Flight Delay Prediction API is running'
    })

if __name__ == '__main__':
    print("\n🚀 Starting Flight Delay Prediction Server...")
    print("📊 Model Status:", "✅ Loaded" if model is not None else "❌ Not Found")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📡 API Endpoints:")
    print("   • GET  /         - Frontend interface")
    print("   • POST /predict  - Make predictions")
    print("   • GET  /model-info - Model information")
    print("   • GET  /health   - Health check")
    print("-" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)