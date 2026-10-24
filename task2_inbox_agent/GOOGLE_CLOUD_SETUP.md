# Google Cloud & Gmail API Setup Guide

This guide walks you through setting up an official **Google Cloud Project** to enable **Sign in with Google** and direct **Gmail API** integration (composing, sending, and drafts) for the Intelligent Email Agent.

---

## 1. Create or Select a Google Cloud Project
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top of the page and select **New Project**.
3. Name your project (e.g. `Intelligent-Email-Agent`) and click **Create**.

---

## 2. Enable the Gmail API & Google People API
1. In the Google Cloud Console navigation menu, go to **APIs & Services > Library**.
2. Search for **Gmail API** and click on it.
3. Click **Enable**.
4. (Optional) Search for **Google People API** and enable it if you wish to retrieve extended profile pictures and contact info.

---

## 3. Configure the OAuth Consent Screen
1. In the navigation menu, go to **APIs & Services > OAuth consent screen**.
2. Select **User Type**:
   - Choose **External** (allows any Google account to sign in).
   - Click **Create**.
3. Fill in the App Information:
   - **App name**: `Intelligent Email Agent`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click **Save and Continue**.
5. **Scopes Configuration**:
   - Click **Add or Remove Scopes**.
   - Add the following scopes:
     - `.../auth/userinfo.email` (View your email address)
     - `.../auth/userinfo.profile` (See your personal info)
     - `openid` (Associate you with your personal info on Google)
     - `https://www.googleapis.com/auth/gmail.send` (Send email on your behalf)
     - `https://www.googleapis.com/auth/gmail.compose` (Manage drafts and send emails)
     - `https://www.googleapis.com/auth/gmail.readonly` (View your email messages and settings)
   - Click **Update** and then **Save and Continue**.
6. **Test Users (for development/testing)**:
   - While the app publishing status is in **Testing**, add the Google email addresses of users or evaluators who will test the application.
   - Click **Save and Continue**.

---

## 4. Create OAuth 2.0 Client ID Credentials
1. In the navigation menu, go to **APIs & Services > Credentials**.
2. Click **Create Credentials** at the top and select **OAuth client ID**.
3. Choose **Application type**: **Web application**.
4. Set **Name**: `Email Agent Web Client`.
5. Under **Authorized redirect URIs**, click **Add URI** and enter:
   ```
   http://localhost:8002/api/v1/auth/google/callback
   ```
   *(If deploying to production or using a public tunnel, also add your public URL callback, e.g. `https://your-domain.loca.lt/api/v1/auth/google/callback`)*.
6. Click **Create**.
7. Copy your **Client ID** and **Client Secret**.

---

## 5. Configure Credentials in the Application
You can supply your Google Cloud credentials using either of two methods:

### Method A: Environment File (.env)
Create or edit `task2_inbox_agent/.env`:
```bash
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8002/api/v1/auth/google/callback
```

### Method B: Live Web UI Setup
1. Launch the Email Agent web client at `http://localhost:8002`.
2. Click the **Sign in with Google** button in the header.
3. Expand the **⚙️ Custom Google Cloud Client ID & Secret Configuration** section.
4. Paste your **Client ID** and **Client Secret** and click **Save OAuth Credentials**.

---

## 6. Instant Demo / Sandbox Mode (Zero Setup Needed)
If you are evaluating the agent without your own Google Cloud Console credentials:
1. Open the Email Agent at `http://localhost:8002`.
2. Click **Sign in with Google**.
3. Click **⚡ Connect Demo Google Account (Suresh Gopi)**.
4. The system immediately simulates official Google OAuth 2.0 authentication, populates your profile badge, and provides full composition, AI synthesis, draft saving, and user approval workflows.
