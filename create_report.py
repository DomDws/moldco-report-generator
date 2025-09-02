import xml.etree.ElementTree as ET
from svglib import svglib
import os
import base64

print("--- MoldCo Report Generator Initialized ---")

# Font embedding configuration
INTER_FONT_PATH = "Inter-VariableFont_opsz,wght.ttf"
FONT_FAMILY_NAME = "Inter"

# --- 1. PATIENT DATA INPUT ---
# This is the only section you'll need to change for each new report.

patient_identifier = "3051"
patient_symptom_data = {
    "July 25": {
        "Fatigue": True,
        "Brain Fog": True,
        "Headaches": True,
        "Joint Pain": True,
        "Skin Irritation": False,
        "Insomnia": True,
        "Digestive Issues": True
    },
    "Sept 25": {
        "Fatigue": True,
        "Brain Fog": False,
        "Headaches": False,
        "Joint Pain": True,
        "Skin Irritation": False,
        "Insomnia": False,
        "Digestive Issues": False
    }
}

def embed_font_in_svg(svg_string, font_path, font_family):
    """
    Embeds a TTF font file into the SVG as a base64-encoded font-face.
    This ensures the font displays correctly even if not installed on the system.
    """
    try:
        # Read the font file and encode it as base64
        with open(font_path, 'rb') as font_file:
            font_data = font_file.read()
            font_base64 = base64.b64encode(font_data).decode('utf-8')
        
        # Create the font-face CSS rule
        font_face_css = f"""
        <style>
        @font-face {{
            font-family: '{font_family}';
            src: url(data:font/ttf;base64,{font_base64}) format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        </style>
        """
        
        # Insert the font-face CSS after the opening <svg> tag
        svg_start = svg_string.find('<svg')
        if svg_start != -1:
            # Find the end of the opening svg tag
            svg_end = svg_string.find('>', svg_start) + 1
            # Insert the font-face CSS after the opening svg tag
            svg_string = svg_string[:svg_end] + font_face_css + svg_string[svg_end:]
            print(f"✅ Successfully embedded {font_family} font")
        else:
            print(f"⚠️  Could not find <svg> tag to embed font")
            
    except FileNotFoundError:
        print(f"⚠️  Font file not found: {font_path}")
        print("   Reports will use system fonts if Inter is not installed")
    except Exception as e:
        print(f"⚠️  Error embedding font: {e}")
        print("   Reports will use system fonts if Inter is not installed")
    
    return svg_string

# --- 2. REPORT GENERATION ENGINE ---
# This function contains all the logic.

