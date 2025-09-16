# 🚀 GitHub Assistant - Quick Start Guide

## 📥 **First Time Setup (5 Minutes)**

### **Step 1: Download & Extract**
1. Download the GitHub Assistant folder
2. Extract it to your desired location (e.g., Desktop)
3. Keep the folder - you'll need it to run the app

### **Step 2: Run Setup**
1. **Double-click `setup.bat`**
2. Follow the on-screen instructions
3. The setup will check for Python, Git, and Git LFS
4. Install any missing requirements

### **Step 3: Launch the App**
1. **Double-click `run.bat`**
2. The app will start and show a welcome wizard
3. Follow the 3-step setup in the app

## 🔑 **Getting Your GitHub Token**

### **Option 1: Use the App's Built-in Guide**
1. When the app opens, click "🌐 Open GitHub Token Page"
2. Follow the step-by-step instructions in the app

### **Option 2: Manual Setup**
1. Go to: https://github.com/settings/tokens/new
2. Click "Generate new token (classic)"
3. Name it "GitHub Assistant"
4. Select these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

## 🎯 **Using the App**

### **Upload Your First Project**
1. **Connect to GitHub** - Enter your token and click "Connect"
2. **Select Project Folder** - Click "Browse" and choose your project
3. **Upload Project** - Click "📤 Upload Project to GitHub"
4. **Choose Repository** - Select existing repo or create new one
5. **Enter Commit Message** - Describe your changes
6. **Click Upload** - Watch the progress in the log area

### **Other Features**
- **🆕 Create Repository** - Make new GitHub repositories
- **🔄 Update Repository** - Push changes to existing repos
- **📋 Clone Repository** - Download repos to your computer
- **🗑️ Delete Repository** - Remove repos (with confirmation)
- **📊 View Repository Info** - See repo details and stats

## ⚡ **Pro Tips**

### **For Large Files (500MB+)**
- Install Git LFS: https://git-lfs.github.io/
- The app will automatically handle large files
- You'll see warnings for files > 100MB

### **For Best Performance**
- Keep your project folder organized
- Use meaningful commit messages
- Don't upload unnecessary files (use .gitignore)

### **Troubleshooting**
- **"Python not found"** → Run setup.bat first
- **"Git not found"** → Install Git from git-scm.com
- **"Connection failed"** → Check your token and internet
- **"Upload failed"** → Check file sizes and Git LFS

## 🆘 **Need Help?**

### **Common Issues**
- **App won't start** → Run setup.bat first
- **Can't connect to GitHub** → Check your token
- **Upload fails** → Check file sizes and Git LFS
- **"Not responding"** → Wait, large uploads take time

### **Getting Support**
- Check the log area for error messages
- Make sure all requirements are installed
- Verify your GitHub token has correct permissions

## 🎉 **You're Ready!**

Once setup is complete, you can:
- Upload projects with just a few clicks
- Manage GitHub repositories easily
- Handle large files automatically
- Enjoy a smooth, responsive experience

**Happy coding!** 🚀
