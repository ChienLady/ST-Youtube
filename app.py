import streamlit as st
def draw_style():
    st.set_page_config(page_title = "Youtube",
                       page_icon = "🔥",
                       layout = "wide",
                       menu_items = {
                          "Get help": "https://www.facebook.com/chienlady/",
                          "Report a Bug": "https://www.facebook.com/chienlady/",
                          "About": "Trang web có mục đích riêng rư."
                       })

    style = """
        <style>
            header {visibility: visible;}
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(style, unsafe_allow_html = True)
draw_style()

import yaml
import os
import streamlit_authenticator as stauth

from components import ytb

CREDENTIAL_PATH = os.path.join("configs", "credentials.yml")

with open(CREDENTIAL_PATH, "r") as file:
    st.session_state["config"] = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    st.session_state["config"]["credentials"],
    st.session_state["config"]["cookie"]["name"],
    st.session_state["config"]["cookie"]["key"],
    st.session_state["config"]["cookie"]["expiry_days"],
    st.session_state["config"]["preauthorized"]
)

def save_config():
    with open(CREDENTIAL_PATH, "w") as file:
        yaml.dump(st.session_state["config"], file)

def login():
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status:
        st.session_state["name"] = name
        st.session_state["username"] = username
    elif authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
    
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = authentication_status

def register():
    try:
        if authenticator.register_user("Register user", preauthorization = False):
            save_config()
            st.success("User registered successfully")
    except Exception as e:
        st.error(e)

def forgot_password():
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password("Forgot password")
        if username_forgot_pw:
            st.success(f"New password is updated for user {username_forgot_pw}: **{random_password}**. Please remmember it!")
            save_config()
        else:
            st.error("Username not found")
    except Exception as e:
        st.error(e)

def forgot_username():
    try:
        username_forgot_username, email_forgot_username = authenticator.forgot_username("Forgot username")
        if username_forgot_username:
            st.success(f"Your username is **{username_forgot_username}**")
        else:
            st.error("Email not found")
    except Exception as e:
        st.error(e)

def login_required():
    login_page, register_page, forgot_password_page, forgot_username_page = \
        st.tabs(["Login", "Register", "Forgot password", "Forgot username"])
    with login_page:
        login()
    with register_page:
        register()
    with forgot_password_page:
        forgot_password()
    with forgot_username_page:
        forgot_username()

def login_success():
    st.sidebar.image("https://media.giphy.com/media/3o7aDgf134NzaaHI8o/giphy-downsized-large.gif")
    st.sidebar.header(f"Welcom {st.session_state['name']}!")
    authenticator.logout("Logout", "sidebar")
    setting = st.sidebar.selectbox("Account settings",
                                    ("Not selected",
                                    "Reset password",
                                    "Update user details"),
                                    key = "account_setting")
    if setting == "Reset password":
        try:
            if authenticator.reset_password(st.session_state["username"], "Reset password", "sidebar"):
                save_config()
                st.success("Password modified successfully")
        except Exception as e:
            st.error(e)
    elif setting == "Update user details":
        try:
            if authenticator.update_user_details(st.session_state["username"], "Update user details", "sidebar"):
                save_config()
                st.success("Entries updated successfully")
        except Exception as e:
            st.error(e)
    ytb.main()

def main():
    if not st.session_state.get("authentication_status", False):
        login_required()
    else:
        login_success()

if __name__ == "__main__":
    main()