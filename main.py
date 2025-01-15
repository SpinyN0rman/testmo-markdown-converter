import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

def strip_tags(text):
    """Uses BeautifulSoup to strip HTML tags from text"""
    parsed = BeautifulSoup(text, 'html.parser')
    return parsed.get_text()

st.title("Testmo CSV to Markdown Converter")
st.text("Use this page to convert a CSV export from Testmo into Markdown which can easily be shared with a wider audience")
st.text("Note that this early version only looks at the 'Case' and 'Description' fields from Testmo")
organise_by = st.selectbox("Organise by: ", ["Testmo Case Name", "Gherkin Feature Name"])

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file is not None:
    if organise_by == "Testmo Case Name":
        df = pd.read_csv(uploaded_file)
        markdown = []

        for index, row in df.iterrows():
            try:
                header = row["Case"]
            except KeyError:
                st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                break
            header = "## " + header + "\n"
            markdown.append(header)

            try:
                lines = row["Description"].splitlines()
            except KeyError:
                st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                break
            lines = [strip_tags(line) for line in lines]

            for index, line in enumerate(lines):
                line = line.strip() + "\n"
                line = line.replace("Feature", "### Feature")
                line = line.replace("Background", "### Background")
                line = line.replace("Scenario", "### Scenario")
                line = line.replace("Given", "- **Given**")
                line = line.replace("When", "- **When**")
                line = line.replace("Then", "- **Then**")
                line = line.replace("And", "    - **And**")
                markdown.append(line)

        for index, line in enumerate(markdown):
            if line == "\n":
                markdown.pop(index)

        code_box_text = ""
        for line in markdown:
            code_box_text = code_box_text + line

        st.code(code_box_text, language="markdown")
    elif organise_by == "Gherkin Feature Name":
        df = pd.read_csv(uploaded_file)
        markdown = []
        feature_files = {}

        for index, row in df.iterrows():
            try:
                cell = strip_tags(row["Description"])
            except KeyError:
                st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                break
            feature = re.search(r"\bFeature: .+", cell).group().strip("Feature: ")
            background = re.search(r"\bBackground:(.+?)\n\n", cell, re.DOTALL).group()
            scenario = re.search(r"\bScenario:.+", cell, re.DOTALL).group()
            if feature in feature_files:
                feature_files[feature]["scenarios"].append(scenario)
            else:
                feature_files.update({feature: {"background": background, "scenarios": []}})
                feature_files[feature]["scenarios"].append(scenario)
        st.code(feature_files, language="markdown")


    # with open("gherkin-markdown.txt", "w") as file:
    #     file.writelines(markdown)

# feature_files = {"feature_name": {"background": "background_name", "scenarios": [[scenario1][scenario2]]}}