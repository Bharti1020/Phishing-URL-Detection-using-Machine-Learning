from flask import Flask, render_template, request
import os
import PyPDF2
import google.generativeai as genai

app=Flask(__name__)
#set up the google api key
os.environ["GOOGLE_API_KEY"]="YOUR API KEY"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model=genai.GenerativeModel("gemini-1.5-flash")
def predict_fake_or_real_email_content(text):
    prompt="""Analyze the following email content and provide:
    1. The type of file (e.g., invoice, report, personal, etc.) if possible.
    2. Whether the content is harmful or not (explain why).
    3. Classify as "scam" or "not scam".

    Email content: {text}

    Respond in this format:
    File Type: <type>
    Harmful: <yes/no> (<reason>)
    Classification: <scam/not scam>
    """
    response=model.generate_content(prompt)
    return response.text.strip() 
def url_detection(url):
        prompt=f"""Classify the following URL as "scam" or "not scam". 
        A URL is considered a scam if it leads to a website that tries to deceive visitors into providing sensitive information, 
        such as passwords, credit card numbers, or other personal details, often for malicious purposes. 
        It may also involve fraudulent schemes or attempts to trick visitors into taking actions that could lead to financial loss or harm.

        URL: {url}

        Respond with only "scam" or "not scam"."""
        response=model.generate_content(prompt)
        return response.text.strip()
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/scam/", methods=["POST"])
def detect_scam():
    if "file" not in request.files:
        return render_template("index.html",message="no file uploaded")
    file=request.files["file"]
    print(file)

    extracted_text=""
    if file.filename.endswith(".pdf"):
        pdf_reader=PyPDF2.PdfReader(file)
        extracted_text="".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith(".txt"):
        extracted_text=file.read().decode("utf-8")
    else:
        return render_template("index.html",message="unsupported file type")
    print(extracted_text)
    message=predict_fake_or_real_email_content(extracted_text)

    return render_template("index.html",message=message)

@app.route("/predict", methods=["GET","POST"])
def url_predict():
    if request.method=="POST":
        url=request.form.get("url","").strip()
        if not url.startswith(("http://", "https://")):
            return render_template("index.html",message="no url provided")
        classification=url_detection(url)
        return render_template("index.html", input_url=url, predicted_class=classification)
    return render_template("index.html")
if __name__=="__main__":

    app.run(debug=True)
