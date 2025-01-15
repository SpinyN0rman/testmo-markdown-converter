import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

def strip_tags(text):
    """Uses BeautifulSoup to strip HTML tags from text"""
    parsed = BeautifulSoup(text, 'html.parser')
    return parsed.get_text()

st.title("Testmo CSV to Markdown Converter")
st.text("Use this page to convert a CSV export from Testmo into Markdown which can easily be shared with a wider audience")
st.text("Note that this early version only looks at the 'Case' and 'Description' fields from Testmo")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    markdown = []

    for index, row in df.iterrows():
        header = row["Case"]
        header = "### " + header + "\n"
        markdown.append(header)

        lines = row["Description"].splitlines()
        lines = [strip_tags(line) for line in lines]

        for index, line in enumerate(lines):
            line = line.strip() + "\n"
            line = line.replace("Feature:", "**Feature:**")
            line = line.replace("Background:", "**Background:**")
            line = line.replace("Scenario:", "**Scenario:**")
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
    # with open("gherkin-markdown.txt", "w") as file:
    #     file.writelines(markdown)