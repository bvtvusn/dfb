import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import uuid
import base64
from pathlib import Path
from datetime import datetime

class DFBConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DFB V1 Converter")
        self.root.geometry("800x600")
        
        # Generate a unique separator for this session
        self.separator = f"----DFB-SEP::{uuid.uuid4()}----"
        
        # Working directory
        self.working_dir = os.path.expanduser("~")
        
        # Supported text file extensions
        self.text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', 
                               '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log', '.csv'}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Working directory section
        dir_frame = ttk.LabelFrame(main_frame, text="Working Directory", padding="5")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Path:").pack(side=tk.LEFT)
        self.dir_label = ttk.Label(dir_frame, text=self.working_dir, relief=tk.SUNKEN, padding=(5, 2))
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(dir_frame, text="Select", command=self.select_directory).pack(side=tk.RIGHT)
        
        # Control buttons
        btn_frame = ttk.LabelFrame(main_frame, text="Operations", padding="5")
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Extract from DFB", command=self.extract_from_dfb).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Create from Directory", command=self.create_from_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Create from File", command=self.create_from_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Save DFB", command=self.save_dfb).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT)
        
        # Text area
        text_frame = ttk.LabelFrame(main_frame, text="DFB Content", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_area = scrolledtext.ScrolledText(text_frame, font=("Consolas", 9))
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Log window
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 8))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, padding=(5, 2))
        status_bar.pack(fill=tk.X)
        
        self.log("Application started")
        
    def log(self, message):
        """Add message to log window"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_area.insert(tk.END, log_entry)
        self.log_area.see(tk.END)
        self.root.update_idletasks()
        
    def select_directory(self):
        """Select working directory"""
        new_dir = filedialog.askdirectory(title="Select working directory", initialdir=self.working_dir)
        if new_dir:
            self.working_dir = new_dir
            self.dir_label.config(text=self.working_dir)
            self.log(f"Working directory changed to: {self.working_dir}")
            
    def extract_from_dfb(self):
        """Extract files from DFB data"""
        dfb_data = self.text_area.get("1.0", tk.END)
        if not dfb_data.strip():
            messagebox.showwarning("Warning", "No DFB data to extract")
            return
            
        if not self.validate_dfb_format(dfb_data):
            messagebox.showerror("Error", "Invalid DFB format")
            return
            
        try:
            self.log("Starting extraction...")
            extracted_files = self.parse_and_extract_dfb(dfb_data, self.working_dir)
            self.log(f"Extraction complete. Extracted {len(extracted_files)} files")
            self.status_var.set(f"Extracted {len(extracted_files)} files")
            messagebox.showinfo("Success", f"Files extracted to: {self.working_dir}")
        except Exception as e:
            self.log(f"Extraction error: {str(e)}")
            messagebox.showerror("Error", f"Extraction failed: {str(e)}")
            
    def create_from_directory(self):
        """Create DFB from directory"""
        if not os.path.exists(self.working_dir):
            messagebox.showerror("Error", "Working directory does not exist")
            return
            
        try:
            self.log("Creating DFB from directory...")
            dfb_content = self.create_dfb_from_directory(self.working_dir)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", dfb_content)
            self.log("DFB creation complete")
            self.status_var.set("DFB created from directory")
        except Exception as e:
            self.log(f"Creation error: {str(e)}")
            messagebox.showerror("Error", f"Creation failed: {str(e)}")
            
    def create_from_file(self):
        """Create DFB from single file"""
        input_file = filedialog.askopenfilename(title="Select file", initialdir=self.working_dir)
        if not input_file:
            return
            
        try:
            self.log(f"Creating DFB from file: {os.path.basename(input_file)}")
            dfb_content = self.create_dfb_from_file(input_file)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", dfb_content)
            self.log("DFB creation complete")
            self.status_var.set("DFB created from file")
        except Exception as e:
            self.log(f"Creation error: {str(e)}")
            messagebox.showerror("Error", f"Creation failed: {str(e)}")
            
    def save_dfb(self):
        """Save DFB content to file"""
        content = self.text_area.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Warning", "No content to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save DFB file",
            defaultextension=".dfb",
            filetypes=[("DFB files", "*.dfb"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.working_dir
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"DFB saved to: {file_path}")
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"DFB file saved to:\n{file_path}")
            except Exception as e:
                self.log(f"Save error: {str(e)}")
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                
    def clear_text(self):
        """Clear text area"""
        self.text_area.delete("1.0", tk.END)
        self.log("Text area cleared")
        self.status_var.set("Ready")
        
    def validate_dfb_format(self, dfb_data):
        """Validate basic DFB format"""
        lines = dfb_data.split('\n')
        if not lines or lines[0].strip() != "DFB V1":
            return False
            
        # Check for separator
        for line in lines[1:]:
            if line.startswith("SEPARATOR:"):
                return True
            if not line.strip():
                break
        return False
        
    def parse_and_extract_dfb(self, dfb_data, output_dir):
        """Parse DFB and extract files"""
        lines = dfb_data.split('\n')
        extracted_files = []
        
        self.log(f"Parsing DFB with {len(lines)} lines")
        
        # Check header
        if not lines[0].strip() == "DFB V1":
            raise ValueError("Invalid DFB header")
            
        # Parse control block
        separator = None
        i = 1
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith("SEPARATOR:"):
                separator = lines[i][10:].strip()
                break
            i += 1
            
        if not separator:
            raise ValueError("No separator found")
            
        self.log(f"Found separator: {separator[:20]}...")
        
        # Skip to end of control block
        while i < len(lines) and lines[i].strip():
            i += 1
        i += 1
        
        self.log(f"Starting to parse entries from line {i}")
        
        # Parse entries
        current_metadata = {}
        current_content = []
        in_metadata = True
        
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == separator:
                # Save previous entry
                if current_metadata:
                    filename = self.save_extracted_file(current_metadata, current_content, output_dir)
                    if filename:
                        extracted_files.append(filename)
                        self.log(f"Extracted: {filename}")
                
                # Start new entry
                current_metadata = {}
                current_content = []
                in_metadata = True
                self.log(f"Found separator at line {i}, starting new entry")
                i += 1
                continue
                
            # Process metadata and content for current entry
            if in_metadata:
                if not line.strip():
                    in_metadata = False
                    self.log(f"Metadata complete, content starts at line {i+1}")
                else:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        current_metadata[key.strip()] = value.strip()
                        self.log(f"Added metadata: {key.strip()}")
            else:
                current_content.append(line)
                    
            i += 1
            
        # Save last entry
        if current_metadata:
            self.log(f"Processing final entry with metadata: {list(current_metadata.keys())}")
            filename = self.save_extracted_file(current_metadata, current_content, output_dir)
            if filename:
                extracted_files.append(filename)
                self.log(f"Extracted: {filename}")
            else:
                self.log(f"Failed to extract final entry")
        else:
            self.log("No final entry to process")
                
        self.log(f"Total entries processed, extracted {len(extracted_files)} files")
        return extracted_files
        
    def save_extracted_file(self, metadata, content_lines, output_dir):
        """Save extracted file"""
        if 'FILENAME' not in metadata:
            self.log(f"No FILENAME in metadata: {list(metadata.keys())}")
            return None
            
        filename = metadata['FILENAME']
        self.log(f"Attempting to save file: {filename}")
        
        # Security check
        if '..' in filename or ':' in filename:
            self.log(f"Skipping unsafe filename: {filename}")
            return None
            
        try:
            output_path = os.path.join(output_dir, filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            encoding = metadata.get('ENCODING', 'utf-8').lower()
            self.log(f"File encoding: {encoding}, content lines: {len(content_lines)}")
            
            if encoding == 'base64':
                base64_content = ''.join(content_lines).replace('\n', '').replace('\r', '').replace(' ', '')
                binary_data = base64.b64decode(base64_content)
                with open(output_path, 'wb') as f:
                    f.write(binary_data)
                self.log(f"Saved binary file: {filename} ({len(binary_data)} bytes)")
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content_lines))
                self.log(f"Saved text file: {filename} ({len(content_lines)} lines)")
                    
            return filename
            
        except Exception as e:
            self.log(f"Failed to extract {filename}: {str(e)}")
            return None
            
    def create_dfb_from_directory(self, input_dir):
        """Create DFB from directory"""
        dfb_lines = ["DFB V1"]
        dfb_lines.append(f"SEPARATOR: {self.separator}")
        dfb_lines.append("")
        
        input_path = Path(input_dir)
        processed_files = 0
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                try:
                    # Try text first, fall back to binary
                    if file_path.suffix.lower() in self.text_extensions:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            encoding = 'utf-8'
                        except UnicodeDecodeError:
                            with open(file_path, 'rb') as f:
                                content_bytes = f.read()
                            content = base64.b64encode(content_bytes).decode('ascii')
                            encoding = 'base64'
                    else:
                        with open(file_path, 'rb') as f:
                            content_bytes = f.read()
                        content = base64.b64encode(content_bytes).decode('ascii')
                        encoding = 'base64'
                        
                    rel_path = file_path.relative_to(input_path)
                    rel_path_str = str(rel_path).replace('\\', '/')
                    
                    dfb_lines.append(self.separator)
                    dfb_lines.append(f"FILENAME: {rel_path_str}")
                    dfb_lines.append(f"ENCODING: {encoding}")
                    dfb_lines.append(f"SIZE: {file_path.stat().st_size}")
                    dfb_lines.append("")
                    dfb_lines.append(content)
                    
                    processed_files += 1
                    self.log(f"Added: {rel_path_str}")
                    
                except Exception as e:
                    self.log(f"Skipping {file_path}: {str(e)}")
                    continue
                    
        return '\n'.join(dfb_lines)
        
    def create_dfb_from_file(self, input_file):
        """Create DFB from single file"""
        dfb_lines = ["DFB V1"]
        dfb_lines.append(f"SEPARATOR: {self.separator}")
        dfb_lines.append("")
        
        filename = os.path.basename(input_file)
        file_path = Path(input_file)
        
        try:
            if file_path.suffix.lower() in self.text_extensions:
                try:
                    with open(input_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    with open(input_file, 'rb') as f:
                        content_bytes = f.read()
                    content = base64.b64encode(content_bytes).decode('ascii')
                    encoding = 'base64'
            else:
                with open(input_file, 'rb') as f:
                    content_bytes = f.read()
                content = base64.b64encode(content_bytes).decode('ascii')
                encoding = 'base64'
                
            dfb_lines.append(self.separator)
            dfb_lines.append(f"FILENAME: {filename}")
            dfb_lines.append(f"ENCODING: {encoding}")
            dfb_lines.append(f"SIZE: {file_path.stat().st_size}")
            dfb_lines.append("")
            dfb_lines.append(content)
            
        except Exception as e:
            raise ValueError(f"Cannot read file: {str(e)}")
            
        return '\n'.join(dfb_lines)

def main():
    root = tk.Tk()
    app = DFBConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
