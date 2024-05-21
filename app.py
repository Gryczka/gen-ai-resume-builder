from bs4 import BeautifulSoup
from docx import Document
import os
from PyPDF2 import PdfReader
import replicate
import requests
import streamlit as st
from transformers import AutoTokenizer

# App title
st.set_page_config(page_title="Gen AI Resume Writer")
st.title('Gen AI Resume Writer')

# Set assistant icon to Snowflake logo
icons = {"assistant": "./write-avatar.webp", "user": "⛷️"}

#########################################################################################
# Section 1 - Provide Applicant Background
#########################################################################################
st.header('📄Provide Applicant Background')

input_applicant_context = ''
applicant_summary = ''

# Define a variable that will hold the state of whether the button was clicked
if 'write_background_button_clicked' not in st.session_state:
    st.session_state.write_background_button_clicked = False
if 'upload_resume_button_clicked' not in st.session_state:
    st.session_state.upload_resume_button_clicked = False

# Define a callback function that will toggle the state of the button
def click_write_background_button():
    st.session_state.write_background_button_clicked = True
    st.session_state.upload_resume_button_clicked = False
def click_upload_resume_button():
    st.session_state.upload_resume_button_clicked = True
    st.session_state.write_background_button_clicked = False
    

col1, col2 = st.columns(2)
with col1:
    cover_letter_btn = st.button("Write Your Background Info", on_click=click_write_background_button)
with col2:
    cover_letter_btn = st.button("Upload Your Existing Resume", on_click=click_upload_resume_button)

if st.session_state.write_background_button_clicked:
    input_applicant_context = st.text_area("Applicant Background Info")
    # first_name = st.text_input("First Name")
    # last_name = st.text_input("Last Name")
    # email = st.text_input("Email")
    # phone = st.text_input("Phone Number")
    # linkedin = st.text_input("LinkedIn Profile")
    # github = st.text_input("GitHub Profile")
    # portfolio = st.text_input("Portfolio")
    # website = st.text_input("Personal Website")
    # location = st.text_input("Location")
    # industry = st.text_input("Industry")
    # experience = st.text_input("Years of Experience")
    # education = st.text_input("Education")
    # skills = st.text_input("Skills")
    # certifications = st.text_input("Certifications")
    # languages = st.text_input("Languages")
    # interests = st.text_input("Interests")
    # volunteer = st.text_input("Volunteer Experience")
    # awards = st.text_input("Awards")
    # publications = st.text_input("Publications")
    # patents = st.text_input("Patents")
    # projects = st.text_input("Projects")
    # courses = st.text_input("Courses")
    # organizations = st.text_input("Organizations")
    # hobbies = st.text_input("Hobbies")
    # summary = st.text_area("Summary")

# Resume Upload
def read_pdf(file):
    """Read and extract text from a PDF file."""
    # Initialize a PDF reader object and extract text
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    """Read and extract text from a DOCX file."""
    # Load the DOCX file
    doc = Document(file)
    text = [paragraph.text for paragraph in doc.paragraphs]
    return "\n".join(text)

