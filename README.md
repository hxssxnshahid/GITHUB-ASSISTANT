# 🚀 GitHub Assistant

A simple Windows desktop application that makes GitHub operations easy with just a few clicks! Perfect for developers who want to manage their GitHub repositories without using the command line.

## ✨ Features

- **🆕 Create New Repository** - Create public or private repositories with descriptions
- **📤 Upload Project to GitHub** - Upload your local projects to existing repositories
- **🔄 Update Existing Repository** - Update your repositories with new code
- **📋 Clone Repository** - Clone repositories to your local machine
- **🗑️ Delete Repository** - Safely delete repositories (with confirmation)
- **📊 View Repository Info** - Get detailed information about your repositories

## 🛠️ Installation & Usage

1. **Download the files** to a folder on your computer
2. **Run `START_HERE.bat`** to get started, follow the instructions.

**Always use 'START_HERE.bat' to launch the application, input 1 for first time, and 2 if you have already done the first time setup and want to use the app as normal**

**Once you are done with using the app, you can close both the windows, the application and the previously opened terminal.**


### Manual Installation

If the batch files don't work, you can install manually:

```bash
pip install -r requirements.txt
python github_assistant.py
```

## 🔑 Getting Started

### 1. Get a GitHub Personal Access Token

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens/new)
2. Click "Generate new token (classic)"
3. Give it a name like "GitHub Assistant"
4. Select these scopes:
   - `repo` (Full control of private repositories)
   - `public_repo` (Access public repositories)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### 2. Connect to GitHub

1. Open the GitHub Assistant
2. Paste your token in the "Personal Access Token" field
3. Click "Connect"
4. You should see a success message with your GitHub username

### 3. Select Your Project

1. Click "Browse" next to "Project Folder"
2. Select the folder containing your project
3. The path will be saved for next time

## 🎯 How to Use

### Create a New Repository
1. Click "🆕 Create New Repository"
2. Enter repository name and description
3. Choose public or private
4. Click "Create Repository"

### Upload Your Project
1. Make sure you've selected your project folder
2. Click "📤 Upload Project to GitHub"
3. Select the target repository
4. Enter a commit message
5. Click "Upload Project"

### Update an Existing Repository
1. Select your project folder
2. Click "🔄 Update Existing Repository"
3. Choose the repository to update
4. Enter a commit message
5. Click "Update Repository"

### Clone a Repository
1. Click "📋 Clone Repository"
2. Enter the repository URL (e.g., `https://github.com/username/repo.git`)
3. Choose where to clone it
4. Click "Clone Repository"

### Delete a Repository
1. Click "🗑️ Delete Repository"
2. Select the repository to delete
3. Check the confirmation box
4. Click "Delete Repository" (be careful!)

### View Repository Information
1. Click "📊 View Repository Info"
2. Select a repository
3. Click "View Info" to see details

## 🔧 Requirements

- Windows 10 or later
- Python 3.7 or later
- Git (for cloning repositories)
- Git LFS (for large files > 100MB) - [Download here](https://git-lfs.github.io/)
- Internet connection

## 📝 Notes

- Your GitHub token is stored locally in `github_config.json`
- The last selected project folder is remembered
- All operations are logged in the status area
- The app remembers your settings between sessions
- **Large file support**: Files > 100MB are automatically handled with Git LFS
- **Upload timeouts**: Large uploads have a 1-hour timeout limit
- **File size warnings**: You'll be warned about large files before upload

## 🚨 Important Security Notes

- Never share your GitHub Personal Access Token
- The token is stored locally on your computer in `github_config.json`
- The config file is automatically excluded from Git commits via `.gitignore`
- If you suspect your token is compromised, revoke it on GitHub and create a new one
- Always use tokens with minimal required permissions

## 🐛 Troubleshooting

### "Git is not installed" Error
- Install Git from [git-scm.com](https://git-scm.com/)
- Make sure Git is added to your system PATH

### "Failed to connect to GitHub" Error
- Check your internet connection
- Verify your token is correct
- Make sure the token has the required permissions

### "Repository not found" Error
- Make sure you have access to the repository
- Check the repository name is spelled correctly

## 📞 Support

If you encounter any issues:
1. Check the log area for error messages
2. Make sure all requirements are installed
3. Verify your GitHub token has the correct permissions

## 🎉 Enjoy!

This tool should make your GitHub workflow much easier. No more command line needed for basic GitHub operations!
