def gherkin_to_md(text, feature=2, background=3, scenario=3):
    text = text.strip() + "\n"
    h = "#"
    if text.startswith("Feature") or text.startswith("feature"):
        text = text.replace("Feature", f"{h * feature} Feature")
        text = text.replace("feature", f"{h * feature} Feature")
        text = text.title()
    elif text.startswith("Background"):
        text = text.replace("Background", f"{h * background} Background")
    elif text.startswith("Scenario"):
        text = text.replace("Scenario", f"{h * scenario} Scenario")
    elif text.startswith("Given"):
        text = text.replace("Given", "- **Given**")
    elif text.startswith("When"):
        text = text.replace("When", "- **When**")
    elif text.startswith("Then"):
        text = text.replace("Then", "- **Then**")
    elif text.startswith("And"):
        text = text.replace("And", "    - **And**")
    elif text.startswith("But"):
        text = text.replace("But", "    - **But**")
    return text