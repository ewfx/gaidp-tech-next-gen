# This is  python  program for GenAI Data Profiling Model

import streamlit as st
import csv
import pdfplumber
from openai import OpenAI
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os




# Title of the app

st.title("Controlled Code Execution After File Upload")

if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

uploaded_file = st.file_uploader("Choose a file", type=None)

# Loading environmental variable
load_dotenv()
if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    # Optionally, display the contents of the file
    content = uploaded_file.read()
    decode_content = content.decode("utf-8")
    rows = decode_content.splitlines()
    
    dataset_path = os.getenv("DATASET_PATH")
    data_set_file_path = dataset_path + 'uploaded_dataset1.csv'
    with open(data_set_file_path,"w", newline="", encoding="utf-8") as file:
          writer = csv.writer(file)
          for row in rows:
                writer.writerow(row.split(","))
    
    st.session_state["file_uploaded"] = True
    st.info("File upload and save completed. You can now execute the code.")




     
def extract_text_from_pages(pdf_path, start_page, end_page):
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = ""
        # Ensure the range of pages is valid
        if start_page <= len(pdf.pages) and end_page <= len(pdf.pages):
            for page_number in range(start_page, end_page + 1):  
                page = pdf.pages[page_number - 1]  
                extracted_text += page.extract_text() + "\n"  
            return extracted_text
        else:
            return "Page range exceeds the total number of pages in the PDF."
        
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True 
    except ValueError:
        return False  


def check_key_or_value(x):
    # First, check if x is a key
    if str(x) in column_dict:
        return True  # Match found in keys
    # If not a key, check if x is a value
    elif x in column_dict.values():
        return True  
    else:
        return False  

# Button to execute the code
if "code_executed" not in st.session_state:
    st.session_state["code_executed"] = False

