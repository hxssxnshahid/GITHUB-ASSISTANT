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
        
        # Check if this is first time setup
        self.is_first_time = not self.config.get('token') or not self.config.get('setup_complete', False)
        
        self.setup_ui()
        
        # Show first-time setup if needed
        if self.is_first_time:
            self.show_first_time_setup()
        
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
    
    def check_git_available(self):
        """Check if Git is available on the system"""
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_large_files(self, project_path):
        """Check for files larger than 100MB and warn user"""
        large_files = []
        total_size = 0
        
        for root, dirs, files in os.walk(project_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    # Check for files larger than 100MB
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        large_files.append((file_path, file_size))
                except (OSError, IOError):
                    continue
        
        return large_files, total_size
    
    def setup_git_lfs(self, project_path):
        """Setup Git LFS for large files"""
        try:
            # Check if Git LFS is available
            subprocess.run(['git', 'lfs', 'version'], check=True, capture_output=True, text=True)
            
            # Initialize Git LFS
            subprocess.run(['git', 'lfs', 'install'], cwd=project_path, check=True, capture_output=True, text=True)
            
            # Track common large file types
            large_file_patterns = [
                '*.zip', '*.rar', '*.7z', '*.tar', '*.gz',
                '*.exe', '*.msi', '*.dmg', '*.pkg',
                '*.mp4', '*.avi', '*.mov', '*.mkv',
                '*.iso', '*.img', '*.bin',
                '*.dll', '*.so', '*.dylib',
                '*.db', '*.sqlite', '*.sqlite3'
            ]
            
            for pattern in large_file_patterns:
                try:
                    subprocess.run(['git', 'lfs', 'track', pattern], cwd=project_path, check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    pass  # Pattern might already be tracked
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        
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
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"[DEBUG] Config file error: {e}")
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
        
        # Basic token validation
        if not token.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            messagebox.showerror("Error", "Invalid token format. GitHub tokens should start with 'ghp_', 'gho_', 'ghu_', 'ghs_', or 'ghr_'")
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
        
        if not self.check_git_available():
            messagebox.showerror("Error", "Git is not installed or not in PATH. Please install Git from https://git-scm.com/")
            return
        
        # Check if already processing
        if hasattr(self, '_upload_in_progress') and self._upload_in_progress:
            self.log_message("⚠️ Upload already in progress, please wait...")
            return
        
        # Set processing state
        self._upload_in_progress = True
        self.set_status("Checking project files...")
        
        # Run file checking in background thread
        def check_files_thread():
            try:
                # Check for large files
                project_path = self.project_var.get()
                large_files, total_size = self.check_large_files(project_path)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.handle_file_check_result(project_path, large_files, total_size))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_file_check_error(str(e)))
        
        # Start background thread
        thread = threading.Thread(target=check_files_thread, daemon=True)
        thread.start()
    
    def handle_file_check_result(self, project_path, large_files, total_size):
        """Handle file check results in main thread"""
        try:
            if large_files:
                # Show warning about large files
                large_file_list = "\n".join([f"- {os.path.basename(f[0])} ({f[1] // (1024*1024)}MB)" for f in large_files[:5]])
                if len(large_files) > 5:
                    large_file_list += f"\n- ... and {len(large_files) - 5} more files"
                
                total_mb = total_size // (1024*1024)
                warning_msg = f"⚠️ LARGE FILES DETECTED ⚠️\n\n" \
                             f"Total project size: {total_mb}MB\n" \
                             f"Large files (>100MB):\n{large_file_list}\n\n" \
                             f"GitHub has a 100MB file limit. Large files will be handled with Git LFS.\n\n" \
                             f"Make sure Git LFS is installed: https://git-lfs.github.io/\n" \
                             f"Continue with upload?"
                
                if not messagebox.askyesno("Large Files Detected", warning_msg):
                    self._upload_in_progress = False
                    self.set_status("Ready")
                    return
            
            # Create dialog for upload details
            dialog = UploadDialog(self.root, self.github, project_path, self.log_message, self.set_status)
            self.root.wait_window(dialog.dialog)
            
        finally:
            self._upload_in_progress = False
            self.set_status("Ready")
    
    def handle_file_check_error(self, error_msg):
        """Handle file check errors in main thread"""
        self.log_message(f"❌ Error checking files: {error_msg}")
        self._upload_in_progress = False
        self.set_status("Ready")
    
    def show_first_time_setup(self):
        """Show first-time setup wizard"""
        setup_dialog = FirstTimeSetupDialog(self.root, self.log_message, self.set_status)
        self.root.wait_window(setup_dialog.dialog)
        
        # Mark setup as complete
        self.config['setup_complete'] = True
        self.save_config()
        
    def update_repo(self):
        """Update existing repository"""
        if not self.github:
            messagebox.showerror("Error", "Please connect to GitHub first")
            return
            
        if not self.project_var.get():
            messagebox.showerror("Error", "Please select a project folder")
            return
        
        if not self.check_git_available():
            messagebox.showerror("Error", "Git is not installed or not in PATH. Please install Git from https://git-scm.com/")
            return
            
        # Create dialog for update details
        dialog = UpdateDialog(self.root, self.github, self.project_var.get(), self.log_message, self.set_status)
        self.root.wait_window(dialog.dialog)
        
    def clone_repo(self):
        """Clone a repository"""
        if not self.check_git_available():
            messagebox.showerror("Error", "Git is not installed or not in PATH. Please install Git from https://git-scm.com/")
            return
        
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
        
        # Validate repository name
        if not name.replace('-', '').replace('_', '').replace('.', '').isalnum():
            messagebox.showerror("Error", "Repository name can only contain letters, numbers, hyphens, underscores, and dots")
            return
        
        if len(name) > 100:
            messagebox.showerror("Error", "Repository name must be 100 characters or less")
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
        
        self.upload_btn = ttk.Button(button_frame, text="Upload Project", command=self.upload_project)
        self.upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="Ready to upload")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var, font=('Arial', 9))
        self.progress_label.grid(row=7, column=0, pady=(10, 0))
        
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
    
    def setup_git_lfs(self, project_path):
        """Setup Git LFS for large files"""
        try:
            # Check if Git LFS is available
            subprocess.run(['git', 'lfs', 'version'], check=True, capture_output=True, text=True)
            
            # Initialize Git LFS
            subprocess.run(['git', 'lfs', 'install'], cwd=project_path, check=True, capture_output=True, text=True)
            
            # Track common large file types
            large_file_patterns = [
                '*.zip', '*.rar', '*.7z', '*.tar', '*.gz',
                '*.exe', '*.msi', '*.dmg', '*.pkg',
                '*.mp4', '*.avi', '*.mov', '*.mkv',
                '*.iso', '*.img', '*.bin',
                '*.dll', '*.so', '*.dylib',
                '*.db', '*.sqlite', '*.sqlite3'
            ]
            
            for pattern in large_file_patterns:
                try:
                    subprocess.run(['git', 'lfs', 'track', pattern], cwd=project_path, check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    pass  # Pattern might already be tracked
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def upload_project(self):
        repo_name = self.repo_var.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Please select a repository")
            return
        
        # Check if already uploading
        if hasattr(self, '_uploading') and self._uploading:
            self.log_callback("⚠️ Upload already in progress, please wait...")
            return
        
        # Disable button and show loading
        self._uploading = True
        self.upload_btn.config(state='disabled', text="Uploading...")
        self.progress_var.set("Starting upload...")
        self.dialog.update()
        
        # Run upload in background thread
        def upload_thread():
            try:
                repo = self.github.get_user().get_repo(repo_name)
                commit_msg = self.commit_var.get().strip() or "Update project"
                branch = self.branch_var.get().strip() or "main"
                
                self.log_callback(f"📤 Uploading project to {repo_name}...")
                self.dialog.after(0, lambda: self.progress_var.set("Preparing upload..."))
                
                # Get the project path from the main app
                project_path = self.project_path
                
                # Check if it's already a git repository
                if os.path.exists(os.path.join(project_path, '.git')):
                    self.log_callback("📁 Project is already a git repository, pushing changes...")
                    self.dialog.after(0, lambda: self.progress_var.set("Pushing to existing repository..."))
                    self.push_existing_repo(project_path, repo, commit_msg, branch)
                else:
                    self.log_callback("📁 Initializing new git repository and uploading...")
                    self.dialog.after(0, lambda: self.progress_var.set("Initializing new repository..."))
                    self.upload_new_repo(project_path, repo, commit_msg, branch)
                
                # Success - update UI in main thread
                self.dialog.after(0, lambda: self.upload_success())
                
            except GithubException as e:
                error_msg = f"Failed to upload project: {str(e)}"
                self.log_callback(f"❌ {error_msg}")
                self.dialog.after(0, lambda: self.upload_error(error_msg))
            except Exception as e:
                error_msg = f"Upload failed: {str(e)}"
                self.log_callback(f"❌ {error_msg}")
                self.dialog.after(0, lambda: self.upload_error(error_msg))
        
        # Start background thread
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
    
    def upload_success(self):
        """Handle successful upload"""
        self._uploading = False
        self.upload_btn.config(state='normal', text="Upload Project")
        self.progress_var.set("Upload completed successfully!")
        self.dialog.after(2000, self.dialog.destroy)  # Close dialog after 2 seconds
    
    def upload_error(self, error_msg):
        """Handle upload error"""
        self._uploading = False
        self.upload_btn.config(state='normal', text="Upload Project")
        self.progress_var.set("Upload failed")
        messagebox.showerror("Error", error_msg)
    
    def push_existing_repo(self, project_path, repo, commit_msg, branch):
        """Push changes to existing git repository"""
        try:
            # Ensure remote 'origin' exists and points to the selected repo
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            current_remote_url = (result.stdout or '').strip()
            desired_remote_url = repo.clone_url

            if result.returncode != 0:
                # No origin → add it
                subprocess.run(
                    ['git', 'remote', 'add', 'origin', desired_remote_url],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.log_callback(f"🔗 Added remote origin → {desired_remote_url}")
            else:
                # Origin exists → retarget if pointing to a different repo
                if current_remote_url.rstrip('/') != desired_remote_url.rstrip('/'):
                    self.log_callback(f"🔁 Updating remote origin: {current_remote_url} → {desired_remote_url}")
                    subprocess.run(
                        ['git', 'remote', 'set-url', 'origin', desired_remote_url],
                        cwd=project_path,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                else:
                    self.log_callback(f"🔗 Remote origin already set to {current_remote_url}")

            # Add all files
            self.dialog.after(0, lambda: self.progress_var.set("Adding files to staging..."))
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True, text=True)
            self.log_callback("📝 Added files to staging")

            # Check if there are staged changes
            diff_result = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            has_changes = diff_result.returncode != 0
            
            if has_changes:
                # There are staged changes → commit
                self.dialog.after(0, lambda: self.progress_var.set("Committing changes..."))
                subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.log_callback("💾 Committed changes")
            else:
                self.log_callback("ℹ️ No changes to commit")

            # Determine current branch if branch not provided
            if not branch:
                branch_out = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                branch = branch_out.stdout.strip() or 'main'

            # Check if this will be the first push to this remote branch
            ls_remote = subprocess.run(
                ['git', 'ls-remote', '--heads', 'origin', branch],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            is_first_push = (ls_remote.returncode != 0) or (ls_remote.stdout.strip() == '')

            # Push to GitHub with progress indication
            self.log_callback(f"🚀 Pushing to {branch} branch... (this may take a while for large files)")
            self.dialog.after(0, lambda: self.progress_var.set(f"Pushing to {branch} branch... (this may take a while)"))
            try:
                subprocess.run(
                    ['git', 'push', '-u', 'origin', branch],
                    cwd=project_path,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout for large uploads
                )
                self.log_callback(f"🚀 Pushed to {branch} branch")
            except subprocess.TimeoutExpired:
                self.log_callback("⏰ Upload timed out - this may happen with very large files")
                self.log_callback("💡 Try uploading smaller chunks or use Git command line")
                raise

            if has_changes or is_first_push:
                self.log_callback(f"✅ Project uploaded successfully to {repo.html_url}")
                messagebox.showinfo("Success", f"Project uploaded to {repo.name} successfully!")
            else:
                self.log_callback(f"ℹ️ Project is already up to date on GitHub")
                messagebox.showinfo("Info", f"Project is already up to date on GitHub.\nNo changes were made to {repo.name}.")
            
            self.dialog.destroy()

        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            stdout = (e.stdout or '').strip()
            combined = stderr if stderr else stdout if stdout else str(e)
            
            # Provide more helpful error messages
            if "not a git repository" in combined.lower():
                error_msg = "This folder is not a Git repository. Please use 'Upload Project' instead."
            elif "authentication failed" in combined.lower():
                error_msg = "Git authentication failed. Please check your Git credentials."
            elif "remote origin already exists" in combined.lower():
                error_msg = "Remote origin already exists. The operation will continue with the existing remote."
                self.log_callback(f"⚠️ {error_msg}")
                return  # This is not actually an error
            else:
                error_msg = f"Git command failed: {combined}"
            
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH. Please install Git from https://git-scm.com/"
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def upload_new_repo(self, project_path, repo, commit_msg, branch):
        """Initialize new git repository and upload"""
        try:
            # Initialize git repository
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
            self.log_callback("🆕 Initialized git repository")
            
            # Setup Git LFS for large files
            if self.setup_git_lfs(project_path):
                self.log_callback("📦 Git LFS initialized for large files")
            else:
                self.log_callback("⚠️ Git LFS not available - large files may cause issues")
                self.log_callback("💡 Install Git LFS from: https://git-lfs.github.io/")
            
            # Configure Git for large files
            try:
                subprocess.run(['git', 'config', 'http.postBuffer', '524288000'], cwd=project_path, check=True)  # 500MB
                subprocess.run(['git', 'config', 'http.maxRequestBuffer', '524288000'], cwd=project_path, check=True)  # 500MB
                self.log_callback("⚙️ Git configured for large file uploads")
            except subprocess.CalledProcessError:
                self.log_callback("⚠️ Could not configure Git for large files")
            
            # Add remote
            subprocess.run(['git', 'remote', 'add', 'origin', repo.clone_url], 
                         cwd=project_path, check=True)
            self.log_callback("🔗 Added remote origin")
            
            # Create .gitignore if it doesn't exist
            gitignore_path = os.path.join(project_path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w') as f:
                    f.write("# GitHub Assistant Configuration\ngithub_config.json\n\n# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n# IDE\n.vscode/\n.idea/\n\n# OS\n.DS_Store\nThumbs.db\n")
                self.log_callback("📝 Created .gitignore file")
            
            # Remove config file from staging if it exists
            config_file = os.path.join(project_path, 'github_config.json')
            if os.path.exists(config_file):
                try:
                    subprocess.run(['git', 'rm', '--cached', 'github_config.json'], 
                                 cwd=project_path, check=True)
                    self.log_callback("🔒 Removed config file from staging (contains sensitive data)")
                except subprocess.CalledProcessError:
                    pass  # File might not be staged yet
            
            # Add all files except config
            self.dialog.after(0, lambda: self.progress_var.set("Adding files to staging..."))
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            subprocess.run(['git', 'reset', 'github_config.json'], cwd=project_path, check=True)
            self.log_callback("📝 Added files to staging (excluding config)")
            
            # Commit changes
            self.dialog.after(0, lambda: self.progress_var.set("Committing changes..."))
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=project_path, check=True)
            self.log_callback("💾 Committed changes")
            
            # Rename branch to main if needed
            try:
                subprocess.run(['git', 'branch', '-M', branch], cwd=project_path, check=True)
                self.log_callback(f"🏷️ Renamed branch to {branch}")
            except subprocess.CalledProcessError:
                pass  # Branch might already be main
            
            # Push to GitHub with progress indication
            self.log_callback(f"🚀 Pushing to {branch} branch... (this may take a while for large files)")
            self.dialog.after(0, lambda: self.progress_var.set(f"Pushing to {branch} branch... (this may take a while)"))
            try:
                # Use git push with progress for large files
                result = subprocess.run(
                    ['git', 'push', '-u', 'origin', branch], 
                    cwd=project_path, 
                    check=True, 
                    capture_output=True, 
                    text=True,
                    timeout=3600  # 1 hour timeout for large uploads
                )
                self.log_callback(f"🚀 Pushed to {branch} branch")
            except subprocess.TimeoutExpired:
                self.log_callback("⏰ Upload timed out - this may happen with very large files")
                self.log_callback("💡 Try uploading smaller chunks or use Git command line")
                raise
            
            self.log_callback(f"✅ Project uploaded successfully to {repo.html_url}")
            messagebox.showinfo("Success", f"Project uploaded to {repo.name} successfully!")
            self.dialog.destroy()
            
        except subprocess.CalledProcessError as e:
            stderr = (e.stderr or '').strip()
            stdout = (e.stdout or '').strip()
            combined = stderr if stderr else stdout if stdout else str(e)
            
            # Provide more helpful error messages
            if "authentication failed" in combined.lower():
                error_msg = "Git authentication failed. Please check your Git credentials."
            elif "repository not found" in combined.lower():
                error_msg = "Repository not found. Please check the repository name and permissions."
            else:
                error_msg = f"Git command failed: {combined}"
            
            self.log_callback(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH. Please install Git from https://git-scm.com/"
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
                
                # Determine current branch
                branch_out = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                current_branch = branch_out.stdout.strip() or 'main'

                # Push to GitHub
                subprocess.run(['git', 'push', 'origin', current_branch], cwd=self.project_path, check=True, capture_output=True, text=True)
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
        
        # Basic URL validation
        if not (url.startswith('https://github.com/') or url.startswith('git@github.com:')):
            messagebox.showerror("Error", "Please enter a valid GitHub repository URL (https://github.com/username/repo or git@github.com:username/repo.git)")
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
        except (GithubException, UnicodeDecodeError, AttributeError):
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
        except (OSError, IOError, AttributeError):
            print("Could not enable console, debug output will go to terminal")
    
    root = tk.Tk()
    app = GitHubAssistant(root)
    root.mainloop()

class FirstTimeSetupDialog:
    def __init__(self, parent, log_callback, status_callback):
        self.log_callback = log_callback
        self.status_callback = status_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🚀 Welcome to GitHub Assistant!")
        self.dialog.geometry("700x650")
        try:
            self.dialog.minsize(650, 600)
        except Exception:
            pass
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Welcome message
        welcome_label = ttk.Label(main_frame, text="🚀 Welcome to GitHub Assistant!", 
                                 font=('Arial', 16, 'bold'))
        welcome_label.pack(pady=(0, 20))
        
        # Single instructions panel
        instructions_frame = ttk.LabelFrame(main_frame, text="Get a GitHub Token", padding="15")
        instructions_frame.pack(fill=tk.X, pady=(0, 20))
        
        instructions_text = """To upload projects to GitHub, you need a Personal Access Token.

1. Click the button below to open GitHub
2. Click "Generate new token (classic)"
3. Name it (e.g., "GitHub Assistant")
4. Select scopes: repo, public_repo (and delete_repo if needed)
5. Click "Generate token" and copy it

Paste the token later in the main window's GitHub Authentication section."""
        ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Button(instructions_frame, text="Open GitHub Token Page", 
                  command=self.open_token_page).pack(pady=(10, 0))
        
        # Footer buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="Next", 
                  command=self.skip_setup).pack(side=tk.RIGHT)
    
    def open_token_page(self):
        """Open GitHub token creation page"""
        webbrowser.open("https://github.com/settings/tokens/new")
        self.log_callback("🌐 Opened GitHub token creation page")
    
    def test_connection(self):
        """Test GitHub connection"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a GitHub token first")
            return
        
        # Basic token validation
        if not token.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            messagebox.showerror("Error", "Invalid token format. GitHub tokens should start with 'ghp_', 'gho_', 'ghu_', 'ghs_', or 'ghr_'")
            return
        
        # Disable button and show testing
        self.test_btn.config(state='disabled', text="Testing...")
        self.status_var.set("Testing connection...")
        self.dialog.update()
        
        # Track progress and add a watchdog to avoid indefinite hangs
        self._test_in_progress = True

        # Test in background thread with timeout
        def test_thread():
            try:
                from github import Github
                # Use a network timeout so calls don't hang forever
                github = Github(token, timeout=10)
                user = github.get_user()
                # Update UI in main thread
                self.dialog.after(0, lambda: self.connection_success(user.login))
            except Exception as e:
                self.dialog.after(0, lambda: self.connection_error(str(e)))

        thread = threading.Thread(target=test_thread, daemon=True)
        thread.start()

        # Watchdog: if still in progress after 15s, report timeout
        def watchdog_fire():
            if getattr(self, '_test_in_progress', False):
                self.connection_error("Connection timed out. Check internet or proxy settings and try again.")

        try:
            self._watchdog_timer = threading.Timer(15.0, lambda: self.dialog.after(0, watchdog_fire))
            self._watchdog_timer.daemon = True
            self._watchdog_timer.start()
        except Exception:
            pass
    
    def connection_success(self, username):
        """Handle successful connection"""
        # Stop watchdog and mark complete
        try:
            if hasattr(self, '_watchdog_timer'):
                self._watchdog_timer.cancel()
        except Exception:
            pass
        self._test_in_progress = False
        self.test_btn.config(state='normal', text="🔗 Test Connection")
        self.status_var.set(f"✅ Connected as {username}")
        self.finish_btn.config(state='normal')
        self.log_callback(f"✅ Connection successful: {username}")
    
    def connection_error(self, error_msg):
        """Handle connection error"""
        # Stop watchdog and mark complete
        try:
            if hasattr(self, '_watchdog_timer'):
                self._watchdog_timer.cancel()
        except Exception:
            pass
        self._test_in_progress = False
        self.test_btn.config(state='normal', text="🔗 Test Connection")
        self.status_var.set("❌ Connection failed")
        messagebox.showerror("Connection Error", f"Failed to connect to GitHub:\n{error_msg}")
        self.log_callback(f"❌ Connection failed: {error_msg}")
    
    def finish_setup(self):
        """Finish setup and save token"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a GitHub token first")
            return
        
        # Save token to config
        config = {}
        if os.path.exists("github_config.json"):
            try:
                with open("github_config.json", 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        
        config['token'] = token
        config['setup_complete'] = True
        
        with open("github_config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_callback("✅ Setup completed successfully!")
        self.dialog.destroy()
    
    def skip_setup(self):
        """Skip setup for now"""
        self.log_callback("Proceeding to the main window. You can enter your token here.")
        self.dialog.destroy()

if __name__ == "__main__":
    main()