# Function for generating Snowflake Arctic response
def summarize_content(applicant_context):
    # Set the values for the temperature and top_p parameters
    temperature = 0.01
    top_p = 0.9
    prompt = []
    prompt.append("<|content|>\n" + applicant_context + "<|content|>")
    prompt.append("<|im_start|>user Hi, I would like you to summarize the important points from the content.<|im_end|>")
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    
    output = replicate.run("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  })
    return output

if st.session_state.upload_resume_button_clicked:
    st.subheader("Resume Reader")
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            # Reading from a PDF file
            raw_text = read_pdf(uploaded_file)
            input_applicant_context = raw_text
            st.text_area("Extracted Text from PDF", raw_text, height=250)
            applicant_summary = summarize_content(raw_text)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Reading from a Word document
            raw_text = read_docx(uploaded_file)
            input_applicant_context = raw_text
            st.text_area("Extracted Text from DOCX", raw_text, height=250)
            applicant_summary = summarize_content(raw_text)
    else:
        st.warning("Please upload a PDF or DOCX file.")

#########################################################################################
# Section 2 - Provide Target Job Details
#########################################################################################
st.header('💼Provide Target Job Details')

input_job_context = ''
job_summary = ''

# Define variables that will hold the state of whether the buttons were clicked
if 'job_link_button_clicked' not in st.session_state:
    st.session_state.job_link_button_clicked = False
if 'write_job_detail_button_clicked' not in st.session_state:
    st.session_state.write_job_detail_button_clicked = False

# Define callback functions that will toggle the state of the button
def click_job_link_button():
    st.session_state.job_link_button_clicked = True
    st.session_state.write_job_detail_button_clicked = False
def click_write_job_detail_button():
    st.session_state.write_job_detail_button_clicked = True
    st.session_state.job_link_button_clicked = False


col1, col2 = st.columns(2)
with col1:
    write_job_details_btn = st.button("Write Job Details", on_click=click_write_job_detail_button)
with col2:
    job_link_btn = st.button("Link Job Description", on_click=click_job_link_button)

# Define an empty url variable
url = ''

# If the user clicks the button to write job details, display text inputs for the job title and company
if st.session_state.write_job_detail_button_clicked:
    job_description = st.text_area("Job Description")
    input_job_context = job_description
    job_summary = summarize_content(job_description)
if st.session_state.job_link_button_clicked:
    url = st.text_input("Link to Job Description")

# Define a function to fetch text from a URL
def fetch_text(url):
    # Send a GET request to the URL
    try:
        response = requests.get(url)
    except:
        return "Our Request to the Provided URL Failed"
    else:
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and return the text
            return soup.get_text()
        else:
            return "Failed to retrieve content"

# Define a function to apply custom CSS styles
def apply_styles():
    with open( "style.css" ) as css:
        st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    st.markdown("""
        <style>
        .card {
            margin: 10px;
            padding: 10px;
            border-radius: 8px;
            background-color: #f9f9f9;
            color: #000000;
            box-shadow: 2px 2px 5px grey;
            height: 300px;
            overflow-y: auto;
        }
        .card h2{
            color: #000000;
        }
        </style>
        """, unsafe_allow_html=True)

# Apply the styles defined above
apply_styles()

# If the user provides a URL, display the text from the URL
## If the URL is invalid, display an error message
if url:
    if (fetch_text(url) == "Our Request to the Provided URL Failed") or (fetch_text(url) == "Failed to retrieve content"):
        data = fetch_text(url)
        st.markdown(f"""
            <div class="card">
                <h2>{data}</h2>
            </div>
            """, unsafe_allow_html=True)
    elif fetch_text(url):
        data = fetch_text(url)
        input_job_context = data
        st.markdown(f"""
            <div class="card">
                <h2>Text from Provided Job Description Link</h2>
                <p>{data}</p>
            </div>
            """, unsafe_allow_html=True)
        job_summary = summarize_content(data)

#########################################################################################
# Section 3 - Generate Customized Content
#########################################################################################
st.header('📝Generate Customized Content')

# Define a variable that will hold the state of whether the button was clicked
if 'cover_letter_button_clicked' not in st.session_state:
    st.session_state.cover_letter_button_clicked = False
if 'targeted_resume_button_clicked' not in st.session_state:
    st.session_state.targeted_resume_button_clicked = False
if 'practice_question_button_clicked' not in st.session_state:
    st.session_state.practice_question_button_clicked = False

# Define a callback function that will toggle the state of the button
def click_cover_letter_button():
    st.session_state.cover_letter_button_clicked = True
def click_targeted_resume_button():
    st.session_state.targeted_resume_button_clicked = True
def click_practice_question_button():
    st.session_state.practice_question_button_clicked = True

# Add a button that uses the callback function
col1, col2, col3 = st.columns(3)
with col1:
    cover_letter_btn = st.button("Cover Letter", on_click=click_cover_letter_button)
    cover_letter_tone = st.selectbox(
    "What tone should your cover letter have?",
    ("Formal", "Casual", "Professional", "Friendly", "Technical"))
with col2:
    cover_letter_btn = st.button("Targeted Resume", on_click=click_targeted_resume_button)
with col3:
    cover_letter_btn = st.button("Practice Interview Questions", on_click=click_practice_question_button)

def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)



# Function for generating Snowflake Arctic response
def generate_cover_letter(applicant_context, job_context):
    # Set the values for the temperature and top_p parameters
    temperature = 0.01
    top_p = 0.9
    prompt = []
    prompt.append("<|applicant_context|>\n" + ''.join(applicant_summary) + "<|applicant_context|>")
    prompt.append("<|job_context|>\n" + ''.join(job_summary) + "<|job_context|>")
    prompt.append("<|im_start|>user Hi, I would like to generate a cover letter for a job application, with the following tone " + ''.join(cover_letter_tone) + "<|im_end|>")
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    
    output = replicate.run("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  })
    return output

# Function for generating Snowflake Arctic response
def generate_resume(applicant_context, job_context):
    # Set the values for the temperature and top_p parameters
    temperature = 0.01
    top_p = 0.9
    prompt = []
    prompt.append("<|im_start|>user Hi, I would like to generate a resume for a job application." + "<applicant summary>" + ''.join(applicant_summary) + "</applicant summary> <job summary>" + ''.join(job_summary) + "</job summary> Do not add any credentials not mentioned in the applicant summary.<|im_end|>")
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    output = replicate.run("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  })
    return output

# Function for generating Snowflake Arctic response
def generate_interview_questions(applicant_context, job_context):
    # Set the values for the temperature and top_p parameters
    temperature = 0.01
    top_p = 0.9
    prompt = []
    prompt.append("<|im_start|>user Hi, I would like to generate interview questions for a job application." + "<applicant summary>" + ''.join(applicant_summary) + "</applicant summary> <job summary>" + ''.join(job_summary) + "</job summary><|im_end|>")
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    output = replicate.run("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  })
    return output

if st.session_state.cover_letter_button_clicked:
    st.subheader("Cover Letter")
    cover_letter_response = generate_cover_letter(input_applicant_context, input_job_context)
    full_cover_letter_response = st.write_stream(cover_letter_response)

if st.session_state.targeted_resume_button_clicked:
    st.subheader("Targeted Resume")
    resume_response = generate_resume(input_applicant_context, input_job_context)
    full_resume_response = st.write_stream(resume_response)

if st.session_state.practice_question_button_clicked:
    st.subheader("Practice Interview Questions")
    interview_question_response = generate_interview_questions(input_applicant_context, input_job_context)
    full_interview_question_response = st.write_stream(interview_question_response)

# Replicate Credentials
with st.sidebar:
    st.title('Gen AI Resume Writer')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your Replicate API token.', icon='⚠️')
            st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")

    os.environ['REPLICATE_API_TOKEN'] = replicate_api

st.sidebar.caption('Built by [@Gryczka](https://github.com/Gryczka) for the [2024 The Future of AI is Open Hackathon](https://arctic-streamlit-hackathon.devpost.com/).')
st.sidebar.caption('App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')
st.sidebar.caption('This App referenced the [Snowflake Arctic Streamlit Example](https://github.com/streamlit/snowflake-arctic-st-demo/tree/main) as a starting point.')

