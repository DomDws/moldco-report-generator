# MoldCo - Automated Patient Progress Reports

This project contains a Python script that automatically generates a visual patient progress report based on a design template created in Figma.

---

### How to Use

1.  **Prerequisites:** Make sure you have Python 3 installed.
2.  **Install Libraries:** Open a terminal in this folder and run the following command to install the necessary libraries:
    `pip install -r requirements.txt`
3.  **Update Data:** Open the `create_report.py` file and modify the `patient_symptom_data` dictionary with the new patient's information.
4.  **Run the Script:** In the terminal, run the script:
    `python create_report.py`
5.  **Done:** The final report will be saved as a PNG file in this folder.

---

### Files in this Project

* `create_report.py`: The main Python script that runs the automation.
* `report_template.svg`: The design template exported from Figma.
* `Inter-VariableFont_opsz,wght.ttf`: The custom font file used in the design.
* `README.md`: This instruction file.
* `requirements.txt`: A list of the required Python libraries.
* `.gitignore`: Specifies files for Git to ignore.