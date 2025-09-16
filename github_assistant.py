import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import subprocess
import sys
from github import Github
from github.GithubException import GithubException
import threading
import webbrowser

class GitHubAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Assistant - Easy Project Management")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # GitHub API setup
        self.github = None
        self.current_repo = None
        self.project_path = None
        
        # Load configuration
        self.config_file = "github_config.json"
        self.load_config()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🚀 GitHub Assistant", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # GitHub Authentication Section
        auth_frame = ttk.LabelFrame(main_frame, text="GitHub Authentication", padding="10")
        auth_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        auth_frame.columnconfigure(1, weight=1)
        
        ttk.Label(auth_frame, text="Personal Access Token:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.token_var = tk.StringVar(value=self.config.get('token', ''))
        token_entry = ttk.Entry(auth_frame, textvariable=self.token_var, show="*", width=50)
        token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(auth_frame, text="Connect", 
                  command=self.connect_github).grid(row=0, column=2)
        
        ttk.Button(auth_frame, text="Get Token", 
                  command=self.open_token_page).grid(row=0, column=3, padx=(10, 0))
        
        # Project Selection Section
        project_frame = ttk.LabelFrame(main_frame, text="Project Selection", padding="10")
        project_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        project_frame.columnconfigure(1, weight=1)
        
        ttk.Label(project_frame, text="Project Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.project_var = tk.StringVar(value=self.config.get('last_project', ''))
        project_entry = ttk.Entry(project_frame, textvariable=self.project_var, width=50)
        project_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(project_frame, text="Browse", 
                  command=self.browse_project).grid(row=0, column=2)
        
        # GitHub Operations Section
        ops_frame = ttk.LabelFrame(main_frame, text="GitHub Operations", padding="10")
        ops_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Create buttons in a grid
        buttons = [
            ("🆕 Create New Repository", self.create_repo, 0, 0),
            ("📤 Upload Project to GitHub", self.upload_project, 0, 1),
            ("🔄 Update Existing Repository", self.update_repo, 0, 2),
            ("📋 Clone Repository", self.clone_repo, 1, 0),
            ("🗑️ Delete Repository", self.delete_repo, 1, 1),
            ("📊 View Repository Info", self.view_repo_info, 1, 2),
        ]
        
        for text, command, row, col in buttons:
            btn = ttk.Button(ops_frame, text=text, command=command, width=25)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure grid weights for buttons
        for i in range(3):
            ops_frame.columnconfigure(i, weight=1)
        
        # Status and Log Section
        status_frame = ttk.LabelFrame(main_frame, text="Status & Log", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(status_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def set_status(self, status):
        """Update status bar"""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def load_config(self):
        """Load configuration from file"""
        self.config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}
            
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def connect_github(self):
        """Connect to GitHub using token"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a GitHub Personal Access Token")
            return
            
        try:
            print(f"[DEBUG] Attempting to connect to GitHub...")
            print(f"[DEBUG] Token length: {len(token)}")
            print(f"[DEBUG] Token starts with: {token[:10]}...")
            
            self.github = Github(token)
            print(f"[DEBUG] GitHub object created successfully")
            
            # Test connection
            print(f"[DEBUG] Testing connection by getting user...")
            user = self.github.get_user()
            print(f"[DEBUG] User retrieved: {user.login}")
            print(f"[DEBUG] User ID: {user.id}")
            print(f"[DEBUG] User type: {user.type}")
            
            self.log_message(f"✅ Connected to GitHub as: {user.login}")
            self.set_status(f"Connected as {user.login}")
            
            # Save token
            self.config['token'] = token
            self.save_config()
            print(f"[DEBUG] Token saved to config")
            
        except GithubException as e:
            error_msg = f"Failed to connect to GitHub:\n{str(e)}"
            print(f"[DEBUG] GitHubException during connection: {str(e)}")
            print(f"[DEBUG] Exception type: {type(e)}")
            print(f"[DEBUG] Exception status: {getattr(e, 'status', 'No status')}")
            messagebox.showerror("GitHub Error", error_msg)
            self.log_message(f"❌ GitHub connection failed: {str(e)}")
        except Exception as e:
            error_msg = f"Unexpected connection error:\n{str(e)}"
            print(f"[DEBUG] Unexpected exception during connection: {str(e)}")
            print(f"[DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"[DEBUG] Full traceback:")
            traceback.print_exc()
            messagebox.showerror("Connection Error", error_msg)
            self.log_message(f"❌ Connection failed: {str(e)}")
            
    def open_token_page(self):
        """Open GitHub token creation page"""
        webbrowser.open("https://github.com/settings/tokens/new")
        self.log_message("🌐 Opened GitHub token creation page")
        
    def browse_project(self):
        """Browse for project folder"""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.project_var.set(folder)
            self.project_path = folder
            self.config['last_project'] = folder
            self.save_config()
            self.log_message(f"📁 Selected project folder: {folder}")
            
    def create_repo(self):
        """Create a new GitHub repository"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        # Create dialog for repo details
        dialog = RepoCreateDialog(self.root, self.github, self.log_message, self.set_status)
        self.root.wait_window(dialog.dialog)
        
    def upload_project(self):
        """Upload current project to GitHub"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        if not self.project_var.get():
            messagebox.showerror("Error", "Please select a project folder")
            return
            
        # Create dialog for upload details
        dialog = UploadDialog(self.root, self.github, self.project_var.get(), self.log_message, self.set_status)
        self.root.wait_window(dialog.dialog)
        
    def update_repo(self):
        """Update existing repository"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        if not self.project_var.get():
            messagebox.showerror("Error", "Please select a project folder")
            return
            
        # Create dialog for update details
        dialog = UpdateDialog(self.root, self.github, self.project_var.get(), self.log_message, self.set_status)
        self.root.wait_window(dialog.dialog)
        
    def clone_repo(self):
        """Clone a repository"""
        dialog = CloneDialog(self.root, self.log_message)
        self.root.wait_window(dialog.dialog)
        
    def delete_repo(self):
        """Delete a repository"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        dialog = DeleteDialog(self.root, self.github, self.log_message)
        self.root.wait_window(dialog.dialog)
        
    def view_repo_info(self):
        """View repository information"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        dialog = RepoInfoDialog(self.root, self.github, self.log_message)
        self.root.wait_window(dialog.dialog)

class RepoCreateDialog:
    def __init__(self, parent, github, log_callback, status_callback):
        self.github = github
        self.log_callback = log_callback
        self.status_callback = status_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Repository")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository name
        ttk.Label(main_frame, text="Repository Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.desc_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.desc_var, width=40).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Visibility
        ttk.Label(main_frame, text="Visibility:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.visibility_var = tk.StringVar(value="public")
        ttk.Radiobutton(main_frame, text="Public", variable=self.visibility_var, value="public").grid(row=5, column=0, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Private", variable=self.visibility_var, value="private").grid(row=6, column=0, sticky=tk.W, pady=(0, 10))
        
        # Options
        self.auto_init_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Initialize with README", variable=self.auto_init_var).grid(row=7, column=0, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, pady=(20, 0))
        
        self.create_btn = ttk.Button(button_frame, text="Create Repository", command=self.create_repo)
        self.create_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def create_repo(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a repository name")
            return
            
        # Disable button and show processing
        self.create_btn.config(state='disabled', text="Creating...")
        self.status_callback("Creating repository...")
        self.dialog.update()
        
        # Run in separate thread to prevent UI freezing
        def create_repo_thread():
            try:
                description = self.desc_var.get().strip()
                private = self.visibility_var.get() == "private"
                auto_init = self.auto_init_var.get()
                
                print(f"[DEBUG] Starting repository creation process...")
                print(f"[DEBUG] Repository name: '{name}'")
                print(f"[DEBUG] Description: '{description}'")
                print(f"[DEBUG] Private: {private}")
                print(f"[DEBUG] Auto init: {auto_init}")
                
                self.log_callback(f"🆕 Creating repository: {name}")
                
                # Check if repository already exists
                print(f"[DEBUG] Checking if repository '{name}' already exists...")
                try:
                    existing_repo = self.github.get_user().get_repo(name)
                    error_msg = f"Repository '{name}' already exists!"
                    print(f"[DEBUG] Repository already exists: {existing_repo.html_url}")
                    self.log_callback(f"❌ {error_msg}")
                    self.dialog.after(0, lambda: self.create_error(error_msg))
                    return
                except Exception as e:
                    print(f"[DEBUG] Repository doesn't exist (good): {str(e)}")
                    # Repository doesn't exist, continue with creation
                    pass
                
                print(f"[DEBUG] Getting GitHub user...")
                user = self.github.get_user()
                print(f"[DEBUG] User: {user.login}")
                
                print(f"[DEBUG] Calling create_repo API...")
                # Fix: Use GithubObject.NotSet instead of None for empty description
                from github import GithubObject
                desc_param = description if description else GithubObject.NotSet
                print(f"[DEBUG] Description parameter: {desc_param}")
                
                repo = user.create_repo(
                    name=name,
                    description=desc_param,
                    private=private,
                    auto_init=auto_init
                )
                
                print(f"[DEBUG] Repository created successfully: {repo.html_url}")
                # Update UI in main thread
                self.dialog.after(0, lambda: self.create_success(repo, name))
                
            except GithubException as e:
                error_msg = f"GitHub API Error: {str(e)}"
                print(f"[DEBUG] GitHubException: {str(e)}")
                print(f"[DEBUG] Exception type: {type(e)}")
                print(f"[DEBUG] Exception args: {e.args}")
                self.log_callback(f"❌ {error_msg}")
                # Update UI in main thread
                self.dialog.after(0, lambda: self.create_error(error_msg))
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                print(f"[DEBUG] Unexpected Exception: {str(e)}")
                print(f"[DEBUG] Exception type: {type(e)}")
                print(f"[DEBUG] Exception args: {e.args}")
                import traceback
                print(f"[DEBUG] Full traceback:")
                traceback.print_exc()
                self.log_callback(f"❌ {error_msg}")
                # Update UI in main thread
                self.dialog.after(0, lambda: self.create_error(error_msg))
        
        # Start the thread
        thread = threading.Thread(target=create_repo_thread, daemon=True)
        thread.start()
        
    def create_success(self, repo, name):
        """Handle successful repository creation"""
        self.log_callback(f"✅ Repository created successfully: {repo.html_url}")
        self.status_callback("Repository created successfully!")
        messagebox.showinfo("Success", f"Repository '{name}' created successfully!\n\nURL: {repo.html_url}")
        self.dialog.destroy()
        
    def create_error(self, error_msg):
        """Handle repository creation error"""
        self.create_btn.config(state='normal', text="Create Repository")
        self.status_callback("Ready")
        messagebox.showerror("Error", error_msg)

class UploadDialog:
    def __init__(self, parent, github, project_path, log_callback, status_callback):
        self.github = github
        self.project_path = project_path
        self.log_callback = log_callback
        self.status_callback = status_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Upload Project to GitHub")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository selection
        ttk.Label(main_frame, text="Select Repository:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.repo_var = tk.StringVar()
        repo_combo = ttk.Combobox(main_frame, textvariable=self.repo_var, width=40)
        repo_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Load repositories
        self.load_repositories(repo_combo)
        
        # Commit message
        ttk.Label(main_frame, text="Commit Message:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.commit_var = tk.StringVar(value="Initial commit")
        ttk.Entry(main_frame, textvariable=self.commit_var, width=40).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Branch
        ttk.Label(main_frame, text="Branch:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.branch_var = tk.StringVar(value="main")
        ttk.Entry(main_frame, textvariable=self.branch_var, width=40).grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, pady=(20, 0))
        
        ttk.Button(button_frame, text="Upload Project", command=self.upload_project).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def load_repositories(self, combo):
        """Load user repositories into combobox"""
        try:
            repos = list(self.github.get_user().get_repos())
            repo_names = [repo.name for repo in repos]
            combo['values'] = repo_names
            if repo_names:
                combo.current(0)
        except Exception as e:
            self.log_callback(f"❌ Failed to load repositories: {str(e)}")
            
    def upload_project(self):
        repo_name = self.repo_var.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Please select a repository")
            return
            
        try:
            repo = self.github.get_user().get_repo(repo_name)
            commit_msg = self.commit_var.get().strip() or "Update project"
            branch = self.branch_var.get().strip() or "main"
            
            self.log_callback(f"📤 Uploading project to {repo_name}...")
            
            # Get the project path from the main app
            project_path = self.project_path
            
            # Check if it's already a git repository
            if os.path.exists(os.path.join(project_path, '.git')):
                self.log_callback("📁 Project is already a git repository, pushing changes...")
                self.push_existing_repo(project_path, repo, commit_msg, branch)
            else:
                self.log_callback("📁 Initializing new git repository and uploading...")
                self.upload_new_repo(project_path, repo, commit_msg, branch)
            
        except GithubException as e:
            error_msg = f"Failed to upload project: {str(e)}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def push_existing_repo(self, project_path, repo, commit_msg, branch):
        """Push changes to existing git repository"""
        try:
            # Add remote if not exists
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  cwd=project_path, capture_output=True, text=True)
            if result.returncode != 0:
                # Add remote
                subprocess.run(['git', 'remote', 'add', 'origin', repo.clone_url], 
                             cwd=project_path, check=True)
                self.log_callback("🔗 Added remote origin")
            
            # Add all files
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            self.log_callback("📝 Added files to staging")
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=project_path, check=True)
            self.log_callback("💾 Committed changes")
            
            # Push to GitHub
            subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=project_path, check=True)
            self.log_callback(f"🚀 Pushed to {branch} branch")
            
            self.log_callback(f"✅ Project uploaded successfully to {repo.html_url}")
            messagebox.showinfo("Success", f"Project uploaded to {repo.name} successfully!")
            self.dialog.destroy()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {e.stderr}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def upload_new_repo(self, project_path, repo, commit_msg, branch):
        """Initialize new git repository and upload"""
        try:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
            self.log_callback("🆕 Initialized git repository")
            
            # Add remote
            subprocess.run(['git', 'remote', 'add', 'origin', repo.clone_url], 
                         cwd=project_path, check=True)
            self.log_callback("🔗 Added remote origin")
            
            # Add all files
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            self.log_callback("📝 Added files to staging")
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=project_path, check=True)
            self.log_callback("💾 Committed changes")
            
            # Rename branch to main if needed
            try:
                subprocess.run(['git', 'branch', '-M', branch], cwd=project_path, check=True)
                self.log_callback(f"🏷️ Renamed branch to {branch}")
            except:
                pass  # Branch might already be main
            
            # Push to GitHub
            subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=project_path, check=True)
            self.log_callback(f"🚀 Pushed to {branch} branch")
            
            self.log_callback(f"✅ Project uploaded successfully to {repo.html_url}")
            messagebox.showinfo("Success", f"Project uploaded to {repo.name} successfully!")
            self.dialog.destroy()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {e.stderr}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

class UpdateDialog:
    def __init__(self, parent, github, project_path, log_callback, status_callback):
        self.github = github
        self.project_path = project_path
        self.log_callback = log_callback
        self.status_callback = status_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Repository")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository selection
        ttk.Label(main_frame, text="Select Repository:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.repo_var = tk.StringVar()
        repo_combo = ttk.Combobox(main_frame, textvariable=self.repo_var, width=40)
        repo_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Load repositories
        self.load_repositories(repo_combo)
        
        # Commit message
        ttk.Label(main_frame, text="Commit Message:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.commit_var = tk.StringVar(value="Update project")
        ttk.Entry(main_frame, textvariable=self.commit_var, width=40).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(20, 0))
        
        self.update_btn = ttk.Button(button_frame, text="Update Repository", command=self.update_repo)
        self.update_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def load_repositories(self, combo):
        """Load user repositories into combobox"""
        try:
            repos = list(self.github.get_user().get_repos())
            repo_names = [repo.name for repo in repos]
            combo['values'] = repo_names
            if repo_names:
                combo.current(0)
        except Exception as e:
            self.log_callback(f"❌ Failed to load repositories: {str(e)}")
            
    def update_repo(self):
        repo_name = self.repo_var.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Please select a repository")
            return
            
        # Disable button and show processing
        self.update_btn.config(state='disabled', text="Updating...")
        self.status_callback("Updating repository...")
        self.dialog.update()
        
        # Run in separate thread
        def update_repo_thread():
            try:
                repo = self.github.get_user().get_repo(repo_name)
                commit_msg = self.commit_var.get().strip() or "Update project"
                
                self.log_callback(f"🔄 Updating repository {repo_name}...")
                
                # Check if project is a git repository
                if not os.path.exists(os.path.join(self.project_path, '.git')):
                    error_msg = "Project folder is not a git repository. Please use 'Upload Project' instead."
                    self.log_callback(f"❌ {error_msg}")
                    self.dialog.after(0, lambda: self.update_error(error_msg))
                    return
                
                # Add all files
                subprocess.run(['git', 'add', '.'], cwd=self.project_path, check=True)
                self.log_callback("📝 Added files to staging")
                
                # Check if there are changes to commit
                result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                      cwd=self.project_path, capture_output=True)
                if result.returncode == 0:
                    self.log_callback("ℹ️ No changes to commit")
                    self.dialog.after(0, lambda: self.update_success(repo_name, "No changes to commit"))
                    return
                
                # Commit changes
                subprocess.run(['git', 'commit', '-m', commit_msg], cwd=self.project_path, check=True)
                self.log_callback("💾 Committed changes")
                
                # Push to GitHub
                subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.project_path, check=True)
                self.log_callback("🚀 Pushed changes to GitHub")
                
                self.dialog.after(0, lambda: self.update_success(repo_name, "Repository updated successfully"))
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Git command failed: {e.stderr}"
                self.log_callback(f"❌ {error_msg}")
                self.dialog.after(0, lambda: self.update_error(error_msg))
            except FileNotFoundError:
                error_msg = "Git is not installed or not in PATH"
                self.log_callback(f"❌ {error_msg}")
                self.dialog.after(0, lambda: self.update_error(error_msg))
            except Exception as e:
                error_msg = f"Update failed: {str(e)}"
                self.log_callback(f"❌ {error_msg}")
                self.dialog.after(0, lambda: self.update_error(error_msg))
        
        # Start the thread
        thread = threading.Thread(target=update_repo_thread, daemon=True)
        thread.start()
        
    def update_success(self, repo_name, message):
        """Handle successful repository update"""
        self.log_callback(f"✅ {message}")
        self.status_callback("Repository updated successfully!")
        messagebox.showinfo("Success", f"Repository {repo_name} updated successfully!")
        self.dialog.destroy()
        
    def update_error(self, error_msg):
        """Handle repository update error"""
        self.update_btn.config(state='normal', text="Update Repository")
        self.status_callback("Ready")
        messagebox.showerror("Error", error_msg)

class CloneDialog:
    def __init__(self, parent, log_callback):
        self.log_callback = log_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Clone Repository")
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository URL
        ttk.Label(main_frame, text="Repository URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Clone directory
        ttk.Label(main_frame, text="Clone to:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.dir_var = tk.StringVar()
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=40).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(20, 0))
        
        ttk.Button(button_frame, text="Clone Repository", command=self.clone_repo).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Clone Directory")
        if directory:
            self.dir_var.set(directory)
            
    def clone_repo(self):
        url = self.url_var.get().strip()
        directory = self.dir_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a repository URL")
            return
            
        if not directory:
            messagebox.showerror("Error", "Please select a clone directory")
            return
            
        try:
            self.log_callback(f"📋 Cloning repository from {url}...")
            
            # Use git command to clone
            result = subprocess.run(['git', 'clone', url, directory], 
                                  capture_output=True, text=True, check=True)
            
            self.log_callback(f"✅ Repository cloned successfully to {directory}")
            messagebox.showinfo("Success", f"Repository cloned successfully to {directory}")
            self.dialog.destroy()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to clone repository: {e.stderr}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

class DeleteDialog:
    def __init__(self, parent, github, log_callback):
        self.github = github
        self.log_callback = log_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Delete Repository")
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository selection
        ttk.Label(main_frame, text="Select Repository to Delete:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.repo_var = tk.StringVar()
        repo_combo = ttk.Combobox(main_frame, textvariable=self.repo_var, width=40)
        repo_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Load repositories
        self.load_repositories(repo_combo)
        
        # Confirmation
        self.confirm_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="I understand this will permanently delete the repository", 
                       variable=self.confirm_var).grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(20, 0))
        
        ttk.Button(button_frame, text="Delete Repository", command=self.delete_repo).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def load_repositories(self, combo):
        """Load user repositories into combobox"""
        try:
            repos = list(self.github.get_user().get_repos())
            repo_names = [repo.name for repo in repos]
            combo['values'] = repo_names
            if repo_names:
                combo.current(0)
        except Exception as e:
            self.log_callback(f"❌ Failed to load repositories: {str(e)}")
            
    def delete_repo(self):
        repo_name = self.repo_var.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Please select a repository")
            return
            
        if not self.confirm_var.get():
            messagebox.showerror("Error", "Please confirm that you understand this will permanently delete the repository")
            return
            
        # Double confirmation
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{repo_name}'?\n\nThis action cannot be undone!"):
            return
            
        try:
            repo = self.github.get_user().get_repo(repo_name)
            repo.delete()
            
            self.log_callback(f"🗑️ Repository '{repo_name}' deleted successfully")
            messagebox.showinfo("Success", f"Repository '{repo_name}' deleted successfully!")
            self.dialog.destroy()
            
        except GithubException as e:
            error_msg = f"Failed to delete repository: {str(e)}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

class RepoInfoDialog:
    def __init__(self, parent, github, log_callback):
        self.github = github
        self.log_callback = log_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Repository Information")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Repository selection
        ttk.Label(main_frame, text="Select Repository:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.repo_var = tk.StringVar()
        repo_combo = ttk.Combobox(main_frame, textvariable=self.repo_var, width=40)
        repo_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Load repositories
        self.load_repositories(repo_combo)
        
        # Info display
        self.info_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.info_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(20, 0))
        
        ttk.Button(button_frame, text="View Info", command=self.view_info).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def load_repositories(self, combo):
        """Load user repositories into combobox"""
        try:
            repos = list(self.github.get_user().get_repos())
            repo_names = [repo.name for repo in repos]
            combo['values'] = repo_names
            if repo_names:
                combo.current(0)
        except Exception as e:
            self.log_callback(f"❌ Failed to load repositories: {str(e)}")
            
    def view_info(self):
        repo_name = self.repo_var.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Please select a repository")
            return
            
        try:
            repo = self.github.get_user().get_repo(repo_name)
            
            # Clear and populate info
            self.info_text.delete(1.0, tk.END)
            
            info = f"""Repository Information: {repo.name}

Description: {repo.description or 'No description'}
URL: {repo.html_url}
Clone URL: {repo.clone_url}
Language: {repo.language or 'Not specified'}
Stars: {repo.stargazers_count}
Forks: {repo.forks_count}
Watchers: {repo.watchers_count}
Issues: {repo.open_issues_count}
Created: {repo.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Updated: {repo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
Private: {'Yes' if repo.private else 'No'}
Archived: {'Yes' if repo.archived else 'No'}

Default Branch: {repo.default_branch}
Size: {repo.size} KB

Topics: {', '.join(repo.get_topics()) if hasattr(repo, 'get_topics') else 'None'}

README:
{self.get_readme_content(repo)}
"""
            
            self.info_text.insert(tk.END, info)
            self.log_callback(f"📊 Retrieved information for repository: {repo_name}")
            
        except GithubException as e:
            error_msg = f"Failed to get repository information: {str(e)}"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
            
    def get_readme_content(self, repo):
        """Get README content if available"""
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')[:500] + "..." if len(readme.decoded_content) > 500 else readme.decoded_content.decode('utf-8')
        except:
            return "No README available"

def main():
    # Enable console output for debugging
    import sys
    if sys.platform == "win32":
        # On Windows, try to show console
        try:
            import ctypes
            ctypes.windll.kernel32.AllocConsole()
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')
            print("Debug console enabled - you can see detailed logs here")
        except:
            print("Could not enable console, debug output will go to terminal")
    
    root = tk.Tk()
    app = GitHubAssistant(root)
    root.mainloop()

if __name__ == "__main__":
    main()
