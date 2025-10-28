import streamlit as st
import requests
import csv
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
CSV_FILE = "verified_users.csv"
REPO_OWNER = "fetchai"
REPO_NAME = "innovation-lab-examples"

def check_star_status(username, repo_owner, repo_name):
    """Check if a user has starred a specific repository"""
    url = f"https://api.github.com/users/{username}/starred"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            starred_repos = response.json()
            for repo in starred_repos:
                if repo['owner']['login'] == repo_owner and repo['name'] == repo_name:
                    return True
        return False
    except requests.RequestException:
        return False

def is_user_already_verified(username):
    """Check if username already exists in CSV file"""
    if not os.path.isfile(CSV_FILE):
        return False
    
    try:
        df = pd.read_csv(CSV_FILE)
        return username in df['username'].values
    except (pd.errors.EmptyDataError, KeyError):
        return False

def save_to_csv(username, repo_owner, repo_name, timestamp):
    """Save verified user data to CSV file"""
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='') as csvfile:
        fieldnames = ['username', 'repo_owner', 'repo_name', 'verified_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'username': username,
            'repo_owner': repo_owner,
            'repo_name': repo_name,
            'verified_at': timestamp
        })

def load_verified_users():
    """Load and display verified users from CSV"""
    if os.path.isfile(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df
    return pd.DataFrame()

def main():
    st.title("🌟 GitHub Star Verification")
    st.write("Enter a GitHub username to verify if they have starred the repository")
    
    # Highlight the repository link for users to star first
    st.markdown("### 📌 **First, please star this repository:**")
    st.markdown("### 🔗 [https://github.com/fetchai/innovation-lab-examples](https://github.com/fetchai/innovation-lab-examples)")
    st.markdown("---")
    
    # Main form
    with st.form("verification_form"):
        username = st.text_input("GitHub Username", placeholder="Enter GitHub username")
        submit_button = st.form_submit_button("Verify Star")
        
        if submit_button and username:
            with st.spinner("Checking star status..."):
                has_starred = check_star_status(username, REPO_OWNER, REPO_NAME)
                
                if has_starred:
                    st.success(f"✅ {username} has starred the repository!")
                    
                    # Check if user already exists before saving
                    if is_user_already_verified(username):
                        st.warning(f"⚠️ {username} is already verified in the system")
                    else:
                        # Save to CSV
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        save_to_csv(username, REPO_OWNER, REPO_NAME, timestamp)
                        st.info("User data saved to CSV file")
                else:
                    st.error(f"❌ {username} has not starred the repository")
        
        elif submit_button and not username:
            st.error("Please enter a GitHub username")
    
    # Display verified users
    st.header("Verified Users")
    df = load_verified_users()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Download CSV option
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="verified_users.csv",
            mime="text/csv"
        )
    else:
        st.info("No verified users yet")

if __name__ == "__main__":
    main()