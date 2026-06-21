"""
PDF Merger and Splitter Tool
A comprehensive GUI application for merging and splitting PDF files
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import PyPDF2
from pathlib import Path
import threading
import re
from datetime import datetime


class PDFMergerSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger & Splitter Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.pdf_files = []
        self.output_file = tk.StringVar()
        self.split_output_dir = tk.StringVar()
        self.page_range = tk.StringVar()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.merger_tab = ttk.Frame(self.notebook)
        self.splitter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.merger_tab, text="PDF Merger")
        self.notebook.add(self.splitter_tab, text="PDF Splitter")
        
        # Setup each tab
        self.setup_merger_tab()
        self.setup_splitter_tab()
        
        # Status bar
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_merger_tab(self):
        """Setup the PDF merger tab"""
        # Main container
        main_frame = ttk.Frame(self.merger_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Left frame for controls
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10))
        
        # Right frame for instructions
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)
        right_frame.pack_propagate(False)
        
        # === Left Frame Controls ===
        # File list
        ttk.Label(left_frame, text="PDF Files to Merge:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.file_listbox = tk.Listbox(list_frame, height=12, selectmode=tk.EXTENDED)
        self.file_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Enable drag and drop
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
        
        # Buttons for file management
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Add PDF Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # Move up/down buttons
        move_frame = ttk.Frame(left_frame)
        move_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(move_frame, text="↑ Move Up", command=self.move_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(move_frame, text="↓ Move Down", command=self.move_down).pack(side=tk.LEFT, padx=(0, 5))
        
        # Output file selection
        ttk.Label(left_frame, text="Output PDF File:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(left_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file, state='readonly')
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", command=self.select_output_file).pack(side=tk.RIGHT)
        
        # Merge button
        self.merge_btn = ttk.Button(left_frame, text="Merge PDFs", command=self.start_merge, 
                                   style='Accent.TButton')
        self.merge_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Progress bar
        self.merge_progress = ttk.Progressbar(left_frame, mode='indeterminate')
        self.merge_progress.pack(fill=tk.X, pady=(5, 0))
        
        # === Right Frame (Instructions) ===
        ttk.Label(right_frame, text="How to Use:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        instructions = """
        1. Add PDF files using "Add PDF Files" button
        2. Or drag and drop PDF files into the list
        3. Reorder files using Up/Down buttons
        4. Select output file location
        5. Click "Merge PDFs" to start
        
        The files will be merged in the order
        they appear in the list.
        """
        
        inst_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=12, state='normal')
        inst_text.insert('1.0', instructions)
        inst_text.config(state='disabled')
        inst_text.pack(fill='both', expand=True)
        
        # File info display
        ttk.Label(right_frame, text="File Information:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.file_info_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=8, state='normal')
        self.file_info_text.pack(fill='both', expand=True)
    
    def setup_splitter_tab(self):
        """Setup the PDF splitter tab"""
        main_frame = ttk.Frame(self.splitter_tab, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Input file selection
        ttk.Label(main_frame, text="Input PDF File:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.split_input_file = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.split_input_file, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.select_split_input).pack(side=tk.RIGHT)
        
        # Split options
        options_frame = ttk.LabelFrame(main_frame, text="Split Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Radio buttons for split method
        self.split_method = tk.StringVar(value="range")
        
        ttk.Radiobutton(options_frame, text="Extract specific pages", variable=self.split_method, 
                       value="range", command=self.toggle_split_options).pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(options_frame, text="Split into individual pages", variable=self.split_method, 
                       value="individual", command=self.toggle_split_options).pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(options_frame, text="Split by page ranges", variable=self.split_method, 
                       value="ranges", command=self.toggle_split_options).pack(anchor=tk.W, pady=(0, 5))
        
        # Range input (for range method)
        self.range_frame = ttk.Frame(options_frame)
        self.range_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.range_frame, text="Page Range (e.g., 1,3-5,7):").pack(anchor=tk.W)
        self.range_entry = ttk.Entry(self.range_frame, width=40)
        self.range_entry.pack(fill=tk.X, pady=(5, 0))
        self.range_entry.insert(0, "1-5")
        
        # Ranges input (for ranges method)
        self.ranges_frame = ttk.Frame(options_frame)
        
        ttk.Label(self.ranges_frame, text="Page Ranges (e.g., 1-3,4-6,7-10):").pack(anchor=tk.W)
        self.ranges_entry = ttk.Entry(self.ranges_frame, width=40)
        self.ranges_entry.pack(fill=tk.X, pady=(5, 0))
        self.ranges_entry.insert(0, "1-3,4-6,7-10")
        
        # Initially hide ranges frame
        self.ranges_frame.pack_forget()
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        output_dir_frame = ttk.Frame(main_frame)
        output_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.split_output_entry = ttk.Entry(output_dir_frame, textvariable=self.split_output_dir, state='readonly')
        self.split_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(output_dir_frame, text="Browse", command=self.select_split_output_dir).pack(side=tk.RIGHT)
        
        # Split button
        self.split_btn = ttk.Button(main_frame, text="Split PDF", command=self.start_split, 
                                   style='Accent.TButton')
        self.split_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Progress
        self.split_progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.split_progress.pack(fill=tk.X, pady=(5, 0))
        
        # Status log
        ttk.Label(main_frame, text="Status Log:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        self.split_log = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10)
        self.split_log.pack(fill='both', expand=True)
    
    def toggle_split_options(self):
        """Toggle visibility of split options based on selected method"""
        method = self.split_method.get()
        
        if method == "range":
            self.range_frame.pack(fill=tk.X, pady=(5, 0))
            self.ranges_frame.pack_forget()
        elif method == "ranges":
            self.range_frame.pack_forget()
            self.ranges_frame.pack(fill=tk.X, pady=(5, 0))
        else:  # individual
            self.range_frame.pack_forget()
            self.ranges_frame.pack_forget()
    
    def on_drop(self, event):
        """Handle drag and drop of files"""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith('.pdf'):
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
        self.update_file_list()
    
    def add_files(self):
        """Add PDF files to the list"""
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")]
        )
        for file in files:
            if file not in self.pdf_files:
                self.pdf_files.append(file)
        self.update_file_list()
    
    def remove_selected(self):
        """Remove selected files from the list"""
        selected = self.file_listbox.curselection()
        for index in reversed(sorted(selected)):
            del self.pdf_files[index]
        self.update_file_list()
    
    def clear_files(self):
        """Clear all files from the list"""
        self.pdf_files.clear()
        self.update_file_list()
        self.file_info_text.delete('1.0', tk.END)
    
    def move_up(self):
        """Move selected file up in the list"""
        selected = self.file_listbox.curselection()
        if selected and selected[0] > 0:
            index = selected[0]
            self.pdf_files[index], self.pdf_files[index-1] = self.pdf_files[index-1], self.pdf_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index-1)
    
    def move_down(self):
        """Move selected file down in the list"""
        selected = self.file_listbox.curselection()
        if selected and selected[0] < len(self.pdf_files) - 1:
            index = selected[0]
            self.pdf_files[index], self.pdf_files[index+1] = self.pdf_files[index+1], self.pdf_files[index]
            self.update_file_list()
            self.file_listbox.selection_set(index+1)
    
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
        
        # Update file info
        self.update_file_info()
    
    def update_file_info(self):
        """Update file information display"""
        self.file_info_text.delete('1.0', tk.END)
        if self.pdf_files:
            info = f"Total files: {len(self.pdf_files)}\n\n"
            for i, file in enumerate(self.pdf_files, 1):
                try:
                    with open(file, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        pages = len(reader.pages)
                        info += f"{i}. {os.path.basename(file)}\n"
                        info += f"   Pages: {pages}\n"
                        info += f"   Size: {os.path.getsize(file) / 1024:.1f} KB\n\n"
                except:
                    info += f"{i}. {os.path.basename(file)}\n"
                    info += "   [Error reading file]\n\n"
            self.file_info_text.insert('1.0', info)
    
    def select_output_file(self):
        """Select output file location"""
        file = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file:
            self.output_file.set(file)
    
    def select_split_input(self):
        """Select input PDF for splitting"""
        file = filedialog.askopenfilename(
            title="Select PDF to Split",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file:
            self.split_input_file.set(file)
            self.update_split_info()
    
    def select_split_output_dir(self):
        """Select output directory for split files"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.split_output_dir.set(directory)
    
    def update_split_info(self):
        """Update split info in log"""
        self.split_log.delete('1.0', tk.END)
        if self.split_input_file.get():
            try:
                with open(self.split_input_file.get(), 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    pages = len(reader.pages)
                    self.split_log.insert('1.0', f"File: {os.path.basename(self.split_input_file.get())}\n")
                    self.split_log.insert('1.0', f"Total pages: {pages}\n")
                    self.split_log.insert('1.0', "Ready to split.\n")
            except Exception as e:
                self.split_log.insert('1.0', f"Error reading file: {str(e)}\n")
    
    def start_merge(self):
        """Start the merge process in a separate thread"""
        if not self.pdf_files:
            messagebox.showwarning("Warning", "Please add PDF files to merge.")
            return
        
        if not self.output_file.get():
            messagebox.showwarning("Warning", "Please select an output file.")
            return
        
        # Disable merge button and show progress
        self.merge_btn.config(state='disabled')
        self.merge_progress.start()
        self.status_bar.config(text="Merging PDF files...")
        
        # Start merge in thread
        thread = threading.Thread(target=self.merge_pdfs)
        thread.daemon = True
        thread.start()
    
    def merge_pdfs(self):
        """Merge the PDF files"""
        try:
            merger = PyPDF2.PdfMerger()
            
            for file in self.pdf_files:
                try:
                    merger.append(file)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error reading {os.path.basename(file)}:\n{str(e)}"))
                    self.reset_merge_ui()
                    return
            
            # Write merged file
            merger.write(self.output_file.get())
            merger.close()
            
            self.root.after(0, self.merge_complete)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error merging files:\n{str(e)}"))
            self.root.after(0, self.reset_merge_ui)
    
    def merge_complete(self):
        """Handle merge completion"""
        self.merge_progress.stop()
        self.merge_btn.config(state='normal')
        self.status_bar.config(text="Merge complete!")
        messagebox.showinfo("Success", f"PDFs merged successfully!\n\nSaved to: {self.output_file.get()}")
        self.reset_merge_ui()
    
    def reset_merge_ui(self):
        """Reset merge UI elements"""
        self.merge_progress.stop()
        self.merge_btn.config(state='normal')
        self.status_bar.config(text="Ready")
    
    def start_split(self):
        """Start the split process in a separate thread"""
        if not self.split_input_file.get():
            messagebox.showwarning("Warning", "Please select an input PDF file.")
            return
        
        if not self.split_output_dir.get():
            messagebox.showwarning("Warning", "Please select an output directory.")
            return
        
        # Disable split button and show progress
        self.split_btn.config(state='disabled')
        self.split_progress.start()
        self.split_log.insert(tk.END, "Splitting PDF...\n")
        self.split_log.see(tk.END)
        
        # Start split in thread
        thread = threading.Thread(target=self.split_pdf)
        thread.daemon = True
        thread.start()
    
    def split_pdf(self):
        """Split the PDF based on selected method"""
        try:
            input_file = self.split_input_file.get()
            output_dir = self.split_output_dir.get()
            method = self.split_method.get()
            
            # Read the PDF
            reader = PyPDF2.PdfReader(input_file)
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                raise ValueError("The PDF file appears to be empty.")
            
            if method == "individual":
                # Split into individual pages
                self.split_individual(reader, output_dir, total_pages)
            elif method == "range":
                # Extract specific pages
                range_str = self.range_entry.get().strip()
                if not range_str:
                    raise ValueError("Please enter page range.")
                self.split_range(reader, output_dir, range_str)
            elif method == "ranges":
                # Split by page ranges
                ranges_str = self.ranges_entry.get().strip()
                if not ranges_str:
                    raise ValueError("Please enter page ranges.")
                self.split_ranges(reader, output_dir, ranges_str, total_pages)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error splitting PDF:\n{str(e)}"))
            self.root.after(0, self.reset_split_ui)
    
    def split_individual(self, reader, output_dir, total_pages):
        """Split PDF into individual pages"""
        base_name = os.path.splitext(os.path.basename(self.split_input_file.get()))[0]
        
        for i in range(total_pages):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[i])
            
            output_file = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            self.root.after(0, lambda msg=f"Page {i+1} saved.": self.update_split_log(msg))
        
        self.root.after(0, lambda: self.split_complete(total_pages))
    
    def split_range(self, reader, output_dir, range_str):
        """Extract specific pages from PDF"""
        pages_to_extract = self.parse_range(range_str, len(reader.pages))
        
        writer = PyPDF2.PdfWriter()
        for page_num in pages_to_extract:
            writer.add_page(reader.pages[page_num - 1])
        
        base_name = os.path.splitext(os.path.basename(self.split_input_file.get()))[0]
        output_file = os.path.join(output_dir, f"{base_name}_extracted.pdf")
        
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        self.root.after(0, lambda: self.split_complete(len(pages_to_extract)))
    
    def split_ranges(self, reader, output_dir, ranges_str, total_pages):
        """Split PDF by page ranges into multiple files"""
        ranges = self.parse_ranges(ranges_str, total_pages)
        base_name = os.path.splitext(os.path.basename(self.split_input_file.get()))[0]
        
        for idx, page_range in enumerate(ranges, 1):
            writer = PyPDF2.PdfWriter()
            for page_num in page_range:
                writer.add_page(reader.pages[page_num - 1])
            
            output_file = os.path.join(output_dir, f"{base_name}_part_{idx}.pdf")
            with open(output_file, 'wb') as f:
                writer.write(f)
            
            self.root.after(0, lambda msg=f"Part {idx} saved.": self.update_split_log(msg))
        
        self.root.after(0, lambda: self.split_complete(len(ranges)))
    
    def parse_range(self, range_str, total_pages):
        """Parse page range string (e.g., '1,3-5,7')"""
        pages = set()
        for part in range_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f"Invalid range: {part}")
                pages.update(range(start, end + 1))
            else:
                page = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(f"Invalid page number: {page}")
                pages.add(page)
        
        return sorted(pages)
    
    def parse_ranges(self, ranges_str, total_pages):
        """Parse multiple page ranges (e.g., '1-3,4-6,7-10')"""
        ranges = []
        for part in ranges_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f"Invalid range: {part}")
                ranges.append(list(range(start, end + 1)))
            else:
                page = int(part)
                if page < 1 or page > total_pages:
                    raise ValueError(f"Invalid page number: {page}")
                ranges.append([page])
        
        return ranges
    
    def update_split_log(self, message):
        """Update split log"""
        self.split_log.insert(tk.END, f"{message}\n")
        self.split_log.see(tk.END)
    
    def split_complete(self, count):
        """Handle split completion"""
        self.split_progress.stop()
        self.split_btn.config(state='normal')
        self.split_log.insert(tk.END, f"\n✅ Split complete! {count} file(s) created.\n")
        self.split_log.see(tk.END)
        messagebox.showinfo("Success", f"PDF split successfully!\n\nCreated {count} file(s).")
        self.reset_split_ui()
    
    def reset_split_ui(self):
        """Reset split UI elements"""
        self.split_progress.stop()
        self.split_btn.config(state='normal')


def main():
    try:
        root = TkinterDnD.Tk()
    except:
        # Fallback if tkinterdnd2 is not installed
        root = tk.Tk()
        messagebox.showinfo("Info", "Drag and drop not available. Install tkinterdnd2 for drag-and-drop support.")
    
    # Set style for accent button
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    app = PDFMergerSplitter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
