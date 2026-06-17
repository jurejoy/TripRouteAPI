# TripRouteAPI

TripRouteAPI is a Python application that queries the Gemini API with Google Maps grounding to generate structured travel route reports, and exports them to a polished PDF document. It supports mixed CJK (Chinese, Japanese, Korean) and English text rendering.

## Features

*   **Google Maps Grounding**: Uses Gemini models grounded with Google Maps to retrieve accurate transit information.
*   **Public Transit Details**: Automatically requests and includes operating hours, schedules, and frequency for public transport options.
*   **PDF Generation**: Exports results into a clean, multi-page PDF report.
*   **Multi-language Support**: Handles mixed CJK/English content and ensures correct font fallback rendering in PDFs.
*   **Source Translation**: Translates CJK source titles to English to bypass PDF link rendering limitations.

---

## Setup & Configuration

### Prerequisites

*   Python 3.10+
*   Google Cloud Project with Vertex AI / Gemini API access.
*   Standard Linux fonts (specifically `LiberationSans` and `DroidSansFallback` usually found on Debian/Ubuntu).

### 1. Environment Preparation (Linux)

Ensure the required system fonts are installed (for PDF rendering):

```bash
sudo apt-get update
sudo apt-get install fonts-liberation fonts-droid-fallback
```

### 2. Installation

Clone the repository (if not already local) and set up a Python virtual environment:

```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Cloud Authentication

The application uses the official Google GenAI SDK. You must configure your Google Cloud Project ID and authenticate:

```bash
# Set your GCP Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Authenticate your terminal
gcloud auth application-default login
```

---

## Running Queries

You can execute the script by passing one or more queries via the command line.

### Examples

*   **Single Query**:
    ```bash
    python3 main.py --query "东京成田机场去佐渡岛交通（分自驾和公共交通两种）"
    ```

*   **Multiple Queries**:
    Pass multiple queries space-separated under the same `--query` flag. The generator will create a new page for each query in the final PDF.
    ```bash
    python3 main.py --query "东京成田机场去佐渡岛交通（分自驾和公共交通两种）" "马累机场去索尼娃西度度假村的交通"
    ```

*   **Custom Output File**:
    Use the `--output` flag to specify a custom filename (defaults to `report.pdf`).
    ```bash
    python3 main.py --query "马累机场去索尼娃西度度假村的交通" --output male_report.pdf
    ```

---

## Syncing to GitHub

To push your local changes to the GitHub repository:

```bash
# Stage all changes
git add .

# Commit changes
git commit -m "Your descriptive commit message"

# Push to GitHub
git push origin main
```