def generate_report(patient_id, data, template_name="report_template.svg"):
    # First, register the SVG namespace. This is crucial for finding elements.
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    print(f"Generating report for Patient #{patient_id}...")

    # --- Read the template file ---
    try:
        with open(template_name, 'r', encoding='utf-8') as f:
            svg_string = f.read()
    except FileNotFoundError:
        print(f"FATAL ERROR: The template file '{template_name}' was not found.")
        print("Please make sure it's in the same folder as the script.")
        return

    # --- Embed the Inter font ---
    print("Embedding Inter font...")
    svg_string = embed_font_in_svg(svg_string, INTER_FONT_PATH, FONT_FAMILY_NAME)

    # --- Get data points ---
    time_points = list(data.keys())
    baseline_key, followup_key = time_points[0], time_points[1]
    symptom_list = sorted(data[baseline_key].keys())

    # --- A) Handle simple text replacements first ---
    # This is easier than finding and editing text nodes in XML.
    print(f"Replacing placeholders...")
    print(f"Baseline key: {baseline_key}")
    print(f"Followup key: {followup_key}")
    print(f"Symptoms: {symptom_list}")
    
    # Replace baseline and followup placeholders
    svg_string = svg_string.replace('{{Baseline}}', baseline_key)
    svg_string = svg_string.replace('{{Follow-Up}}', followup_key)  # Note: Follow-Up with capital U
    
    # Replace symptom placeholders with actual symptom names
    for i, symptom in enumerate(symptom_list):
        placeholder = f'{{{{Symptom_{i+1}}}}}'
        print(f"Replacing {placeholder} with {symptom}")
        svg_string = svg_string.replace(placeholder, symptom)
    
    # Remove any remaining symptom placeholders (like Symptom_7 if you have fewer symptoms)
    for i in range(len(symptom_list) + 1, 10):  # Check up to Symptom_10
        placeholder = f'{{{{Symptom_{i}}}}}'
        print(f"Removing {placeholder}")
        svg_string = svg_string.replace(placeholder, '')
    
    # Calculate and replace percentage improvement
    baseline_symptoms = sum(data[baseline_key].values())
    followup_symptoms = sum(data[followup_key].values())
    improvement = baseline_symptoms - followup_symptoms
    if baseline_symptoms > 0:
        percentage = round((improvement / baseline_symptoms) * 100)
    else:
        percentage = 0
    print(f"Replacing {{percentage}} with {percentage}%")
    svg_string = svg_string.replace('{{percentage}}', f"{percentage}%")
    
    # Replace months placeholder
    print("Replacing {{months}} with 2")
    svg_string = svg_string.replace('{{months}}', '2')
    
    # Debug: Check if any placeholders remain
    remaining_placeholders = []
    import re
    for match in re.finditer(r'\{\{[^}]+\}\}', svg_string):
        remaining_placeholders.append(match.group())
    
    if remaining_placeholders:
        print(f"WARNING: These placeholders were NOT replaced: {set(remaining_placeholders)}")
    else:
        print("✅ All placeholders were successfully replaced!")
    
    # --- B) Parse the SVG and handle icon visibility ---
    # Now that text is replaced, we parse the string into an XML tree.
    root = ET.fromstring(svg_string.encode('utf-8'))

    print("Populating template with symptom data...")
    for i, symptom in enumerate(symptom_list):
        idx = i + 1 # Our layer names are 1-based (e.g., tick_base_1)

        # Find the icon elements by their ID (which you set in Figma)
        tick_base = root.find(f'.//*[@id="tick_base_{idx}"]', ns)
        cross_base = root.find(f'.//*[@id="cross_base_{idx}"]', ns)
        tick_followup = root.find(f'.//*[@id="tick_followup_{idx}"]', ns)
        cross_followup = root.find(f'.//*[@id="cross_followup_{idx}"]', ns)

        # Toggle visibility for BASELINE icons
        if data[baseline_key].get(symptom, False): # Symptom is PRESENT
            if tick_base is not None: tick_base.set('opacity', '0')
            if cross_base is not None: cross_base.set('opacity', '1')
        else: # Symptom is ABSENT
            if tick_base is not None: tick_base.set('opacity', '1')
            if cross_base is not None: cross_base.set('opacity', '0')
        
        # Toggle visibility for FOLLOW-UP icons
        if data[followup_key].get(symptom, False): # Symptom is PRESENT
            if tick_followup is not None: tick_followup.set('opacity', '0')
            if cross_followup is not None: cross_followup.set('opacity', '1')
        else: # Symptom is ABSENT
            if tick_followup is not None: tick_followup.set('opacity', '1')
            if cross_followup is not None: cross_followup.set('opacity', '0')

    # --- C) Save the final files ---
    output_svg_path = f"Patient_{patient_id}_Progress_Report.svg"
    final_tree = ET.ElementTree(root)

    # Save the final SVG file
    final_tree.write(output_svg_path, encoding='utf-8', xml_declaration=True)

    print(f"\n✅ SUCCESS! Your report has been saved as '{output_svg_path}'")
    print("You can open this SVG file in any web browser or vector graphics program.")
    print("The Inter font is now embedded, ensuring consistent display across all systems.")
    print("To convert to PNG, you can use online tools or programs like Inkscape.")

# --- 3. EXECUTE THE SCRIPT ---
generate_report(patient_identifier, patient_symptom_data)
