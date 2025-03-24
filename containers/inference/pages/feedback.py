import json
import boto3
import streamlit as st

# Add user input fields for cost estimation
st.subheader("User Feedback")

if "service_center" not in st.session_state:
    st.session_state.service_center = 0
if "estimated_cost" not in st.session_state:
    st.session_state.estimated_cost = 0
if "parts_for_repair" not in st.session_state:
    st.session_state.parts_for_repair = "Right fender, Paint"
if "labor_hours" not in st.session_state:
    st.session_state.labor_hours = 0
if "parts_cost" not in st.session_state:
    st.session_state.parts_cost = 0
if "labor_cost" not in st.session_state:
    st.session_state.labor_cost = 0
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

st.session_state.service_center = st.text_area("Service Center Name", value=st.session_state.service_center)
st.session_state.estimated_cost = st.number_input("Repair Cost ($)", min_value=0, step=10, value=st.session_state.estimated_cost)
st.session_state.parts_for_repair = st.text_area("Parts Required for Repair (comma-separated)", value=st.session_state.parts_for_repair)
st.session_state.labor_hours = st.number_input("Estimated Labor Hours", min_value=0, step=1, value=st.session_state.labor_hours)
st.session_state.parts_cost = st.number_input("Parts Cost ($)", min_value=0, step=10, value=st.session_state.parts_cost)
st.session_state.labor_cost = st.number_input("Labor Cost ($)", min_value=0, step=10, value=st.session_state.labor_cost)

# Convert parts_for_repair input from string to list
parts_for_repair_list = [part.strip() for part in st.session_state.parts_for_repair.split(",") if part.strip()]

if st.button("Submit"):
    BUCKET_NAME = "meet-harsh-vatsal-blog-store"
    FILE_NAME = "feedback.json"

    s3_client = boto3.client("s3")

    # Try to fetch the existing JSON file from S3
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        existing_data = json.loads(response["Body"].read().decode("utf-8"))  # Load existing JSON
    except s3_client.exceptions.NoSuchKey:
        existing_data = []  # If file doesn't exist, initialize an empty list

    # Ensure it's a list
    if not isinstance(existing_data, list):
        existing_data = []

    # Construct the new response data
    new_entry = {
        "make": st.session_state.selected,
        "model": st.session_state.selected_make,
        "state": "FL",
        "damage": st.session_state.selected_damage_area,
        "damage_severity": st.session_state.selected_damage_sev,
        "damage_description": st.session_state.damage_description,  # Claude 3 response
        "service_center": st.session_state.service_center,
        "repair_cost": st.session_state.estimated_cost,
        "parts_for_repair": parts_for_repair_list,  # Ensure list format
        "labor_hours": st.session_state.labor_hours,
        "parts_cost": st.session_state.parts_cost,
        "labor_cost": st.session_state.labor_cost,
        "s3_location": f"https://uploaded-images-bucket-for-blog.s3.us-east-1.amazonaws.com/{st.session_state.uploaded_file_data["filename"]}",
        "reference_images": st.session_state.similar_images,
        "relevance": st.session_state.relevance
    }

    # Append the new entry to the existing list
    existing_data.append(new_entry)

    # Convert to JSON string
    json_data = json.dumps(existing_data, indent=2)

    # Upload the updated JSON back to S3
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=FILE_NAME,
        Body=json_data,
        ContentType="application/json"
    )

    st.success(f"Feedback saved successfully!")