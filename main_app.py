import streamlit as st
import os
from autogen import ConversableAgent , AssistantAgent , UserProxyAgent, register_function
import os
import autogen
from dotenv import load_dotenv
import mammoth
import re
import sys
import pandas as pd

# Define the folder to store uploaded files
UPLOAD_FOLDER = "/Users/janhvi/Desktop/RFP_Scoring_QualificationCriteriaValidation"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(uploaded_file, doc_type):
    """Function to save the uploaded file to the designated folder."""
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_FOLDER, f"{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"{doc_type} uploaded successfully!")
        return file_path
    return None

load_dotenv()
#Define LLM Configuration
llm_config = {
    "config_list": [{"model": os.environ["MODEL"], "api_key": os.environ["OPENAI_API_KEY"]}],
}
critic_llm_config = {
    "config_list": [{"model": os.environ["CRITIC_MODEL"], "api_key": os.environ["OPENAI_API_KEY"]}],
}

input_dir=UPLOAD_FOLDER
human_input_mode=os.environ["human_input_mode"]
orchestrator_name=os.environ["orchestrator_name"]

#Function to process the documents
def preprocess_document(file_path: str) -> str:
    if not os.path.exists(file_path):
        return "File not found"

    with open(file_path, "rb") as docx_file:
        result = mammoth.extract_raw_text(docx_file).value
        result = re.sub(r'\n+', '\n', result).strip()
        result = re.sub(r' +', ' ', result).strip()
        return result  # Extracted text as a string
    
#Function to get the validation results from the Agent's output
import re
import json

def get_val_resuls(summary: str) -> str:
    # Extract JSON block that starts with ```json and ends with ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", summary, re.DOTALL)

    if match:
        json_text = match.group(1)  # Extract JSON content
        try:
            json_data = json.loads(json_text)  # Parse JSON
            return json_data.get("Validation Result", "Validation Result not found")  # Extract value
        except json.JSONDecodeError:
            return "Error: Invalid JSON format"
    else:
        return "Validation Result not found"

#Define Agents
#Orchestrator Agent
orchestrator = ConversableAgent(orchestrator_name,code_execution_config=False,human_input_mode=human_input_mode)

#Validation Agent
validation_agent = ConversableAgent (
                                    'validation_agent',
                                    system_message="""Role - RFP Criteria Validation Agent
                                    The Goal - To validate the Criteria with the input document
                                    Task - 
                                    Breakdown the Qualification Criteria give in {qualification_criteria}

                                    Check the following document / content submitted by bidder:
                                    {content}
                                    
                                    Validate if the bidder qualifies the given Criteria
                                    
                                    Expected output of Task - 
                                    - Breakdown: Breakdown of  {qualification_criteria} in bulleted format.
                                    - Rationale: Provide the rationale behinde the Validation process.
                                    Provide output of following in json format with given key and the output must start with ```json - 
                                    - Validation Result : [Pass] or [Fail]
                                    """,
                                    llm_config=llm_config,
                                    human_input_mode="NEVER",
)


#function to extract RFP criterias
df_eval_crt_inputs = pd.read_excel('C:/Users/HP/Documents/RFP_Scoring_QualificationCriteriaValidation/import_df.xlsx', index_col=None, header=0)

import io
import sys

def process_all(dff):
    df1 = dff
    df_upd = df1.copy()
    
    # Capture printed output
    text_output = io.StringIO()
    sys.stdout = text_output  # Redirect stdout to capture print statements
    
    for index, row in df1.iterrows():  # Unpacking the tuple (index, row)
        print(f"Processing Criteria no. {index + 1}:")
        qualification_criteria = row[0]+ row[1]
        file_name = row[2]
        print(f"#1 Validation of Criteria - ",qualification_criteria)
        print(f"#2 Artifact considered for validation - ",file_name)
        input_doc=input_dir+"/"+file_name
        #print(input_doc)
        supporting_document = preprocess_document(input_doc)
        print(supporting_document)
        if supporting_document != "File not found":
            chat_1 = orchestrator.initiate_chat(validation_agent,message={"role": "user", "content": supporting_document, "qualification_criteria": qualification_criteria},
                    max_turns=1,)
            Validation_results = get_val_resuls(chat_1.summary)
            print(f"#3 Validation Result - " ,Validation_results)
            df_upd.loc[index, 'Result'] = Validation_results
        else: 
            df_upd.loc[index, 'Result'] = "Fail"
        print(f"------------------------- Validation of one Criteria no.{index + 1} Completed ------------------------------")
        sys.stdout = sys.__stdout__  # Restore stdout
  
    return df_upd, text_output.getvalue()


