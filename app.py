# Import necessary libraries
import streamlit as st  # For creating the web application
import pandas as pd  # For handling and processing tabular data
from openai import OpenAI  # For interacting with OpenAI API
from utils.question_answering import answer_question_with_gpt4  # Custom function for generating answers using LLMs


# Step 1: Set up the OpenAI API key
# The API key is stored in a text file and read here for authentication
with open('api_key.txt', 'r') as file: 
    key = file.read().strip()  # Remove any leading or trailing whitespace
    
# Initialize the OpenAI client using the API key
client = OpenAI(api_key=key)

# Step 2: Configure the Streamlit app
# Define the app's title, icon, and layout (wide layout for better usability)
st.set_page_config(page_title="Email QA App", page_icon="📧", layout="wide")
st.title("📧 Email Question Answering App")  # Display app title on the UI

# Step 3: Define session states
# Session states are used to keep track of the current page and selected emails
if "page" not in st.session_state:
    st.session_state.page = "upload"  # Default page is "upload"
if "selected_emails" not in st.session_state:
    st.session_state.selected_emails = []  # Initialize selected emails as an empty list

# Step 4: Navigation function
# Function to navigate between different pages of the app
def navigate_to(page_name):
    st.session_state.page = page_name  # Update the current page in session state
    
    
# Step 5: Page 1 - Upload Emails
if st.session_state.page == "upload":
    st.header("Step 1: Upload Emails") # Display a header for this step
    # File uploader to allow users to upload CSV or Excel files
    uploaded_file = st.file_uploader("Upload your email dataset (CSV or Excel):", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # Read the uploaded file into a pandas DataFrame
            if uploaded_file.name.endswith(".csv"):
                email_data = pd.read_csv(uploaded_file)
            else:
                email_data = pd.read_excel(uploaded_file)
                
            # Check if the required column "Email Body" exists
            if "Email Body" not in email_data.columns:
                st.error("❌ Error: The uploaded file must contain a column named 'Email Body'.")
            else:
                st.write("### Uploaded Emails Preview:") # Display the file preview
                st.write(email_data.head()) # Show the first few rows of the file
                st.session_state.email_data = email_data # Store the email data in session state
                
                # Navigation button to move to the next step                
                if st.button("Next", key="upload_to_select"):
                    navigate_to("select")
        except Exception as e:
            st.error(f"❌ Error reading the file: {e}") # Handle any file reading errors

# Step 6: Page 2 - Select Emails
if st.session_state.page == "select":
    st.header("Step 2: Select Emails for Question Answering")  # Display a header for this step

    if "email_data" in st.session_state:
        email_data = st.session_state.email_data  # Retrieve the email data from session state

        # Option to preview all emails
        preview_all = st.checkbox("Preview All Emails")
        if preview_all:
            st.write(email_data)

        # Radio buttons to select emails based on different modes
        selection_mode = st.radio(
            "Select Emails to Answer Questions:",
            ("All Emails", "Specific Range", "Manual Selection"),
            index=0,
        )

        selected_emails = []
        if selection_mode == "Specific Range":
            # Allow users to specify a range of emails using number inputs
            start_index = st.number_input("Start Index (1-based):", min_value=1, max_value=len(email_data), value=1)
            end_index = st.number_input("End Index (1-based):", min_value=start_index, max_value=len(email_data), value=len(email_data))
            selected_emails = email_data.iloc[start_index - 1 : end_index]  # Select rows within the specified range
        elif selection_mode == "Manual Selection":
            # Allow users to manually select specific email indices
            email_indices = st.multiselect(
                "Select Email Indices (1-based):",
                options=range(1, len(email_data) + 1),
                format_func=lambda x: f"Email {x}",
            )
            selected_emails = email_data.iloc[[i - 1 for i in email_indices]]  # Select rows corresponding to chosen indices

        if selection_mode == "All Emails":
            selected_emails = email_data  # Select all emails if this option is chosen

        st.session_state.selected_emails = selected_emails  # Save selected emails to session state

        # Navigation buttons for moving forward or backward
        if st.button("Next", key="select_to_question"):
            navigate_to("question")
        if st.button("Back", key="select_to_upload"):
            navigate_to("upload")

# Step 7: Page 3 - Ask Questions and Get Answers
if st.session_state.page == "question":
    st.header("Step 3: Ask a Question and Get Answers")  # Display a header for this step

    if st.session_state.selected_emails is not None and len(st.session_state.selected_emails) > 0:
        selected_emails = st.session_state.selected_emails  # Retrieve selected emails from session state

        # Input box for the user to type a question
        question = st.text_input("Enter your question:")
        # Radio buttons to allow users to choose output length
        output_length = st.radio(
            "Select Output Length:",
            options=["Short", "Medium", "Detailed"],
            index=1,
        )

        # Button to generate answers
        if st.button("Get Answers"):
            with st.spinner("Processing..."):  # Display a spinner while processing
                results = []
                # Iterate through each selected email and generate answers using GPT-4
                for i, email_text in enumerate(selected_emails["Email Body"]):
                    if pd.notna(email_text):  # Skip empty email bodies
                        prompt = f"Provide a {output_length.lower()} answer. {question}"
                        answer = answer_question_with_gpt4(email_text, prompt, client)  # Call the GPT-4 function
                        results.append({"Email": email_text, "Answer": answer["response"]})  # Store results

                # Display the results for each email
                st.write("### Results")
                for result in results:
                    st.write(f"**Email:** {result['Email']}")
                    st.write(f"**Answer:** {result['Answer']}")
    else:
        st.error("No emails selected. Please go back to Step 2 and select emails.")

    # Button to navigate back to the selection page
    if st.button("Back"):
        navigate_to("select")




































