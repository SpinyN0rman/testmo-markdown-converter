import streamlit as st
import pandas as pd
import re
from functions import gherkin_to_md, strip_tags

st.title("Testmo CSV to Markdown Converter")
st.text("Use this page to convert a CSV export from Testmo into Markdown which can easily be shared with a wider audience")
st.markdown("_Note that this early version only looks at the 'Case' and 'Description' fields from Testmo_")

how_to_tab, upload_tab, paste_tab = st.tabs(["How to use", "Upload a Testmo CSV", "Paste Gherkin code"])

with how_to_tab:
    st.header("How to use this app")
with upload_tab:
    st.header("Upload a Testmo CSV")
    uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
    organise_by = st.selectbox("Organise by: ", ["Testmo Case Name", "Gherkin Feature Name"])

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
                # Don't send the header through the formatter (it isn't gherkin text)
                header = "## " + header + "\n"
                markdown.append(header)

                try:
                    lines = row["Description"].splitlines()
                except KeyError:
                    st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                    break
                lines = [strip_tags(line) for line in lines]

                for index, line in enumerate(lines):
                    line = gherkin_to_md(line, feature=3, background=3, scenario=3)
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
                    feature = re.search(r"\bFeature: .+", cell).group()
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
                    background_inner = gherkin_to_md(background_inner, background=3)
                    background_formatted = background_formatted + background_inner

                # Turn the scenario into a list of lines, format to markdown, turn back into a string
                scenario_list = scenario.splitlines()
                scenario_formatted = ""
                for scenario_inner in scenario_list:
                    scenario_inner = gherkin_to_md(scenario_inner, scenario=3)
                    scenario_formatted = scenario_formatted + scenario_inner

                if feature in feature_files:
                    feature_files[feature]["scenarios"].append(scenario_formatted)
                else:
                    feature_files.update({feature: {"background": background_formatted, "scenarios": []}})
                    feature_files[feature]["scenarios"].append(scenario_formatted)

            # Write the dictionary out into a flat list
            for feature_inner in feature_files:
                feature_header = gherkin_to_md(feature_inner, feature=2)
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
with paste_tab:
    st.header("Paste Gherkin code")
    user_input = st.text_area("Paste your Gherkin code into this box")
    st.text("If needed, you may adjust the header levels below")

    col1, col2, col3 = st.columns(spec=3)

    with col1:
        feature_level = st.number_input("Header level for the Feature line", value=2, min_value=1, max_value=6)
    with col2:
        background_level = st.number_input("Header level for the Background line", value=3, min_value=1, max_value=6)
    with col3:
        scenario_level = st.number_input("Header level for the Scenario line", value=3, min_value=1, max_value=6)

    if feature_level > 3 or background_level > 3 or scenario_level > 3:
        st.info("Note: Notion only supports header levels up to level three ('###')")

    if user_input is not None:
        markdown = []
        lines = user_input.splitlines()
        for index, line in enumerate(lines):
            line = gherkin_to_md(line, feature=feature_level, background=background_level, scenario=scenario_level)
            markdown.append(line)

        # Remove any blank lines (they muck with GitLab formatting)
        for index, line in enumerate(markdown):
            if line == "\n":
                markdown.pop(index)

        # Write the markdown list into a single string for the code box
        code_box_text = ""
        for line in markdown:
            code_box_text = code_box_text + line

        if code_box_text != "":
            st.code(code_box_text, language="markdown")
