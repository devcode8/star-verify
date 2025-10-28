import streamlit as st
import pandas as pd
import random
import time
import os
from datetime import datetime

CSV_FILE = "verified_users.csv"

def load_verified_users():
    """Load verified users from CSV file"""
    if not os.path.isfile(CSV_FILE):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(CSV_FILE)
        # Remove empty rows and strip whitespace
        df = df.dropna(subset=['username'])
        df['username'] = df['username'].str.strip()
        # Remove rows where username is empty string after stripping
        df = df[df['username'] != '']
        # Create a temporary column for case-insensitive duplicate removal
        df['username_lower'] = df['username'].str.lower()
        # Remove case-insensitive duplicate usernames (keep first occurrence)
        df = df.drop_duplicates(subset=['username_lower'], keep='first')
        # Drop the temporary column
        df = df.drop('username_lower', axis=1)
        return df
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return pd.DataFrame()

def get_random_winner(df):
    """Select a random winner from the dataframe"""
    if df.empty:
        return None
    
    return df.sample(n=1).iloc[0]

def show_gacha_animation():
    """Display gacha-style animation"""
    placeholder = st.empty()
    
    # Animation frames
    frames = ["🎰", "🎲", "🎯", "🎪", "🎉", "⭐", "🏆"]
    
    for i in range(15):
        with placeholder.container():
            st.markdown(f"<div style='text-align: center; font-size: 80px;'>{random.choice(frames)}</div>", 
                       unsafe_allow_html=True)
        time.sleep(0.2)
    
    placeholder.empty()

def main():
    st.set_page_config(
        page_title="Lucky Draw Gacha",
        page_icon="🎰",
        layout="centered"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .big-font {
        font-size: 50px !important;
        text-align: center;
        font-weight: bold;
    }
    .winner-card {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .gacha-button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>🎰 Lucky Draw Gacha 🎰</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>✨ Spin the wheel and find your winner! ✨</h3>", 
                unsafe_allow_html=True)
    
    # Load users
    df = load_verified_users()
    
    if df.empty:
        st.error("❌ No verified users found! Please run the verification system first.")
        st.info("💡 Users need to be verified in the star verification system before they can participate in the lucky draw.")
        return
    
    # Display participant count
    st.info(f"🎯 **{len(df)} verified users** are eligible for the lucky draw!")
    
    # Show participants in an expander
    with st.expander("👥 View All Participants"):
        st.dataframe(df[['username', 'verified_at']], use_container_width=True)
    
    st.markdown("---")
    
    # Main gacha section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎲 DRAW WINNER! 🎲", use_container_width=True):
            st.markdown("<div class='big-font'>🎰 Drawing... 🎰</div>", unsafe_allow_html=True)
            
            # Show animation
            show_gacha_animation()
            
            # Select winner
            winner = get_random_winner(df)
            
            if winner is not None:
                # Celebration
                st.balloons()
                
                # Winner announcement
                st.markdown(f"""
                <div class='winner-card'>
                    <h1>🏆 WINNER! 🏆</h1>
                    <h2 style='color: #FF1493; margin: 20px 0;'>@{winner['username']}</h2>
                    <p><strong>Verified on:</strong> {winner['verified_at']}</p>
                    <p>🎉 Congratulations! 🎉</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Additional celebration effects
                time.sleep(1)
                st.snow()
                
                # Winner details
                st.success(f"🎊 The lucky winner is **@{winner['username']}**! 🎊")
                
                # Option to draw again
                st.markdown("---")
                if st.button("🔄 Draw Another Winner"):
                    st.experimental_rerun()
    
    # Statistics section
    st.markdown("---")
    st.markdown("### 📊 Lucky Draw Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Participants", len(df))
    
    with col2:
        if not df.empty:
            latest_verification = df['verified_at'].max()
            st.metric("Latest Verification", latest_verification.split()[0] if latest_verification else "N/A")
    
    with col3:
        win_probability = f"{(1/len(df)*100):.2f}%" if len(df) > 0 else "0%"
        st.metric("Win Probability", win_probability)
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #666;'>🌟 May the odds be ever in your favor! 🌟</p>", 
                unsafe_allow_html=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Run with custom port
        import subprocess
        subprocess.run(["streamlit", "run", __file__, "--server.port", "8502"])
    else:
        main()