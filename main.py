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

        # Remove any blank lines (they muck with GitLab formatting)
        for index, line in enumerate(markdown):
            if line == "\n":
                markdown.pop(index)

        # Write the markdown list into a single string for the code box
        code_box_text = ""
        for line in markdown:
            code_box_text = code_box_text + line

        st.code(code_box_text, language="markdown")

    elif organise_by == "Gherkin Feature Name":
        df = pd.read_csv(uploaded_file)
        markdown = []
        feature_files = {}

        for index, row in df.iterrows():
            # Try to find our expected Gherkin sections, if any aren't found, set them as an empty string
            try:
                cell = strip_tags(row["Description"])
            except KeyError:
                st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                break
            try:
                feature = re.search(r"\bFeature: .+", cell).group().strip("Feature: ")
                feature = feature.replace("-", " ").lower()
            except AttributeError:
                feature = ""
            try:
                background = re.search(r"\bBackground:(.+?)\n\n", cell, re.DOTALL).group()
            except AttributeError:
                background = ""
            try:
                scenario = re.search(r"\bScenario:.+", cell, re.DOTALL).group()
            except AttributeError:
                scenario = ""

            # Turn the background into a list of lines, format to markdown, turn back into a string
            background_list = background.splitlines()
            background_formatted = ""
            for background_inner in background_list:
                background_inner = background_inner.strip() + "\n"
                background_inner = background_inner.replace("Background", "### Background")
                background_inner = background_inner.replace("Given", "- **Given**")
                background_inner = background_inner.replace("When", "- **When**")
                background_inner = background_inner.replace("Then", "- **Then**")
                background_inner = background_inner.replace("And", "    - **And**")
                background_formatted = background_formatted + background_inner

            # Turn the scenario into a list of lines, format to markdown, turn back into a string
            scenario_list = scenario.splitlines()
            scenario_formatted = ""
            for scenario_inner in scenario_list:
                scenario_inner = scenario_inner.strip() + "\n"
                scenario_inner = scenario_inner.replace("Scenario", "### Scenario")
                scenario_inner = scenario_inner.replace("Given", "- **Given**")
                scenario_inner = scenario_inner.replace("When", "- **When**")
                scenario_inner = scenario_inner.replace("Then", "- **Then**")
                scenario_inner = scenario_inner.replace("And", "    - **And**")
                scenario_formatted = scenario_formatted + scenario_inner

            if feature in feature_files:
                feature_files[feature]["scenarios"].append(scenario_formatted)
            else:
                feature_files.update({feature: {"background": background_formatted, "scenarios": []}})
                feature_files[feature]["scenarios"].append(scenario_formatted)

        # Write the dictionary out into a flat list
        for feature_inner in feature_files:
            feature_header = f"## {feature_inner.title()}\n"
            markdown.append(feature_header)
            markdown.append(feature_files[feature_inner]["background"])
            for feature_scenario in feature_files[feature_inner]["scenarios"]:
                markdown.append(feature_scenario)

        # Remove any blank lines (they muck with GitLab formatting)
        for index, line in enumerate(markdown):
            line = line.replace("\n\n", "\n")
            markdown[index] = line
            if line == "\n" or line == "":
                markdown.pop(index)

        # Write the markdown list into a single string for the code box
        code_box_text = ""
        for line in markdown:
            code_box_text = code_box_text + line

        st.code(code_box_text, language="markdown")
