from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfReader
import os
import openai
from config import api_key
import subprocess
import time 
import argparse


# Rest of your code

# Define the "files" folder path
files_folder = 'files'
app = Flask(__name__)
# Directory to monitor for incoming PDF files
input_directory = 'input_pdfs/'
def extract_text_from_pdf(pdf_file_path):
    try:
        # Use OpenAI's GPT-3 to extract text from the PDF
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Extract text from PDF: '{pdf_file_path}'",
            max_tokens=150,
        )
        extracted_text = response.choices[0].text
        # Save the extracted text to a text file
        text_file_path = f'output_texts/{os.path.basename(pdf_file_path)}.txt'
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        print(f"Text extracted and saved to '{text_file_path}'")
    except Exception as e:  
        print(f"An error occurred: {str(e)}")
def save_text_to_file(text):
    # Create the "files" folder if it doesn't exist
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
    # Generate a unique filename based on the current timestamp
    timestamp = int(time.time())  # Get current timestamp
    file_name = f'text_{timestamp}.txt'
    # Define the file path in the "files" folder
    file_path = os.path.join(files_folder, file_name)
    # Write the text to the file
    with open(file_path, 'w') as file:
        file.write(text)
# Sample initial extracted text (you would replace this with your actual data source)
extracted_text = "Initial extracted text goes here."
@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    if request.method == "POST":
        uploaded_file = request.files["pdf_file"]
        if uploaded_file.filename != "":
            try:
                # Use the original PDF file name for the text file
                pdf_file_name = uploaded_file.filename
                # Read the PDF and extract text
                summary = "Summary goes here"
                pdf_text = ""
                pdf = PdfReader(uploaded_file)
                for page in pdf.pages:
                    pdf_text += page.extract_text()
                # Save the extracted text to a file with its original name
                save_text_to_file(pdf_file_name, pdf_text)
                # Extracted text can be used in other parts of the application
                # For now, we'll just redirect to the display page with the extracted text
                return redirect(url_for('notepad_display', extracted_text=pdf_text,summary=summary))
            except Exception as e:
                extracted_text = f"An error occurred: {str(e)}"
    # Add a return statement to render the HTML template when the method is GET
    return render_template('index.html')
@app.route("/notepad_display")
def notepad_display():
    extracted_text = request.args.get("extracted_text", default="", type=str)
    return render_template('notepad_display.html', extracted_text=extracted_text)
@app.route('/reset', methods=['POST'])
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    global extracted_text
    if request.method == 'POST':
        # Handle form submission
        updated_text = request.form['editor']
        
        # Update the extracted_text variable or save to your data source
        extracted_text = updated_text
        # Save the text to a file
        save_text_to_file(extracted_text)
        arser = argparse.ArgumentParser(description="Generate a result based on the summary.")
        # Redirect to the display page after saving changes
        return redirect(url_for('index'))
    return render_template('notepad_edit.html', extracted_text=extracted_text)
@app.route('/reset', methods=['POST'])
def reset():
    global extracted_text
    
    # Reset to the initial extracted text
    extracted_text = "Initial extracted text goes here."
    
    # Redirect to the edit page after resetting
    return redirect(url_for('edit'))
def save_text_to_file(pdf_file_name, text):
    # Create the "files" folder if it doesn't exist
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)

    # Use the original PDF file name for the text file (remove file extension)
    base_name, _ = os.path.splitext(pdf_file_name)
    text_file_name = f'{base_name}.txt'
    # Define the file path in the "files" folder
    file_path = os.path.join(files_folder, text_file_name)
    # Write the text to the file
    with open(file_path, 'w') as file:
        file.write(text)
@app.route('/generate_summary', methods=['GET', 'POST'])
def generate_summary():

    parser = argparse.ArgumentParser(description="Generate a result based on the summary.")

    # Add command-line arguments
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call your function with the provided input and output paths
    generate_summary(args.input, args.output)

    try:
        # Extracted text from the PDF
        extracted_text = request.form.get('extracted_text', '')
        # Run the short.py script using subprocess and pass the extracted text as input
        cmd = ['python', 'subdirectory/short.py', extracted_text]
        completed_process = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if completed_process.returncode == 0:
            # If the script runs successfully, you can display a success message or redirect
            return redirect(url_for('notepad_display', extracted_text='Summary generated successfully'))

        else:
            # Handle any errors that occur when running the script
            error_message = f"Error running short.py: {completed_process.stderr}"
            return redirect(url_for('notepad_display', extracted_text=error_message))
    except Exception as e:
        # Handle any other exceptions
        error_message = f"An error occurred: {str(e)}"
        return redirect(url_for('notepad_display', extracted_text=error_message))


if __name__ == "__main__":
    app.run(debug=True) 