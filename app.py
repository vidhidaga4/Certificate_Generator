import cv2
import pandas as pd
from flask import Flask, request, send_file, render_template
import io
import os

app = Flask(__name__)

# Load the CSV file with student data (ensure 'course' column exists)
df = pd.read_csv("student.csv")

# Dynamically get the absolute path to the certificate template
current_directory = os.path.dirname(os.path.abspath(__file__))
certificate_template = os.path.join(current_directory, 'Certificate_template.jpg')

# Font settings for OpenCV
font = cv2.FONT_HERSHEY_DUPLEX
font_scale_name = 2.5  # Reduced font size for name
font_thickness = 5  # Reduced thickness for better alignment
font_color = (255, 255, 255)  # Black color

# Route for the web form
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling the certificate generation
@app.route('/generate_certificate', methods=['POST'])
def generate_certificate():
    name = request.form.get('name')
    email = request.form.get('email')

    # Verify if the student exists in the CSV
    student = df[(df['name'] == name) & (df['email'] == email)]

    if not student.empty:
        
        # Generate the certificate
        certificate = create_certificate(name)

        # Return the generated certificate as a downloadable file
        return send_file(certificate, mimetype='image/png', as_attachment=True, download_name='certificate.png')

    else:
        # Student not found, return an error message
        return render_template('index.html', message="Student not found. Please check your details and try again.")

# Function to generate the certificate
def create_certificate(name):
    # Load the certificate template
    img = cv2.imread(certificate_template)

    # Get the size of the image
    img_height, img_width, _ = img.shape

    # Calculate text size and position for name
    text_size_name, _ = cv2.getTextSize(name, font, font_scale_name, font_thickness)
    text_width_name, text_height_name = text_size_name

    # Center the name text horizontally and position it vertically
    x_name = (img_width - text_width_name) // 2
    y_name = img_height // 2 - 190  # Adjust vertical position for the name

    # Add the student's name to the certificate
    cv2.putText(img, name, (x_name, y_name), font, font_scale_name, font_color, font_thickness, lineType=cv2.LINE_AA)

   
    # Save the certificate to an in-memory file (for download)
    certificate_io = io.BytesIO()
    is_success, buffer = cv2.imencode('.png', img)
    certificate_io.write(buffer)
    certificate_io.seek(0)

    return certificate_io

if __name__ == '__main__':
    app.run(debug=True)
