import streamlit as st
import os
import json
from PIL import Image
from datetime import datetime

# Function to get list of image files in a directory
def get_image_files(folder_path):
    image_extensions = ['.png', '.jpg', '.jpeg']
    return [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]

# Function to save statuses to a JSON file
def save_statuses(statuses, folder_path):
    try:
        with open(os.path.join(folder_path, "statuses.json"), "w") as f:
            json.dump(statuses, f)
        st.success("Statuses saved successfully!")
    except Exception as e:
        st.error(f"Error saving statuses: {e}")

# Function to load statuses from a JSON file
def load_statuses(folder_path, status_options):
    statuses_file = os.path.join(folder_path, "statuses.json")
    if os.path.exists(statuses_file):
        try:
            with open(statuses_file, "r") as f:
                statuses = json.load(f)
                # Ensure loaded statuses are within current status options
                for image_file, status in list(statuses.items()):
                    if status not in status_options:
                        statuses[image_file] = status_options[0]  # Default to the first status option
                return statuses
        except Exception as e:
            st.error(f"Error loading statuses: {e}")
    return {}

# Function to display images and status input with dynamic radio buttons
def display_images_with_status(folder_path, status_options):
    image_files = get_image_files(folder_path)
    
    statuses = load_statuses(folder_path, status_options)
    new_statuses = {}

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        try:
            image = Image.open(image_path)
            # Resize the image to 50% of its original size
            image = image.resize((image.width // 2, image.height // 2))
            st.image(image, caption=image_file)
            
            # Display dynamic radio buttons for status options
            selected_status = st.radio(f"Select status for {image_file}", status_options, index=status_options.index(statuses.get(image_file, status_options[0])))
            
            new_statuses[image_file] = selected_status
            st.write(f"Status for {image_file}: {selected_status}")
        except Exception as e:
            st.error(f"Error displaying image {image_file}: {e}")

    save_statuses(new_statuses, folder_path)

# Function to display status summary with dynamic expanders
def display_status_summary_with_expanders(folder_path, status_options):
    statuses = load_statuses(folder_path, status_options)
    status_counts = {status: 0 for status in status_options}

    # Count statuses
    for status in statuses.values():
        if status in status_counts:
            status_counts[status] += 1

    st.subheader("Status Overview:")
    for status in status_options:
        st.write(f"- {status}: {status_counts[status]} image(s)")

    # Display expanders for each status
    for status in status_options:
        with st.expander(f"{status} Images ({status_counts[status]} images)"):
            for image_file, image_status in statuses.items():
                if image_status == status:
                    st.write(f"- {image_file}")

# Main function to run the Streamlit app
def main():
    st.title("Image Status Input")
    
    selected_date = st.date_input("Select a date", value=datetime.today())
    folder_path = selected_date.strftime("%Y%m%d")

    # Define the status options dynamically with English - Chinese pairs
    status_options_dict = {
        "正常-OK": "正常",
        "无法在微信打开-Không mở được trong wechat": "无法在微信打开",
        "无法在Chrome打开-Không mở được trong chrome": "无法在Chrome打开"
    }

    # Display multiselect with determined default options
    status_options = st.multiselect("Select status options",
                                    list(status_options_dict.keys()),
                                    default=list(status_options_dict.keys()))

    if os.path.isdir(folder_path):
        display_status_summary_with_expanders(folder_path, status_options)
        st.markdown("---")
        display_images_with_status(folder_path, status_options)
    else:
        st.write("No images found for the selected date")

if __name__ == "__main__":
    main()
