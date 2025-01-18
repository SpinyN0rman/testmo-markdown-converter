import streamlit as st
import pandas as pd
import re
from functions import gherkin_to_md, strip_tags

st.title("Testmo CSV to Markdown Converter")
st.text("Use this page to convert a CSV export from Testmo into Markdown which can easily be shared with a wider audience")
st.markdown("_Note that this early version only looks at the 'Case' and 'Description' fields from Testmo_")

how_to_tab, upload_tab, paste_tab = st.tabs(["How to use", "Upload a Testmo CSV", "Paste Gherkin code"])

with how_to_tab:
    with open("how-to-content.md", "r") as file:
        page_content = file.read()
    st.markdown(page_content)
with upload_tab:
    st.header("Upload a Testmo CSV")
    uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
    organise_by = st.selectbox("Organise by: ", ["Testmo Case Name", "Gherkin Feature Name"])

    up_col1, up_col2, up_col3 = st.columns(spec=3)
    up_col4, up_col5, up_col6 = st.columns(spec=3)

    # Let the user choose the header levels
    if organise_by == "Testmo Case Name":
        with up_col1:
            up_case_level = st.number_input("Header level for the Case Name line", value=2, min_value=1,
                                                   max_value=6, key="up_case_h")
        with up_col2:
            st.text("")
        with up_col3:
            st.text("")
        with up_col4:
            up_feature_level = st.number_input("Header level for the Feature line", value=3, min_value=1,
                                                max_value=6, key="up_feature_h")
        with up_col5:
            up_background_level = st.number_input("Header level for the Background line", value=3, min_value=1,
                                                max_value=6, key="up_background_h")
        with up_col6:
            up_scenario_level = st.number_input("Header level for the Scenario line", value=3, min_value=1,
                                                        max_value=6, key="up_scenario_h")
        if up_case_level > 3 or up_feature_level > 3 or up_background_level > 3 or up_scenario_level > 3:
            st.info("Note: Notion only supports header levels up to level three ('###')")
    elif organise_by == "Gherkin Feature Name":
        with up_col4:
            up_feature_level = st.number_input("Header level for the Feature line", value=2, min_value=1,
                                                max_value=6, key="up_feature_h")
        with up_col5:
            up_background_level = st.number_input("Header level for the Background line", value=3, min_value=1,
                                                max_value=6, key="up_background_h")
        with up_col6:
            up_scenario_level = st.number_input("Header level for the Scenario line", value=3, min_value=1,
                                                        max_value=6, key="up_scenario_h")
        if up_feature_level > 3 or up_background_level > 3 or up_scenario_level > 3:
            st.info("Note: Notion only supports header levels up to level three ('###')")

    # When a file is uploaded, start the conversions
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
                header = "#" * up_case_level + " " + header + "\n"
                markdown.append(header)

                try:
                    lines = row["Description"].splitlines()
                except KeyError:
                    st.info("Error, the file does not contain the expected headers. Upload a new file to try again")
                    break
                lines = [strip_tags(line) for line in lines]

                for index, line in enumerate(lines):
                    line = gherkin_to_md(line, feature=up_feature_level, background=up_background_level,
                                         scenario=up_scenario_level)
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
                    background_inner = gherkin_to_md(background_inner, background=up_background_level)
                    background_formatted = background_formatted + background_inner

                # Turn the scenario into a list of lines, format to markdown, turn back into a string
                scenario_list = scenario.splitlines()
                scenario_formatted = ""
                for scenario_inner in scenario_list:
                    scenario_inner = gherkin_to_md(scenario_inner, scenario=up_scenario_level)
                    scenario_formatted = scenario_formatted + scenario_inner

                if feature in feature_files:
                    feature_files[feature]["scenarios"].append(scenario_formatted)
                else:
                    feature_files.update({feature: {"background": background_formatted, "scenarios": []}})
                    feature_files[feature]["scenarios"].append(scenario_formatted)

            # Write the dictionary out into a flat list
            for feature_inner in feature_files:
                feature_header = gherkin_to_md(feature_inner, feature=up_feature_level)
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
        paste_feature_level = st.number_input("Header level for the Feature line", value=2, min_value=1,
                                              max_value=6, key="paste_feature_h")
    with col2:
        paste_background_level = st.number_input("Header level for the Background line", value=3, min_value=1,
                                                 max_value=6, key="paste_background_h")
    with col3:
        paste_scenario_level = st.number_input("Header level for the Scenario line", value=3, min_value=1,
                                               max_value=6, key="paste_scenario_h")

    if paste_feature_level > 3 or paste_background_level > 3 or paste_scenario_level > 3:
        st.info("Note: Notion only supports header levels up to level three ('###')")

    if user_input is not None:
        markdown = []
        lines = user_input.splitlines()
        for index, line in enumerate(lines):
            line = gherkin_to_md(line, feature=paste_feature_level, background=paste_background_level,
                                 scenario=paste_scenario_level)
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