import sqlite3

def validate():
    test , logs_output = process_all(df_eval_crt_inputs)
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    # Load DataFrame into SQLite
    test.to_sql("temp_table", conn, if_exists="replace", index=False)
    # Run an SQL UPDATE statement
    cursor.execute("UPDATE temp_table SET points = allocated_points WHERE Result like '%Pass%'")
    cursor.execute("UPDATE temp_table SET points = 0 WHERE Result not like '%Pass%'")
    conn.commit()
    # Fetch updated DataFrame
    test_updated = pd.read_sql("SELECT * FROM temp_table", conn)
    
    test_updated.to_sql("temp_table_1", conn, if_exists="replace", index=False)
    cursor.execute("Select sum(points)  from temp_table_1")
    points_aq = cursor.fetchone()[0]  # Fetch the first value from the result
    cursor.execute("Select sum(allocated_points)  from temp_table_1")
    points_total = cursor.fetchone()[0] 
       
    return test_updated,logs_output,points_aq,points_total




import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import os

# Custom CSS for modern UI
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .title {
            font-size: 36px;
            color: #2C3E50;
            text-align: center;
            font-weight: bold;
        }
        .upload-box {
            border: 2px dashed #3498db;
            padding: 10px;
            border-radius: 10px;
            background-color: #ECF0F1;
            text-align: center;
        }
        .button {
            background-color: #2ECC71;
            color: white;
            border-radius: 5px;
            font-size: 18px;
            padding: 10px 15px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit App UI
st.markdown("<div class='title'>🤖 AI Powered RFP Qualification Criteria Validation System</div>", unsafe_allow_html=True)

st.markdown("#### 📂 Upload Required Documents")

document_types = [
    "📑 Pre Contract Integrity Pact",
    "🇮🇳 Make in India Certificate",
    "📝 Letter of Confirmation for No Related Entity Participation",
    "🏢 Original OEM Letter",
    "🔏 Company Credentials",
    "📝 Self Declaration for Non-Debarment / Non-Blacklisting",
    "📝 Letter of Confirmation for No Relation with member of the Bank’s Board of directors"
]

uploaded_files_paths = {}

for doc_type in document_types:
    #st.markdown(f"<div class='upload-box'>📌 <b>{doc_type}</b></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        background: rgba(203, 242, 214, 0.1);
        backdrop-filter: blur(8px);
        padding: 14px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
        font-size: 20px;
        font-weight: bold;
        color: #333;
        display: flex;
        align-items: center;
    ">
        📜 <span style="margin-left: 12px;">{doc_type}</span>
    </div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", key=doc_type, label_visibility='collapsed')
    if uploaded_file:
        uploaded_files_paths[doc_type] = save_uploaded_file(uploaded_file, doc_type)

# Modern styled button
if st.button("⚙️ Validate", key="validate", help="Click to start validation",use_container_width=True , type="primary"):
    out_df, final_output,pt_ac,pt_total = validate()
    
    # Store logs in session state to avoid truncation after rerun
    st.session_state["validation_logs"] = final_output
    
    # Validation Output Box
    st.markdown("### 📜 Validation Logs")
    st.text_area("Logs", st.session_state["validation_logs"], height=500)
    
    # Display DataFrame Output
    st.markdown("### 📊 Points acquired for each Criteria")
    st.dataframe(out_df)
    
    st.markdown(f"### ⚡Total {pt_ac} points aquired out of {pt_total} points.")