if st.session_state["file_uploaded"]:
    if st.button("Execute Code"):
        #EXTRACTING content from pdf file containing rules
        
        pfd_directory_path = os.getenv("PDF_PATH")
        pdf_path = pfd_directory_path + '/Federal_reserver_report.pdf'
        start_page = 58  # Starting page number
        end_page = 60    # Ending page number

        text = extract_text_from_pages(pdf_path, start_page, end_page)

    # Display the extracted text from PDF
        st.success("Text extracted from the PDF:")
        st.text_area("Extracted Text", text, height=300)

    # Display the LLM result of extracted text
        API_KEY_VALUE = os.getenv("API_CALL_KEY")

        client = OpenAI(
        api_key = API_KEY_VALUE
        )

        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        temperature=0,
        messages=[
         {"role": "developer", "content": "You are a helpful assistant for extracting compliance rules."},
         {
            "role": "user",
            "content": text + "\nPlease extract compliance rules from the above content and structure them as a JSON object with fields such as `rule_id`, `field name`,`condition`,  `action` and `allowable values`",
         },
         ],
         )
        result = completion.choices[0].message;
        st.success("Text extracted from the LLM:")
        st.text_area("Extracted Text From LLM", result, height=300)
        

        # Converting the result From LLM in JSON form
        content = result.content  


        start = content.find("json") + len("json") 
        end = content.find("```", start) 
        json_data = content[start:end].strip() # Extract and clean the JSON part
        parsed_json = json.loads(json_data)
        json_data_extract = json.dumps(parsed_json,indent=4)
    
        compliance_path = os.getenv("COMPLIANCE_RULE_PATH")
        compliance_path_file = compliance_path + '/compliance_rules.txt'
        with open(compliance_path_file, "w") as json_file:
            json.dump(parsed_json,json_file,indent=4)
        st.success("JSON TEXT extracted from  LLM output:")
        st.text_area("Extracted JSON Text From LLM output", json_data_extract, height=300)

        #Another LLM call on JSON Data to derive more meaningful result

        client = OpenAI(
        api_key = API_KEY_VALUE
        )

        completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        temperature=0,
        messages=[
         {"role": "developer", "content": "You are a helpful assistant for converting to python code ."},
         {
            "role": "user",
            "content": json_data_extract + "\nPlease convert `allowable_values` content in the form of Python code logic and put the result in a new field `allowable_value_code`. The new field `allowable_value_code` should be in JSON format. For example, `allowable_value_code` should look like this:\nallowable_value_code: {\n    '1': 'Last-of-Layer',\n    '2': 'One or more selected contractual cash flows',\n    '3': 'Not applicable'\n}"
         },
         ],
         )
        
        result_code = completion.choices[0].message;
        st.success("LLM output  from  JSON Data:")
        st.text_area("Extracted LLM output from JSON Data", result_code, height=300)
        
        # Access the `content` attribute of the ChatCompletionMessage object
        content_with_code = result_code.content  # Assuming `result` is the ChatCompletionMessage object


        start_code = content_with_code.find("```json") + len("```json") 

        end_code = content_with_code.find("```", start_code) 

        json_data_code = content_with_code[start_code:end_code].strip() # Extract and clean the JSON part
        parsed_json_code = json.loads(json_data_code)
        json_data_extract_code = json.dumps(parsed_json_code,indent=4)
        
        compliance_code_path = os.getenv("COMPLIANCE_RULE_CODE_PATH")
        compliance_code_path_file = compliance_code_path + '/compliance_rules_with_code.txt'
        with open(compliance_code_path_file, "w") as json_file:
            json.dump(parsed_json_code,json_file,indent=4)
        st.success("JSON Data from second LLM call:")
        st.text_area("Extracted JSON Data from second LLM call", json_data_extract_code, height=300)

        # Applying Rules on the Dataset
        
        df1 = pd.read_csv(data_set_file_path)



        with open(compliance_code_path_file,"r") as file:
            dict_data = json.load(file)
        for entry in dict_data:
            field_name = entry["field_name"]
 
            if field_name in df1.columns:
                column_dict = entry["allowable_value_code"]
        
                if field_name  in ('Hedge Percentage'): #LLM provided instruction set in simple english so had to handle
                    df1[f"{field_name}_validation"] = df1[field_name].apply(lambda x: isinstance(x, (int, float)) and 0 <= x <= 1)
                    df1[f"{field_name}_rule_applied"] = "RULEID- " + str(entry["rule_id"]) + " -CONDITION " + entry["condition"] + " -ACTION " + entry["action"] + " -ALLOWABLE_VALUES" + entry["allowable_values"]
            
                elif field_name  in ('Effective Portion of Cumulative Gains and Losses','Hedging Instrument at Fair Value'): #LLM provided instruction set in simple english so had to handle
                    df1[f"{field_name}_validation"] = df1[field_name].apply(lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer()))
                    df1[f"{field_name}_rule_applied"] = "RULEID- " + str(entry["rule_id"]) + " -CONDITION " + entry["condition"] + " -ACTION " + entry["action"] + " -ALLOWABLE_VALUES" + entry["allowable_values"]

                elif field_name  in ('Hedge Horizon'): #LLM provided instruction set in simple english so had to handle
                    df1[f"{field_name}_validation"] = df1[field_name].apply(lambda x: validate_date(x))
                    df1[f"{field_name}_rule_applied"] = "RULEID- " + str(entry["rule_id"]) + " -CONDITION " + entry["condition"] + " -ACTION " + entry["action"] + " -ALLOWABLE_VALUES" + entry["allowable_values"]

    
                elif field_name  not in ('Identifier Type','Identifier Value','Amortized Cost','Market Value (USD Equivalent)'): #LLM provided data in key value pair for fields on which generic code is written
                    #Below two conditions applies on all the allowable values which are in key value pair description in fedral report. This is automation of rules getting applied via LLM help 
                    df1[f"{field_name}_validation"] = df1[field_name].apply(check_key_or_value)
            
                    df1[f"{field_name}_rule_applied"] = "RULEID- " + str(entry["rule_id"]) + " -CONDITION " + entry["condition"] + " -ACTION " + entry["action"] + " -ALLOWABLE_VALUES" + entry["allowable_values"]
                else:
                    print(f"field_name {field_name} not required to be validated in the report")
            else:
                print(f"rule {field_name} not found in dataset columns or field names belongs to either of Identifier Type,Identifier Value,Amortized Cost,Market Value (USD Equivalent)")
    
        
        result_file_path = os.getenv("OUTPUT_FILE_PATH")
        result_file = result_file_path + '/Data_profiling_Report.csv'  # Update the path
        df1.to_csv(result_file, index=False)
        st.success("Rule Set Applied , Ready For Download:")
        st.session_state["code_executed"] = True




    else:
         st.warning("Please upload a file before executing the code.")
        

#Download File
if st.session_state["code_executed"] and st.session_state["file_uploaded"]:
    st.header("File Download Section")
    # File content to be downloaded
    with open(result_file,"r") as file1:
     file_content = file1.read()
     file_name = "Data_profiling_Report.csv"
     # Display the download button
     st.download_button(
     label="Download File",
     data=file_content,
     file_name=file_name,
     mime="text/csv"  # MIME type for plain text files
     )
else:
    st.warning("file upload and code execute should  happen  before downloading the file.")

st.session_state["file_uploaded"] = False
st.session_state["code_executed"] = False
