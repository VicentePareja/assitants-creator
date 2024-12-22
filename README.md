# README

## Google Docs Text Fetcher

This project fetches text from a Google Doc using the Google Docs API. It is structured to use a `parametros.py` file for configuration.

### Prerequisites

1. **Python**: Ensure Python 3.7 or higher is installed.
2. **Google Cloud Project**:
   - Enable the **Google Docs API** and **Google Drive API**.
   - Create a service account and download its JSON credentials file.
   - Share the Google Doc with the service account email to grant access.
3. **Install dependencies**:
   ```bash
   pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
   ```

### Files

1. **`fetch_google_doc.py`**:
   - Main script that fetches and prints the content of a Google Doc.
2. **`parametros.py`**:
   - Configuration file that contains:
     - Path to the service account JSON file.
     - Google Doc ID.
3. **`README.md`**:
   - Documentation for setting up and running the project.

### Usage

1. Replace the placeholders in `parametros.py`:
   - `path_to_your_service_account.json`: Path to your service account JSON file.
   - `DOCUMENT_ID`: The ID of your Google Doc (from the URL).

2. Run the script:
   ```bash
   python fetch_google_doc.py
   ```

### Output

The script prints the content of the specified Google Doc to the console.

### Notes

- Ensure the Google Doc is shared with the service account email.
- Do not expose your service account JSON file publicly for security reasons.

