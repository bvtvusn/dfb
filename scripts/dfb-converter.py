import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import uuid
import base64
from pathlib import Path

class MTXTConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DFB V1 Converter")
        self.root.geometry("900x700")
        
        # Generate a unique separator for this session
        self.separator = f"----DFB-SEP::{uuid.uuid4()}----"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DFB V1 Converter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Extract button
        extract_btn = ttk.Button(button_frame, text="Extract from DFB", command=self.extract_from_mtxt)
        extract_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create from directory button
        create_dir_btn = ttk.Button(button_frame, text="Create DFB from Directory", command=self.create_mtxt_from_directory)
        create_dir_btn.pack(side=tk.LEFT, padx=5)
        
        # Create from single file button
        create_file_btn = ttk.Button(button_frame, text="Create DFB from File", command=self.create_mtxt_from_file)
        create_file_btn.pack(side=tk.LEFT, padx=5)
        
        # Clipboard buttons
        copy_btn = ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        paste_btn = ttk.Button(button_frame, text="Paste from Clipboard", command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.RIGHT)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_area = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 9))
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_area.xview)
        
        self.text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - DFB V1 format")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def extract_from_mtxt(self):
        """Extract files from DFB data in the text area"""
        mtxt_data = self.text_area.get("1.0", tk.END)
        if not mtxt_data.strip():
            messagebox.showwarning("Warning", "No DFB data to extract")
            return
            
        # Select output directory
        output_dir = filedialog.askdirectory(title="Select output directory")
        if not output_dir:
            return
            
        try:
            self.parse_and_extract_mtxt_text(mtxt_data, output_dir)
            self.status_var.set(f"Files extracted to: {output_dir}")
            messagebox.showinfo("Success", f"Files extracted successfully to:\n{output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract files: {str(e)}")
            self.status_var.set("Extraction failed")
            
    def create_mtxt_from_directory(self):
        """Create DFB from all files in a selected directory"""
        input_dir = filedialog.askdirectory(title="Select directory with files to archive")
        if not input_dir:
            return
            
        try:
            mtxt_content = self.create_mtxt_from_directory_text(input_dir)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", mtxt_content)
            self.status_var.set(f"DFB created from: {input_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create DFB: {str(e)}")
            self.status_var.set("DFB creation failed")
            
    def create_mtxt_from_file(self):
        """Create DFB from a single selected file"""
        input_file = filedialog.askopenfilename(title="Select file to archive")
        if not input_file:
            return
            
        try:
            mtxt_content = self.create_mtxt_from_single_file_text(input_file)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", mtxt_content)
            self.status_var.set(f"DFB created from: {input_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create DFB: {str(e)}")
            self.status_var.set("DFB creation failed")
            
    def copy_to_clipboard(self):
        """Copy text area content to clipboard"""
        content = self.text_area.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set("Content copied to clipboard")
        
    def paste_from_clipboard(self):
        """Paste clipboard content to text area"""
        try:
            content = self.root.clipboard_get()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.status_var.set("Content pasted from clipboard")
        except tk.TclError:
            messagebox.showwarning("Warning", "No content in clipboard")
            
    def parse_and_extract_mtxt_text(self, mtxt_data, output_dir):
        """Parse DFB data and extract text files"""
        lines = mtxt_data.split('\n')
        
        # Check header
        if not lines[0].strip() == "DFB V1":
            raise ValueError("Invalid DFB header - expected 'DFB V1'")
            
        # Parse control block
        separator = None
        i = 1
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith("SEPARATOR:"):
                separator = lines[i][10:].strip()  # Remove "SEPARATOR:" prefix
                break
            i += 1
            
        if not separator:
            raise ValueError("No separator found in control block")
            
        # Skip to end of control block
        while i < len(lines) and lines[i].strip():
            i += 1
        i += 1  # Skip blank line
        
        # Parse entries
        current_entry = None
        current_metadata = {}
        current_content = []
        in_metadata = True
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a separator line
            if line.strip() == separator:
                # Save previous entry if exists
                if current_entry and current_metadata:
                    self.save_extracted_text_file(current_metadata, current_content, output_dir)
                
                # Start new entry
                current_entry = i
                current_metadata = {}
                current_content = []
                in_metadata = True
                i += 1
                continue
                
            if current_entry is not None:
                if in_metadata:
                    if not line.strip():  # Blank line ends metadata
                        in_metadata = False
                    else:
                        # Parse metadata line
                        if ':' in line:
                            key, value = line.split(':', 1)
                            current_metadata[key.strip()] = value.strip()
                else:
                    current_content.append(line)
                    
            i += 1
            
        # Save last entry
        if current_entry and current_metadata:
            self.save_extracted_text_file(current_metadata, current_content, output_dir)
            
    def save_extracted_text_file(self, metadata, content_lines, output_dir):
        """Save extracted file content (text or binary)"""
        if 'FILENAME' not in metadata:
            raise ValueError("Missing FILENAME in metadata")
            
        filename = metadata['FILENAME']
        
        # Security check - prevent path traversal
        if filename.startswith('/') or '..' in filename or ':' in filename:
            raise ValueError(f"Invalid filename: {filename}")
            
        # Create output path
        output_path = os.path.join(output_dir, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check encoding type
        encoding = metadata.get('ENCODING', 'utf-8').lower()
        
        if encoding == 'base64':
            # Extract binary data from base64
            try:
                # Join all content lines and remove whitespace
                base64_content = ''.join(content_lines).replace('\n', '').replace('\r', '').replace(' ', '')
                binary_data = base64.b64decode(base64_content)
                with open(output_path, 'wb') as f:
                    f.write(binary_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 data format: {str(e)}")
        else:
            # Write text content as UTF-8
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            
    def create_mtxt_from_directory_text(self, input_dir):
        """Create DFB content from directory (all files)"""
        mtxt_lines = ["DFB V1"]
        mtxt_lines.append(f"SEPARATOR: {self.separator}")
        mtxt_lines.append("")  # Blank line ends control block
        
        input_path = Path(input_dir)
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                # Try to read as text file, but don't skip on failure
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Calculate relative path
                    rel_path = file_path.relative_to(input_path)
                    rel_path_str = str(rel_path).replace('\\', '/')  # POSIX style
                    
                    # Add separator
                    mtxt_lines.append(self.separator)
                    
                    # Add metadata
                    mtxt_lines.append(f"FILENAME: {rel_path_str}")
                    mtxt_lines.append("ENCODING: utf-8")
                    # Try to guess MIME type from extension
                    mime_type = self.guess_mime_type(rel_path_str)
                    if mime_type:
                        mtxt_lines.append(f"MIME: {mime_type}")
                    mtxt_lines.append("")  # Blank line ends metadata
                    
                    # Add file content
                    mtxt_lines.append(content)
                    
                except UnicodeDecodeError:
                    # Try to read as binary and convert to base64
                    try:
                        with open(file_path, 'rb') as f:
                            content_bytes = f.read()
                        content = base64.b64encode(content_bytes).decode('ascii')
                        
                        # Calculate relative path
                        rel_path = file_path.relative_to(input_path)
                        rel_path_str = str(rel_path).replace('\\', '/')  # POSIX style
                        
                        # Add separator
                        mtxt_lines.append(self.separator)
                        
                        # Add metadata
                        mtxt_lines.append(f"FILENAME: {rel_path_str}")
                        mtxt_lines.append("ENCODING: base64")
                        # Try to guess MIME type from extension
                        mime_type = self.guess_mime_type(rel_path_str)
                        if mime_type:
                            mtxt_lines.append(f"MIME: {mime_type}")
                        mtxt_lines.append("")  # Blank line ends metadata
                        
                        # Add binary content as base64
                        mtxt_lines.append(content)
                        
                    except Exception:
                        # If even binary reading fails, skip the file
                        continue
                        
                except Exception as e:
                    # Skip files that can't be read at all
                    continue
                    
        return '\n'.join(mtxt_lines)
        
    def guess_mime_type(self, filename):
        """Guess MIME type from file extension"""
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.yaml': 'text/yaml',
            '.yml': 'text/yaml',
            '.ini': 'text/plain',
            '.cfg': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip',
            '.exe': 'application/x-executable',
            '.dll': 'application/x-msdownload',
        }
        
        ext = os.path.splitext(filename)[1].lower()
        return mime_types.get(ext)
        
    def create_mtxt_from_single_file_text(self, input_file):
        """Create DFB content from a single file (any type)"""
        mtxt_lines = ["DFB V1"]
        mtxt_lines.append(f"SEPARATOR: {self.separator}")
        mtxt_lines.append("")  # Blank line ends control block
        
        # Get filename
        filename = os.path.basename(input_file)
        
        # Try to read as text file first
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add separator
            mtxt_lines.append(self.separator)
            
            # Add metadata
            mtxt_lines.append(f"FILENAME: {filename}")
            mtxt_lines.append("ENCODING: utf-8")
            # Try to guess MIME type from extension
            mime_type = self.guess_mime_type(filename)
            if mime_type:
                mtxt_lines.append(f"MIME: {mime_type}")
            mtxt_lines.append("")  # Blank line ends metadata
            
            # Add file content
            mtxt_lines.append(content)
            
        except UnicodeDecodeError:
            # Try to read as binary and convert to base64
            try:
                with open(input_file, 'rb') as f:
                    content_bytes = f.read()
                content = base64.b64encode(content_bytes).decode('ascii')
                
                # Add separator
                mtxt_lines.append(self.separator)
                
                # Add metadata
                mtxt_lines.append(f"FILENAME: {filename}")
                mtxt_lines.append("ENCODING: base64")
                # Try to guess MIME type from extension
                mime_type = self.guess_mime_type(filename)
                if mime_type:
                    mtxt_lines.append(f"MIME: {mime_type}")
                mtxt_lines.append("")  # Blank line ends metadata
                
                # Add binary content as base64
                mtxt_lines.append(content)
                
            except Exception as e:
                raise ValueError(f"Cannot read file: {str(e)}")
                
        except Exception as e:
            raise ValueError(f"Cannot read file: {str(e)}")
            
        return '\n'.join(mtxt_lines)

def main():
    root = tk.Tk()
    app = MTXTConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
