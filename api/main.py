import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import binascii
import os
import sys

class HexPreviewWindow:
    def __init__(self, parent, hex_data):
        self.parent = parent
        self.hex_data = hex_data
        self.window = tk.Toplevel(parent.root)
        self.window.title("Hex Data Preview")
        self.window.geometry("600x400")

        # Main frame for the text and scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Hex text area
        self.hex_text = tk.Text(main_frame, height=20, width=80, font=("Courier", 10))
        self.hex_text.pack(side="left", fill="both", expand=True)

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.hex_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.hex_text.config(yscrollcommand=scrollbar.set)

        # Load the hex data
        self.load_hex_data(hex_data)

        # Range selection frame
        range_frame = ttk.Frame(self.window)
        range_frame.pack(fill="x", pady=5)

        ttk.Label(range_frame, text="Start Offset (hex):").pack(side="left", padx=5)
        self.start_offset = tk.StringVar()
        ttk.Entry(range_frame, textvariable=self.start_offset, width=10).pack(side="left", padx=5)

        ttk.Label(range_frame, text="End Offset (hex):").pack(side="left", padx=5)
        self.end_offset = tk.StringVar()
        ttk.Entry(range_frame, textvariable=self.end_offset, width=10).pack(side="left", padx=5)

        ttk.Button(range_frame, text="Select Range", command=self.select_range).pack(side="left", padx=5)

        # Buttons frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Copy Selected", command=self.copy_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side="right", padx=5)

    def load_hex_data(self, hex_data):
        self.hex_text.delete(1.0, tk.END)
        try:
            hex_bytes = binascii.unhexlify(hex_data)
            self.byte_length = len(hex_bytes)  # Store the byte length for range validation
            lines = []
            for i in range(0, len(hex_bytes), 16):
                chunk = hex_bytes[i:i + 16]
                if len(chunk) > 0:
                    hex_value = " ".join(f"{byte:02X}" for byte in chunk)
                    ascii_value = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in chunk.decode('ascii', errors='ignore'))
                    hex_part = f"{hex_value:<47}"
                    line = f"{i:08x}  {hex_part}  {ascii_value}\n"
                    lines.append(line)
            self.hex_text.insert(tk.END, "".join(lines).rstrip())
        except binascii.Error:
            self.parent.log("Invalid hex data provided for preview.")

    def select_range(self):
        try:
            start = int(self.start_offset.get(), 16)
            end = int(self.end_offset.get(), 16)

            # Validate range
            if start < 0 or end < start or end >= self.byte_length:
                self.parent.log(f"Invalid range: start={start}, end={end}. Must be within 0 to {self.byte_length-1}.")
                return

            # Calculate the line numbers and positions
            start_line = (start // 16) + 1
            start_byte_in_line = start % 16
            start_pos = f"{start_line}.{10 + start_byte_in_line * 3}"

            end_line = (end // 16) + 1
            end_byte_in_line = end % 16
            end_pos = f"{end_line}.{10 + end_byte_in_line * 3 + 1}"

            # Select the range in the text widget
            self.hex_text.tag_remove("sel", "1.0", tk.END)
            self.hex_text.tag_add("sel", start_pos, end_pos)
            self.hex_text.see(start_pos)  # Scroll to the start of the selection
            self.parent.log(f"Selected range from offset {start:08x} to {end:08x}.")
        except ValueError:
            self.parent.log("Invalid offset values. Please enter valid hexadecimal numbers.")

    def copy_selected(self):
        try:
            if self.hex_text.tag_ranges("sel"):
                selection = self.hex_text.get("sel.first", "sel.last")
                lines = selection.strip().splitlines()
                hex_data = []
                for line in lines:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    hex_start_idx = 1
                    hex_bytes = min(16, (len(parts) - 1) // 3)
                    ascii_start_idx = hex_start_idx + hex_bytes
                    hex_values = parts[hex_start_idx:ascii_start_idx]
                    if hex_values:
                        hex_data.extend(hex_values)
                hex_string = "".join(hex_data).replace(" ", "")
                self.parent.copied_data = hex_string
                self.parent.log(f"Copied selected hex from preview: {hex_string[:100]}... ({len(hex_string)//2} bytes)")
            else:
                self.parent.log("No selection to copy in preview window.")
        except tk.TclError:
            self.parent.log("No selection to copy in preview window.")

class HeaderReplacementWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Replace STY Header with AUS Header")
        self.window.geometry("1200x600")

        # Main frame split into AUS and STY sections
        main_frame = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True)

        # AUS frame (left)
        aus_frame = ttk.LabelFrame(main_frame, text="AUS File Raw Data", padding=5)
        main_frame.add(aus_frame, weight=1)

        self.aus_text = tk.Text(aus_frame, height=30, width=60, font=("Courier", 10))
        self.aus_text.pack(fill="both", expand=True, padx=5, pady=5)

        aus_scrollbar = ttk.Scrollbar(aus_frame, orient="vertical", command=self.aus_text.yview)
        aus_scrollbar.pack(side="right", fill="y")
        self.aus_text.config(yscrollcommand=aus_scrollbar.set)

        # STY frame (right)
        sty_frame = ttk.LabelFrame(main_frame, text="STY File Raw Data", padding=5)
        main_frame.add(sty_frame, weight=1)

        self.sty_text = tk.Text(sty_frame, height=30, width=60, font=("Courier", 10))
        self.sty_text.pack(fill="both", expand=True, padx=5, pady=5)

        sty_scrollbar = ttk.Scrollbar(sty_frame, orient="vertical", command=self.sty_text.yview)
        sty_scrollbar.pack(side="right", fill="y")
        self.sty_text.config(yscrollcommand=sty_scrollbar.set)

        # Load full raw data into both text areas
        self.load_aus_data()
        self.load_sty_data()

        # Buttons frame at the bottom
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(button_frame, text="Select and Copy from AUS", command=self.select_and_copy_aus).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Select and Copy from STY", command=self.select_and_copy_sty).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Paste to AUS", command=self.paste_to_aus).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Paste to STY", command=self.paste_to_sty).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Apply Header Replacement", command=self.apply_header_replacement).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side="right", padx=5)

    def load_aus_data(self):
        self.aus_text.delete(1.0, tk.END)
        data = self.parent.aus_data
        if not data:
            self.parent.log("No AUS data to display.")
            return
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            hex_value = " ".join(f"{byte:02X}" for byte in chunk)
            ascii_value = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in chunk.decode('ascii', errors='ignore'))
            hex_part = f"{hex_value:<47}"
            line = f"{i:08x}  {hex_part}  {ascii_value}\n"
            lines.append(line)
        self.aus_text.insert(tk.END, "".join(lines).rstrip())
        self.parent.log(f"Loaded full raw AUS data into header replacement window: {len(data)} bytes.")

    def load_sty_data(self):
        self.sty_text.delete(1.0, tk.END)
        data = self.parent.sty_data
        if not data:
            self.parent.log("No STY data to display.")
            return
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            hex_value = " ".join(f"{byte:02X}" for byte in chunk)
            ascii_value = ''.join(c if 32 <= ord(c) <= 126 else '.' for c in chunk.decode('ascii', errors='ignore'))
            hex_part = f"{hex_value:<47}"
            line = f"{i:08x}  {hex_part}  {ascii_value}\n"
            lines.append(line)
        self.sty_text.insert(tk.END, "".join(lines).rstrip())
        self.parent.log(f"Loaded full raw STY data into header replacement window: {len(data)} bytes.")

    def select_and_copy_aus(self):
        try:
            if self.aus_text.tag_ranges("sel"):
                selection = self.aus_text.get("sel.first", "sel.last")
                lines = selection.strip().splitlines()
                hex_data = []
                for line in lines:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    hex_start_idx = 1
                    hex_bytes = min(16, (len(parts) - 1) // 3)
                    ascii_start_idx = hex_start_idx + hex_bytes
                    hex_values = parts[hex_start_idx:ascii_start_idx]
                    if hex_values:
                        hex_data.extend(hex_values)
                hex_string = "".join(hex_data).replace(" ", "")
                self.parent.copied_data = hex_string
                self.parent.log(f"Copied hex from AUS: {hex_string[:100]}...")
            else:
                self.parent.log("No selection to copy from AUS.")
        except tk.TclError:
            self.parent.log("No selection to copy from AUS.")

    def select_and_copy_sty(self):
        try:
            if self.sty_text.tag_ranges("sel"):
                selection = self.sty_text.get("sel.first", "sel.last")
                lines = selection.strip().splitlines()
                hex_data = []
                for line in lines:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    hex_start_idx = 1
                    hex_bytes = min(16, (len(parts) - 1) // 3)
                    ascii_start_idx = hex_start_idx + hex_bytes
                    hex_values = parts[hex_start_idx:ascii_start_idx]
                    if hex_values:
                        hex_data.extend(hex_values)
                hex_string = "".join(hex_data).replace(" ", "")
                self.parent.copied_data = hex_string
                self.parent.log(f"Copied hex from STY: {hex_string[:100]}...")
            else:
                self.parent.log("No selection to copy from STY.")
        except tk.TclError:
            self.parent.log("No selection to copy from STY.")

    def paste_to_aus(self):
        if self.parent.copied_data:
            try:
                hex_bytes = " ".join(self.parent.copied_data[i:i+2] for i in range(0, len(self.parent.copied_data), 2))
                self.aus_text.insert(tk.INSERT, hex_bytes)
                self.parent.log(f"Pasted hex to AUS: {self.parent.copied_data[:100]}...")
            except tk.TclError:
                self.parent.log("Failed to paste hex data to AUS.")
        else:
            self.parent.log("No data to paste to AUS.")

    def paste_to_sty(self):
        if self.parent.copied_data:
            try:
                hex_bytes = " ".join(self.parent.copied_data[i:i+2] for i in range(0, len(self.parent.copied_data), 2))
                self.sty_text.insert(tk.INSERT, hex_bytes)
                self.parent.log(f"Pasted hex to STY: {self.parent.copied_data[:100]}...")
            except tk.TclError:
                self.parent.log("Failed to paste hex data to STY.")
        else:
            self.parent.log("No data to paste to STY.")

    def apply_header_replacement(self):
        sty_content = self.sty_text.get(1.0, tk.END).strip().splitlines()
        new_sty_data = bytearray()
        for line in sty_content:
            parts = line.split()
            if len(parts) < 2:
                continue
            hex_values = parts[1:17]
            for hex_val in hex_values:
                try:
                    byte = int(hex_val, 16)
                    new_sty_data.append(byte)
                except ValueError:
                    continue
        self.parent.sty_data = bytes(new_sty_data)

        aus_header_length = int(self.parent.aus_header_length.get(), 16)
        aus_header = self.parent.aus_data[:aus_header_length] if len(self.parent.aus_data) >= aus_header_length else self.parent.aus_data
        if len(self.parent.sty_data) >= aus_header_length:
            self.parent.sty_data = aus_header + self.parent.sty_data[aus_header_length:]
        else:
            self.parent.sty_data = aus_header

        self.parent.log("Applied header replacement to STY data.")
        self.parent.load_hex_editor(self.parent.sty_editor, self.parent.sty_data, "sty")
        self.window.destroy()

class DataSelectionWindow:
    def __init__(self, parent, data, title):
        self.parent = parent
        self.data = data
        self.window = tk.Toplevel(parent.root)
        self.window.title(title)
        self.window.geometry("1000x600")
        self.window.minsize(800, 400)

        # Performance settings
        self.chunk_size = 1024 * 16  # 16KB chunks for rendering
        self.current_start = 0
        self.total_lines = (len(data) + 15) // 16  # Calculate total number of lines

        # Configure window
        if sys.platform == "win32":
            self.window.state('zoomed')
        self.window.resizable(True, True)

        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True)

        # Toolbar frame
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill="x", pady=(5, 0))

        # Selection tools
        ttk.Label(toolbar_frame, text="Selection:").pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Select All", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Clear Selection", command=self.clear_selection).pack(side="left", padx=5)
        
        # Navigation tools
        ttk.Separator(toolbar_frame, orient="vertical").pack(side="left", padx=5, fill="y")
        ttk.Label(toolbar_frame, text="Go to offset (hex):").pack(side="left", padx=5)
        self.goto_offset = tk.StringVar()
        ttk.Entry(toolbar_frame, textvariable=self.goto_offset, width=10).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Go", command=self.goto_offset_cmd).pack(side="left", padx=5)
        
        # Copy tools
        ttk.Separator(toolbar_frame, orient="vertical").pack(side="left", padx=5, fill="y")
        ttk.Label(toolbar_frame, text="Data:").pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Copy Selected", command=self.copy_selected).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Copy as Hex", command=self.copy_as_hex).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Copy as Bytes", command=self.copy_as_bytes).pack(side="left", padx=5)

        # Search tools
        ttk.Separator(toolbar_frame, orient="vertical").pack(side="left", padx=5, fill="y")
        ttk.Label(toolbar_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(toolbar_frame, textvariable=self.search_var, width=20).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Find", command=self.find_next).pack(side="left", padx=5)
        ttk.Button(toolbar_frame, text="Find All", command=self.find_all).pack(side="left", padx=5)

        # Editor container
        editor_container = ttk.Frame(main_frame)
        editor_container.pack(fill="both", expand=True, pady=5)
        editor_container.grid_rowconfigure(0, weight=1)
        editor_container.grid_columnconfigure(0, weight=1)

        # Create hex editor with performance optimizations
        self.hex_editor = tk.Text(
            editor_container,
            font=("Courier", 10),
            wrap="none",
            blockcursor=True,  # Better cursor performance
            maxundo=0,  # Disable undo for better performance
            setgrid=True,  # Better grid alignment
            height=20,
            width=80
        )
        
        # Configure tags for better performance
        self.hex_editor.tag_configure("search", background="yellow")
        self.hex_editor.tag_configure("sel", background="lightblue")
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(editor_container, orient="vertical")
        x_scrollbar = ttk.Scrollbar(editor_container, orient="horizontal")
        
        # Configure scrolling
        y_scrollbar.config(command=self.on_vertical_scroll)
        x_scrollbar.config(command=self.hex_editor.xview)
        self.hex_editor.config(
            yscrollcommand=self.on_scroll_update,
            xscrollcommand=x_scrollbar.set
        )

        # Layout with grid
        self.hex_editor.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.pack(fill="x", pady=(5, 0))

        # Initialize view
        self.load_visible_data()
        self.update_status()

        # Bind events
        self.hex_editor.bind("<MouseWheel>", self._on_mousewheel)
        self.hex_editor.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_visible_data(self):
        """Load only the visible portion of data"""
        self.hex_editor.delete(1.0, tk.END)
        start_line = self.current_start
        end_line = min(start_line + (self.chunk_size // 16), self.total_lines)
        
        lines = []
        for i in range(start_line * 16, min(end_line * 16, len(self.data)), 16):
            chunk = self.data[i:i + 16]
            hex_value = " ".join(f"{byte:02X}" for byte in chunk)
            ascii_value = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            hex_part = f"{hex_value:<47}"
            line = f"{i:08x}  {hex_part}  {ascii_value}\n"
            lines.append(line)
        
        self.hex_editor.insert(tk.END, "".join(lines))
        self.status_var.set(f"Showing bytes {start_line*16:,} to {min(end_line*16, len(self.data)):,} of {len(self.data):,}")

    def on_vertical_scroll(self, *args):
        """Handle scrollbar movement"""
        if args[0] == "moveto":
            fraction = float(args[1])
            line = int(fraction * self.total_lines)
            if line != self.current_start:
                self.current_start = line
                self.load_visible_data()
        elif args[0] == "scroll":
            amount = int(args[1])
            if args[2] == "units":
                self.current_start = max(0, min(self.current_start + amount, self.total_lines - 1))
            elif args[2] == "pages":
                self.current_start = max(0, min(self.current_start + amount * (self.chunk_size // 16), self.total_lines - 1))
            self.load_visible_data()

    def on_scroll_update(self, first, last):
        """Update scrollbar position"""
        first = float(first)
        last = float(last)
        if self.current_start / self.total_lines != first:
            self.current_start = int(first * self.total_lines)
            self.load_visible_data()

    def goto_offset_cmd(self):
        """Jump to specific offset"""
        try:
            offset = int(self.goto_offset.get(), 16)
            if 0 <= offset < len(self.data):
                line = offset // 16
                self.current_start = max(0, line - 5)  # Show 5 lines before target
                self.load_visible_data()
                # Highlight the target offset
                target_line = line - self.current_start + 1
                target_col = 10 + (offset % 16) * 3
                self.hex_editor.see(f"{target_line}.{target_col}")
                self.hex_editor.tag_add("search", f"{target_line}.{target_col}", f"{target_line}.{target_col+2}")
        except ValueError:
            self.status_var.set("Invalid offset value")

    def _on_mousewheel(self, event):
        """Smooth scrolling with mouse wheel"""
        amount = -1 if event.delta > 0 else 1
        self.current_start = max(0, min(self.current_start + amount, self.total_lines - 1))
        self.load_visible_data()

    def _on_shift_mousewheel(self, event):
        """Horizontal scrolling with Shift+mouse wheel"""
        self.hex_editor.xview_scroll(-1 if event.delta > 0 else 1, "units")

    def on_closing(self):
        self.hex_editor.unbind("<MouseWheel>")
        self.hex_editor.unbind("<Shift-MouseWheel>")
        self.window.destroy()

    def select_all(self):
        self.hex_editor.tag_add("sel", "1.0", tk.END)
        self.update_status()

    def clear_selection(self):
        self.hex_editor.tag_remove("sel", "1.0", tk.END)
        self.update_status()

    def copy_selected(self):
        try:
            if self.hex_editor.tag_ranges("sel"):
                selection = self.hex_editor.get("sel.first", "sel.last")
                self.parent.copied_data = self.extract_hex_data(selection)
                self.status_var.set(f"Copied {len(self.parent.copied_data)//2} bytes")
            else:
                self.status_var.set("No selection to copy")
        except tk.TclError:
            self.status_var.set("No selection to copy")

    def copy_as_hex(self):
        try:
            if self.hex_editor.tag_ranges("sel"):
                selection = self.hex_editor.get("sel.first", "sel.last")
                hex_data = self.extract_hex_data(selection)
                self.parent.root.clipboard_clear()
                self.parent.root.clipboard_append(hex_data)
                self.status_var.set(f"Copied {len(hex_data)//2} bytes as hex")
            else:
                self.status_var.set("No selection to copy")
        except tk.TclError:
            self.status_var.set("No selection to copy")

    def copy_as_bytes(self):
        try:
            if self.hex_editor.tag_ranges("sel"):
                selection = self.hex_editor.get("sel.first", "sel.last")
                hex_data = self.extract_hex_data(selection)
                bytes_data = binascii.unhexlify(hex_data)
                self.parent.root.clipboard_clear()
                self.parent.root.clipboard_append(bytes_data)
                self.status_var.set(f"Copied {len(bytes_data)} bytes")
            else:
                self.status_var.set("No selection to copy")
        except tk.TclError:
            self.status_var.set("No selection to copy")

    def find_next(self):
        search_text = self.search_var.get()
        if not search_text:
            return

        # Remove previous highlights
        self.hex_editor.tag_remove("search", "1.0", tk.END)
        
        # Start search from last position
        pos = self.hex_editor.search(search_text, self.last_search_pos)
        if not pos:
            # If not found, wrap around to beginning
            pos = self.hex_editor.search(search_text, "1.0")
            if not pos:
                self.status_var.set("Text not found")
                return

        # Highlight the found text
        end_pos = f"{pos}+{len(search_text)}c"
        self.hex_editor.tag_add("search", pos, end_pos)
        self.hex_editor.tag_config("search", background="yellow")
        self.hex_editor.see(pos)
        self.last_search_pos = end_pos
        self.status_var.set(f"Found at position {pos}")

    def find_all(self):
        search_text = self.search_var.get()
        if not search_text:
                return

        # Remove previous highlights
        self.hex_editor.tag_remove("search", "1.0", tk.END)
        
        # Find all occurrences
        pos = "1.0"
        count = 0
        while True:
            pos = self.hex_editor.search(search_text, pos)
            if not pos:
                break
            end_pos = f"{pos}+{len(search_text)}c"
            self.hex_editor.tag_add("search", pos, end_pos)
            self.hex_editor.tag_config("search", background="yellow")
            pos = end_pos
            count += 1

        self.status_var.set(f"Found {count} occurrences")
        self.hex_editor.see("1.0")

    def extract_hex_data(self, text):
        lines = text.strip().splitlines()
        hex_data = []
        for line in lines:
            parts = line.split()
            if len(parts) > 1:
                hex_values = parts[1:17]  # Get hex values between offset and ASCII
                hex_data.extend(hex_values)
        return "".join(hex_data)

    def update_status(self):
        try:
            if self.hex_editor.tag_ranges("sel"):
                start = self.hex_editor.index("sel.first")
                end = self.hex_editor.index("sel.last")
                selection = self.hex_editor.get(start, end)
                hex_data = self.extract_hex_data(selection)
                self.status_var.set(f"Selected: {len(hex_data)//2} bytes")
            else:
                self.status_var.set("No selection")
        except tk.TclError:
            self.status_var.set("No selection")

class AUSPreviewWindow:
    def __init__(self, parent, data):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("AUS Data Preview - Advanced Hex Editor")
        self.window.geometry("1000x800")
        self.window.minsize(800, 600)

        # Performance settings
        self.chunk_size = 1024 * 16  # 16KB chunks
        self.current_start = 0
        self.data = data
        self.total_lines = (len(data) + 15) // 16
        self.visible_lines = 0  # Will be set after first load

        # Main container with grid
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ttk.Frame(self.window)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Range selection frame
        range_frame = ttk.LabelFrame(toolbar, text="Hex Range Selection", padding=5)
        range_frame.pack(side="left", padx=5, fill="x")

        # Start range
        ttk.Label(range_frame, text="Start Offset (hex):").pack(side="left", padx=2)
        self.start_range = ttk.Entry(range_frame, width=10)
        self.start_range.pack(side="left", padx=2)

        # End range
        ttk.Label(range_frame, text="End Offset (hex):").pack(side="left", padx=2)
        self.end_range = ttk.Entry(range_frame, width=10)
        self.end_range.pack(side="left", padx=2)

        # Quick selection button for 0x170 to end
        ttk.Button(range_frame, text="Select From 0x170 to End", 
                  command=self.select_from_170_to_end).pack(side="left", padx=2)

        # Select and Get Range buttons
        ttk.Button(range_frame, text="Select Range", command=self.select_range).pack(side="left", padx=2)
        ttk.Button(range_frame, text="Get Range Data", command=self.get_range_data).pack(side="left", padx=2)

        # Other toolbar buttons
        ttk.Button(toolbar, text="Find", command=self.show_find_dialog).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Go to Offset", command=self.show_goto_dialog).pack(side="left", padx=2)

        # Hex editor frame
        editor_frame = ttk.Frame(self.window)
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        # Create hex editor
        self.hex_editor = tk.Text(
            editor_frame,
            wrap="none",
            font=("Consolas", 12),
            blockcursor=True,
            maxundo=0,
            height=1,
            width=1
        )
        self.hex_editor.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        self.vsb = ttk.Scrollbar(editor_frame, orient="vertical", command=self.on_vertical_scroll)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb = ttk.Scrollbar(editor_frame, orient="horizontal", command=self.hex_editor.xview)
        self.hsb.grid(row=1, column=0, sticky="ew")

        # Configure scrolling
        self.hex_editor.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set
        )

        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Initialize view
        self.hex_editor.update_idletasks()
        self.calculate_visible_lines()
        self.load_visible_data()
        self.update_status("Ready")

        # Bind events
        self.hex_editor.bind("<MouseWheel>", self.on_mousewheel)
        self.hex_editor.bind("<Configure>", self.on_resize)

    def select_range(self):
        """Select hex range based on input values"""
        try:
            # Get and validate start range
            start_hex = self.start_range.get().strip().upper().replace('0X', '')
            if not start_hex:
                self.update_status("Please enter a start offset")
            return

            # Get and validate end range
            end_hex = self.end_range.get().strip().upper().replace('0X', '')
            if not end_hex:
                self.update_status("Please enter an end offset")
                return

            # Convert hex to integers
            try:
                start = int(start_hex, 16)
                end = int(end_hex, 16)
            except ValueError:
                self.update_status("Invalid hex values. Please enter valid hex numbers (e.g., FF or 0xFF)")
                return

            # Validate range
            if start < 0 or end >= len(self.data) or start > end:
                self.update_status(f"Invalid range. Must be between 0 and {len(self.data)-1:08X}")
                return

            # Calculate the lines where these offsets appear
            start_line = (start // 16) - self.current_start + 1
            end_line = (end // 16) - self.current_start + 1

            # Calculate column positions
            start_col = 10 + (start % 16) * 3
            end_col = 10 + (end % 16) * 3 + 2

            # Clear any existing selection
            self.hex_editor.tag_remove('sel', '1.0', 'end')

            # Add new selection
            self.hex_editor.tag_add('sel', f"{start_line}.{start_col}", f"{end_line}.{end_col}")
            self.hex_editor.see(f"{start_line}.0")

            # Update status
            self.update_status(f"Selected range: {start:08X} to {end:08X}")

        except Exception as e:
            self.update_status(f"Error selecting range: {str(e)}")

    def get_range_data(self):
        """Get hex data between specified ranges and store in parent"""
        try:
            # Get and validate start range
            start_hex = self.start_range.get().strip().upper().replace('0X', '')
            if not start_hex:
                self.update_status("Please enter a start offset")
                return

            # Get and validate end range
            end_hex = self.end_range.get().strip().upper().replace('0X', '')
            if not end_hex:
                self.update_status("Please enter an end offset")
                return

            # Convert hex to integers
            try:
                start = int(start_hex, 16)
                end = int(end_hex, 16)
            except ValueError:
                self.update_status("Invalid hex values. Please enter valid hex numbers (e.g., FF or 0xFF)")
                return

            # Validate range
            if start < 0 or end >= len(self.data) or start > end:
                self.update_status(f"Invalid range. Must be between 0 and {len(self.data)-1:08X}")
                return

            # Extract only the selected range of data
            range_data = self.data[start:end + 1]

            # Store in parent's aus_copied_data
            self.parent.aus_copied_data = range_data

            # Log success and close window
            self.parent.log(f"Copied {len(range_data)} bytes from AUS data (offset {start:08X} to {end:08X})")
            self.window.destroy()

        except Exception as e:
            self.update_status(f"Error getting range data: {str(e)}")
            self.parent.log(f"Error copying range data: {str(e)}")

    def calculate_visible_lines(self):
        """Calculate how many lines can be displayed in the current window"""
        font_height = self.hex_editor.tk.call("font", "metrics", self.hex_editor.cget("font"), "-linespace")
        widget_height = self.hex_editor.winfo_height()
        self.visible_lines = max(1, widget_height // font_height)
        
    def on_resize(self, event=None):
        """Handle window resize events"""
        self.calculate_visible_lines()
        self.load_visible_data()

    def on_vertical_scroll(self, *args):
        """Handle scrollbar movement with proper scrolling"""
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self.total_lines - self.visible_lines)
            new_start = int(fraction * self.total_lines)
            new_start = max(0, min(new_start, max_start))
            if new_start != self.current_start:
                self.current_start = new_start
                self.load_visible_data()
                # Update scrollbar position
                if self.total_lines > 0:
                    self.vsb.set(new_start/self.total_lines, 
                               min(1.0, (new_start + self.visible_lines)/self.total_lines))
        elif args[0] == "scroll":
            amount = int(args[1])
            if args[2] == "units":
                delta = amount
            else:  # pages
                delta = amount * self.visible_lines

            max_start = max(0, self.total_lines - self.visible_lines)
            new_start = max(0, min(self.current_start + delta, max_start))
            
            if new_start != self.current_start:
                self.current_start = new_start
                self.load_visible_data()
                # Update scrollbar position
                if self.total_lines > 0:
                    self.vsb.set(new_start/self.total_lines, 
                               min(1.0, (new_start + self.visible_lines)/self.total_lines))

    def load_visible_data(self):
        """Load only the visible portion of data"""
        self.hex_editor.delete(1.0, tk.END)
        
        # Calculate the range of data to display
        start_byte = self.current_start * 16
        end_byte = min(start_byte + (self.visible_lines * 16), len(self.data))
        
        # Ensure we display complete lines
        if end_byte % 16 != 0:
            end_byte = ((end_byte + 15) // 16) * 16
        end_byte = min(end_byte, len(self.data))
        
        lines = []
        for i in range(start_byte, end_byte, 16):
            chunk = self.data[i:min(i + 16, len(self.data))]
            # Pad the last line with spaces to maintain alignment
            hex_value = " ".join(f"{byte:02X}" for byte in chunk)
            hex_value = f"{hex_value:<47}"
            ascii_value = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            ascii_value = f"{ascii_value:<16}"
            line = f"{i:08x}  {hex_value}  {ascii_value}\n"
            lines.append(line)
        
        self.hex_editor.insert(tk.END, "".join(lines))
        
        # Update scrollbar position
        if self.total_lines > 0:
            first = self.current_start / self.total_lines
            last = min(1.0, (self.current_start + self.visible_lines) / self.total_lines)
            self.vsb.set(first, last)
        
        self.update_status(f"Showing bytes {start_byte:,} to {end_byte:,} of {len(self.data):,}")

    def on_mousewheel(self, event):
        """Smooth scrolling with mouse wheel"""
        if event.state & 0x4:  # Control is pressed
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            delta = -1 if event.delta > 0 else 1
            max_start = max(0, self.total_lines - self.visible_lines)
            new_start = max(0, min(self.current_start + delta, max_start))
            
            if new_start != self.current_start:
                self.current_start = new_start
                self.load_visible_data()
                # Update scrollbar position
                if self.total_lines > 0:
                    self.vsb.set(new_start/self.total_lines, 
                               min(1.0, (new_start + self.visible_lines)/self.total_lines))

    def select_all(self):
        self.hex_editor.tag_add("sel", "1.0", tk.END)
        self.update_status("All text selected")

    def copy_selection(self):
        """Copy selected hex data to parent's aus_copied_data"""
        try:
            if self.hex_editor.tag_ranges("sel"):
                selection = self.hex_editor.get("sel.first", "sel.last")
                hex_data = []
                for line in selection.strip().splitlines():
                    parts = line.split()
                    if len(parts) > 1:
                        hex_values = parts[1:17]  # Get hex values between offset and ASCII
                        hex_data.extend(hex_values)
                
                # Convert hex strings to bytes
                hex_string = "".join(hex_data)
                self.parent.aus_copied_data = bytes.fromhex(hex_string)
                
                # Update status and close window
                self.update_status(f"Copied {len(hex_data)} bytes")
                self.parent.log(f"Copied {len(hex_data)} bytes from AUS data")
                self.window.destroy()
            else:
                self.update_status("No selection to copy")
        except Exception as e:
            self.update_status(f"Error copying selection: {str(e)}")

    def show_find_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Find")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()

        ttk.Label(dialog, text="Search for:").pack(pady=5)
        search_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=search_var, width=40)
        entry.pack(pady=5)
        entry.focus_set()

        def find():
            text = search_var.get()
            if text:
                self.find_text(text)
            dialog.destroy()

        ttk.Button(dialog, text="Find", command=find).pack(pady=5)
        dialog.bind("<Return>", lambda e: find())

    def show_goto_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Go to Offset")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()

        ttk.Label(dialog, text="Enter offset (hex):").pack(pady=5)
        offset_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=offset_var, width=20)
        entry.pack(pady=5)
        entry.focus_set()

        def goto():
            try:
                offset = int(offset_var.get(), 16)
                self.goto_offset(offset)
            except ValueError:
                self.update_status("Invalid hex offset")
            dialog.destroy()

        ttk.Button(dialog, text="Go", command=goto).pack(pady=5)
        dialog.bind("<Return>", lambda e: goto())

    def find_text(self, text):
        try:
            # Convert text to hex if it's a hex string
            if all(c in "0123456789ABCDEFabcdef" for c in text):
                search_bytes = bytes.fromhex(text)
            else:
                search_bytes = text.encode('ascii')

            # Search in raw data
            pos = self.data.find(search_bytes)
            if pos >= 0:
                self.goto_offset(pos)
                self.update_status(f"Found at offset: {pos:08x}")
            else:
                self.update_status("Text not found")
        except Exception as e:
            self.update_status(f"Search error: {str(e)}")

    def goto_offset(self, offset):
        if 0 <= offset < len(self.data):
            line = offset // 16
            self.current_start = max(0, line - 5)  # Show 5 lines before target
            self.load_visible_data()
            # Highlight the target offset
            target_line = line - self.current_start + 1
            target_col = 10 + (offset % 16) * 3
            self.hex_editor.see(f"{target_line}.{target_col}")
            self.hex_editor.tag_add("found", f"{target_line}.{target_col}", f"{target_line}.{target_col+2}")
            self.hex_editor.tag_config("found", background="yellow")

    def zoom_in(self):
        current_size = self.hex_editor.cget("font").split()[-1]
        new_size = min(24, int(current_size) + 2)
        self.hex_editor.configure(font=("Consolas", new_size))

    def zoom_out(self):
        current_size = self.hex_editor.cget("font").split()[-1]
        new_size = max(8, int(current_size) - 2)
        self.hex_editor.configure(font=("Consolas", new_size))

    def update_status(self, message):
        self.status_var.set(message)

    def on_selection_change(self, event=None):
        try:
            if not hasattr(self, 'hex_editor'):
                return

            selection = self.hex_editor.tag_ranges("sel")
            if not selection:
                self.status_var.set("No selection")
                return

            # Get the line and column of the selection
            start_line = self.hex_editor.index(selection[0]).split('.')[0]
            end_line = self.hex_editor.index(selection[1]).split('.')[0]
            
            # Calculate byte offsets
            start_offset = (int(start_line) - 1) * 16
            end_offset = (int(end_line) - 1) * 16
            
            # Format offsets with 8 digits
            start_hex = self.format_hex_offset(start_offset)
            end_hex = self.format_hex_offset(end_offset)
            
            # Update status with the formatted offsets
            self.status_var.set(f"Selection: {start_hex} to {end_hex}")
            
            # Update the range inputs with the current selection
            self.start_range.delete(0, tk.END)
            self.start_range.insert(0, start_hex)
            self.end_range.delete(0, tk.END)
            self.end_range.insert(0, end_hex)
            
        except Exception as e:
            self.status_var.set(f"Error updating selection: {str(e)}")
            print(f"Debug - Error details: {str(e)}")  # For debugging

    def select_hex_range(self, editor, start_entry, end_entry):
        """Select hex range in specified editor"""
        try:
            start_hex = start_entry.get().strip().upper().replace('0X', '')
            end_hex = end_entry.get().strip().upper().replace('0X', '')
            
            # Convert hex to int
            start_offset = int(start_hex, 16)
            end_offset = int(end_hex, 16)
            
            # Calculate lines to select
            start_line = (start_offset // 16) + 1
            end_line = (end_offset // 16) + 1
            
            # Select the range
            editor.tag_remove('sel', '1.0', 'end')
            editor.tag_add('sel', f"{start_line}.0", f"{end_line}.0")
            editor.see(f"{start_line}.0")
            
            # Update status
            self.status_var.set(f"Selected range: {self.format_hex_offset(start_offset)} to {self.format_hex_offset(end_offset)}")
            
        except ValueError:
            self.status_var.set("Invalid hex value. Please enter valid hex numbers.")
        except Exception as e:
            self.status_var.set(f"Error selecting range: {str(e)}")

    def format_hex_offset(self, offset):
        """Format hex offset as 8 digits with leading zeros"""
        return f"{offset:08X}"

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        editor = event.widget
        if editor == self.sty_editor:
            delta = -1 if event.delta > 0 else 1
            max_start = max(0, self.sty_total_lines - self.sty_visible_lines)
            new_start = max(0, min(self.sty_current_start + delta, max_start))
            if new_start != self.sty_current_start:
                self.sty_current_start = new_start
                self.load_sty_data()
        else:
            delta = -1 if event.delta > 0 else 1
            max_start = max(0, self.aus_total_lines - self.aus_visible_lines)
            new_start = max(0, min(self.aus_current_start + delta, max_start))
            if new_start != self.aus_current_start:
                self.aus_current_start = new_start
                self.load_aus_data()

    def select_last_n_bytes(self, n_bytes):
        """Select the last N bytes of the data"""
        try:
            total_size = len(self.data)
            if total_size == 0:
                self.update_status("No data to select")
                return

            # Calculate start and end offsets
            end_offset = total_size - 1
            start_offset = max(0, end_offset - n_bytes + 1)

            # Update the range entry fields
            self.start_range.delete(0, tk.END)
            self.start_range.insert(0, f"{start_offset:08X}")
            self.end_range.delete(0, tk.END)
            self.end_range.insert(0, f"{end_offset:08X}")

            # Calculate the lines where these offsets appear
            start_line = (start_offset // 16) - self.current_start + 1
            end_line = (end_offset // 16) - self.current_start + 1

            # Calculate column positions
            start_col = 10 + (start_offset % 16) * 3
            end_col = 10 + (end_offset % 16) * 3 + 2

            # Ensure the end of the file is visible
            self.current_start = max(0, (end_offset // 16) - self.visible_lines + 2)
            self.load_visible_data()

            # Clear any existing selection
            self.hex_editor.tag_remove('sel', '1.0', 'end')

            # Add new selection
            start_line = (start_offset // 16) - self.current_start + 1
            end_line = (end_offset // 16) - self.current_start + 1
            self.hex_editor.tag_add('sel', f"{start_line}.{start_col}", f"{end_line}.{end_col}")
            self.hex_editor.see(f"{end_line}.0")

            # Update status
            self.update_status(f"Selected last {n_bytes} bytes (offset {start_offset:08X} to {end_offset:08X})")

        except Exception as e:
            self.update_status(f"Error selecting last {n_bytes} bytes: {str(e)}")

    def select_from_170_to_end(self):
        """Select data from offset 0x170 to the end of file"""
        try:
            # Set start offset to 0x170
            start_offset = 0x170
            # Set end offset to last byte
            end_offset = len(self.data) - 1

            # Update the range entry fields
            self.start_range.delete(0, tk.END)
            self.start_range.insert(0, f"{start_offset:08X}")
            self.end_range.delete(0, tk.END)
            self.end_range.insert(0, f"{end_offset:08X}")

            # Ensure the range is visible
            self.current_start = max(0, (start_offset // 16) - 2)  # Show 2 lines before selection
            self.load_visible_data()

            # Calculate the lines where these offsets appear
            start_line = (start_offset // 16) - self.current_start + 1
            end_line = (end_offset // 16) - self.current_start + 1

            # Calculate column positions
            start_col = 10 + (start_offset % 16) * 3
            end_col = 10 + (end_offset % 16) * 3 + 2

            # Clear any existing selection
            self.hex_editor.tag_remove('sel', '1.0', 'end')

            # Add new selection
            self.hex_editor.tag_add('sel', f"{start_line}.{start_col}", f"{end_line}.{end_col}")
            self.hex_editor.see(f"{start_line}.0")

            # Update status
            self.update_status(f"Selected range from {start_offset:08X} to {end_offset:08X}")

        except Exception as e:
            self.update_status(f"Error selecting range: {str(e)}")

class CombinedPreviewWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("STY and AUS Data Editor - Advanced Mode")
        
        # Set minimum window size
        self.window.minsize(1200, 800)
        
        # Set initial window size to 80% of screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Performance settings
        self.chunk_size = 1024 * 64  # 64KB chunks for better performance
        self.sty_current_start = 0
        self.aus_current_start = 0
        
        # Initialize data containers
        self.sty_data = bytearray()
        self.aus_data = bytes()
        self.sty_total_lines = 0
        self.aus_total_lines = 0
        self.sty_visible_lines = 0
        self.aus_visible_lines = 0

        # Split pane for STY and AUS data
        paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # STY Frame with toolbar
        sty_container = ttk.Frame(paned)
        paned.add(sty_container, weight=1)
        
        # STY Toolbar
        sty_toolbar = ttk.LabelFrame(sty_container, text="STY Editor Tools")
        sty_toolbar.pack(fill="x", padx=5, pady=2)
        
        # Range selection frame for STY
        sty_range_frame = ttk.Frame(sty_toolbar)
        sty_range_frame.pack(side="left", fill="x", padx=2)
        
        ttk.Label(sty_range_frame, text="Start:").pack(side="left")
        self.sty_start_offset = ttk.Entry(sty_range_frame, width=10)
        self.sty_start_offset.pack(side="left", padx=2)
        
        ttk.Label(sty_range_frame, text="End:").pack(side="left")
        self.sty_end_offset = ttk.Entry(sty_range_frame, width=10)
        self.sty_end_offset.pack(side="left", padx=2)
        
        ttk.Button(sty_range_frame, text="Select", 
                  command=lambda: self.select_hex_range(self.sty_editor, self.sty_start_offset, self.sty_end_offset)
                  ).pack(side="left", padx=2)
        
        # STY Edit buttons
        ttk.Button(sty_toolbar, text="Copy", 
                  command=lambda: self.copy_selection(self.sty_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(sty_toolbar, text="Cut",
                  command=lambda: self.cut_selection(self.sty_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(sty_toolbar, text="Paste",
                  command=lambda: self.paste_at_cursor(self.sty_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(sty_toolbar, text="Delete",
                  command=lambda: self.delete_selection(self.sty_editor)
                  ).pack(side="left", padx=2)
        
        # STY Editor container
        sty_editor_container = ttk.Frame(sty_container)
        sty_editor_container.pack(fill="both", expand=True)
        sty_editor_container.grid_rowconfigure(0, weight=1)
        sty_editor_container.grid_columnconfigure(0, weight=1)

        # Create STY editor with performance optimizations
        self.sty_editor = tk.Text(
            sty_editor_container,
            font=("Consolas", 10),
            wrap="none",
            blockcursor=True,
            maxundo=0,
            setgrid=True,
            height=1,
            width=1
        )
        self.sty_editor.grid(row=0, column=0, sticky="nsew")
        
        # STY Scrollbars
        self.sty_vsb = ttk.Scrollbar(sty_editor_container, orient="vertical", command=self.on_sty_scroll)
        self.sty_vsb.grid(row=0, column=1, sticky="ns")
        self.sty_hsb = ttk.Scrollbar(sty_editor_container, orient="horizontal", command=self.sty_editor.xview)
        self.sty_hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure STY scrolling
        self.sty_editor.config(
            yscrollcommand=self.update_sty_scrollbar,
            xscrollcommand=self.sty_hsb.set
        )

        # AUS Frame with toolbar
        aus_container = ttk.Frame(paned)
        paned.add(aus_container, weight=1)

        # AUS Toolbar
        aus_toolbar = ttk.LabelFrame(aus_container, text="AUS Editor Tools")
        aus_toolbar.pack(fill="x", padx=5, pady=2)

        # Range selection frame for AUS
        aus_range_frame = ttk.Frame(aus_toolbar)
        aus_range_frame.pack(side="left", fill="x", padx=2)
        
        ttk.Label(aus_range_frame, text="Start:").pack(side="left")
        self.aus_start_offset = ttk.Entry(aus_range_frame, width=10)
        self.aus_start_offset.pack(side="left", padx=2)
        
        ttk.Label(aus_range_frame, text="End:").pack(side="left")
        self.aus_end_offset = ttk.Entry(aus_range_frame, width=10)
        self.aus_end_offset.pack(side="left", padx=2)
        
        ttk.Button(aus_range_frame, text="Select",
                  command=lambda: self.select_hex_range(self.aus_editor, self.aus_start_offset, self.aus_end_offset)
                  ).pack(side="left", padx=2)
        
        # AUS Edit buttons
        ttk.Button(aus_toolbar, text="Copy",
                  command=lambda: self.copy_selection(self.aus_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(aus_toolbar, text="Cut",
                  command=lambda: self.cut_selection(self.aus_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(aus_toolbar, text="Paste",
                  command=lambda: self.paste_at_cursor(self.aus_editor)
                  ).pack(side="left", padx=2)
        ttk.Button(aus_toolbar, text="Delete",
                  command=lambda: self.delete_selection(self.aus_editor)
                  ).pack(side="left", padx=2)
        
        # AUS Editor container
        aus_editor_container = ttk.Frame(aus_container)
        aus_editor_container.pack(fill="both", expand=True)
        aus_editor_container.grid_rowconfigure(0, weight=1)
        aus_editor_container.grid_columnconfigure(0, weight=1)

        # Create AUS editor with performance optimizations
        self.aus_editor = tk.Text(
            aus_editor_container,
            font=("Consolas", 10),
            wrap="none",
            blockcursor=True,
            maxundo=0,
            setgrid=True,
            height=1,
            width=1
        )
        self.aus_editor.grid(row=0, column=0, sticky="nsew")
        
        # AUS Scrollbars
        self.aus_vsb = ttk.Scrollbar(aus_editor_container, orient="vertical", command=self.on_aus_scroll)
        self.aus_vsb.grid(row=0, column=1, sticky="ns")
        self.aus_hsb = ttk.Scrollbar(aus_editor_container, orient="horizontal", command=self.aus_editor.xview)
        self.aus_hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure AUS scrolling
        self.aus_editor.config(
            yscrollcommand=self.update_aus_scrollbar,
            xscrollcommand=self.aus_hsb.set
        )

        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief="sunken")
        status_bar.pack(fill="x", padx=5, pady=5)
        
        # Bottom button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="Replace STY Header with AUS", 
                  command=self.replace_sty_header_with_aus).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Apply and Close", 
                  command=self.apply_and_close).pack(side="right", padx=5)

        # Configure tags for better performance
        for editor in [self.sty_editor, self.aus_editor]:
            editor.tag_configure("sel", background="lightblue")
            editor.bind("<<Selection>>", self.on_selection_change)
            editor.bind("<Configure>", self.on_editor_resize)
            editor.bind("<MouseWheel>", self.on_mousewheel)
        
        # Initialize data and view
        self.sty_data = self.parent.sty_data if self.parent.sty_data else bytes()
        self.aus_data = self.parent.aus_data if self.parent.aus_data else bytes()
        
        self.sty_total_lines = (len(self.sty_data) + 15) // 16
        self.aus_total_lines = (len(self.aus_data) + 15) // 16
        
        # Calculate visible lines after window is shown
        self.window.update_idletasks()
        self.calculate_visible_lines()
        
        # Load initial data chunks
        self.load_sty_data()
        self.load_aus_data()

        # Update status with data sizes
        self.status_var.set(f"Loaded appended STY ({len(self.sty_data):,} bytes) and AUS ({len(self.aus_data):,} bytes)")
        
        # Log operation
        self.parent.log(f"Opened combined editor with appended STY ({len(self.sty_data):,} bytes) and AUS ({len(self.aus_data):,} bytes)")

    def load_sty_data(self):
        """Load and format STY data chunk with hex and ASCII"""
        try:
            self.sty_editor.delete(1.0, tk.END)
            
            # Calculate chunk boundaries
            start = self.sty_current_start * 16
            end = min(start + (self.sty_visible_lines * 16), len(self.sty_data))
            
            # Format and display data
            for i in range(start, end, 16):
                # Get current chunk
                chunk = self.sty_data[i:min(i+16, end)]
                
                # Format offset
                offset = f"{i:08X}"
                
                # Format hex values
                hex_values = " ".join(f"{b:02X}" for b in chunk)
                hex_values = f"{hex_values:<47}"  # Pad to fixed width
                
                # Format ASCII representation
                ascii_values = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                # Combine all parts
                line = f"{offset}  {hex_values}  {ascii_values}\n"
                self.sty_editor.insert(tk.END, line)
                
        except Exception as e:
            self.status_var.set(f"Error loading STY data: {str(e)}")

    def load_aus_data(self):
        """Load and format AUS data chunk with hex and ASCII"""
        try:
            self.aus_editor.delete(1.0, tk.END)
            
            # Calculate chunk boundaries
            start = self.aus_current_start * 16
            end = min(start + (self.aus_visible_lines * 16), len(self.aus_data))
            
            # Format and display data
            for i in range(start, end, 16):
                # Get current chunk
                chunk = self.aus_data[i:min(i+16, end)]
                
                # Format offset
                offset = f"{i:08X}"
                
                # Format hex values
                hex_values = " ".join(f"{b:02X}" for b in chunk)
                hex_values = f"{hex_values:<47}"  # Pad to fixed width
                
                # Format ASCII representation
                ascii_values = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                # Combine all parts
                line = f"{offset}  {hex_values}  {ascii_values}\n"
                self.aus_editor.insert(tk.END, line)
                
        except Exception as e:
            self.status_var.set(f"Error loading AUS data: {str(e)}")

    def on_sty_scroll(self, *args):
        """Handle STY scrollbar movement"""
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self.sty_total_lines - self.sty_visible_lines)
            new_start = int(fraction * self.sty_total_lines)
            new_start = max(0, min(new_start, max_start))
            if new_start != self.sty_current_start:
                self.sty_current_start = new_start
                self.load_sty_data()
        elif args[0] == "scroll":
            amount = int(args[1])
            if args[2] == "units":
                delta = amount
            else:  # pages
                delta = amount * self.sty_visible_lines
            
            max_start = max(0, self.sty_total_lines - self.sty_visible_lines)
            new_start = max(0, min(self.sty_current_start + delta, max_start))
            if new_start != self.sty_current_start:
                self.sty_current_start = new_start
                self.load_sty_data()
                
    def on_aus_scroll(self, *args):
        """Handle AUS scrollbar movement"""
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self.aus_total_lines - self.aus_visible_lines)
            new_start = int(fraction * self.aus_total_lines)
            new_start = max(0, min(new_start, max_start))
            if new_start != self.aus_current_start:
                self.aus_current_start = new_start
                self.load_aus_data()
        elif args[0] == "scroll":
            amount = int(args[1])
            if args[2] == "units":
                delta = amount
            else:  # pages
                delta = amount * self.aus_visible_lines
            
            max_start = max(0, self.aus_total_lines - self.aus_visible_lines)
            new_start = max(0, min(self.aus_current_start + delta, max_start))
            if new_start != self.aus_current_start:
                self.aus_current_start = new_start
                self.load_aus_data()
                
    def update_sty_scrollbar(self, *args):
        """Update STY scrollbar position"""
        if self.sty_total_lines > 0:
            first = self.sty_current_start / self.sty_total_lines
            last = min(1.0, (self.sty_current_start + self.sty_visible_lines) / self.sty_total_lines)
            self.sty_vsb.set(first, last)
            
    def update_aus_scrollbar(self, *args):
        """Update AUS scrollbar position"""
        if self.aus_total_lines > 0:
            first = self.aus_current_start / self.aus_total_lines
            last = min(1.0, (self.aus_current_start + self.aus_visible_lines) / self.aus_total_lines)
            self.aus_vsb.set(first, last)

    def copy_selection(self, editor):
        """Copy selected data with both hex and ASCII representation"""
        try:
            if editor.tag_ranges("sel"):
                selection = editor.get("sel.first", "sel.last")
                start_index = editor.index("sel.first")
                start_line, start_col = map(int, start_index.split('.'))
                
                # Determine if selection started in ASCII section
                is_ascii_selection = start_col >= 61
                
                lines = selection.strip().splitlines()
                hex_data = []
                ascii_data = []
                
                for line in lines:
                    if len(line) >= 61:  # Make sure line is long enough
                        if is_ascii_selection:
                            # Get ASCII part (after column 61)
                            ascii_part = line[61:77].rstrip()  # Limit to 16 chars
                            ascii_data.append(ascii_part)
                            # Convert ASCII to hex
                            hex_data.extend(ord(c) for c in ascii_part)
                        else:
                            # Get hex values (between offset and ASCII)
                            hex_values = line[10:57].split()
                            hex_data.extend(int(h, 16) for h in hex_values if h)
                            # Get corresponding ASCII
                            ascii_part = line[61:77].rstrip()  # Limit to 16 chars
                            ascii_data.append(ascii_part)
                
                # Store both hex and ASCII data
                self.parent.clipboard_data = {
                    'hex': bytes(hex_data),
                    'ascii': "".join(ascii_data)
                }
                self.status_var.set(f"Copied {len(hex_data)} bytes")
            else:
                self.status_var.set("No selection to copy")
        except Exception as e:
            self.status_var.set(f"Copy error: {str(e)}")

    def cut_selection(self, editor):
        """Cut selected hex data"""
        try:
            if editor.tag_ranges("sel"):
                selection = editor.get("sel.first", "sel.last")
                hex_data = self.extract_hex_data(selection)
                self.parent.clipboard_data = bytes.fromhex(hex_data)
                editor.delete("sel.first", "sel.last")
                self.status_var.set(f"Cut {len(self.parent.clipboard_data)} bytes")
            else:
                self.status_var.set("No selection to cut")
        except Exception as e:
            self.status_var.set(f"Cut error: {str(e)}")

    def paste_at_cursor(self, editor):
        """Paste data at cursor position with proper formatting"""
        try:
            if not self.parent.clipboard_data:
                self.status_var.set("No data to paste")
                return

            # Get cursor position
            cursor_pos = editor.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # Determine if we're in the ASCII section (col >= 61)
            is_ascii_section = col >= 61

            # If there's a selection, replace it
            if editor.tag_ranges("sel"):
                editor.delete("sel.first", "sel.last")

            # Get the data to paste
            paste_data = self.parent.clipboard_data
            
            # Handle different paste formats
            if isinstance(paste_data, dict):
                hex_bytes = paste_data['hex']
            elif isinstance(paste_data, (bytes, bytearray)):
                hex_bytes = paste_data
            else:
                self.status_var.set("Invalid clipboard data format")
                return

            # Calculate byte position based on cursor
            if is_ascii_section:
                byte_pos = min(15, col - 61)  # ASCII section starts at column 61
            else:
                byte_pos = min(15, (col - 10) // 3)  # Hex section starts at column 10

            # Process data line by line
            remaining_bytes = hex_bytes
            current_line = line
            current_byte_pos = byte_pos

            while remaining_bytes:
                # Get current line content
                try:
                    line_content = editor.get(f"{current_line}.0", f"{current_line}.end")
                except tk.TclError:
                    line_content = ""

                # Parse or create line components
                if line_content and len(line_content) >= 61:
                    try:
                        offset = int(line_content[:8], 16)
                        hex_values = line_content[10:57].split()
                        ascii_part = line_content[61:77]
                    except (ValueError, IndexError):
                        offset = (current_line - 1) * 16
                        hex_values = ["00"] * 16
                        ascii_part = "." * 16
                else:
                    offset = (current_line - 1) * 16
                    hex_values = ["00"] * 16
                    ascii_part = "." * 16

                # Convert components to lists for modification
                hex_list = hex_values if len(hex_values) == 16 else ["00"] * 16
                ascii_list = list(ascii_part.ljust(16, '.'))

                # Calculate how many bytes to process in this line
                bytes_in_line = min(16 - current_byte_pos, len(remaining_bytes))
                chunk = remaining_bytes[:bytes_in_line]
                remaining_bytes = remaining_bytes[bytes_in_line:]

                # Update hex and ASCII representations
                for i, b in enumerate(chunk):
                    pos = current_byte_pos + i
                    if pos < 16:
                        hex_list[pos] = f"{b:02X}"
                        ascii_list[pos] = chr(b) if 32 <= b <= 126 else '.'

                # Format the line with strict spacing
                hex_str = " ".join(hex_list)
                ascii_str = "".join(ascii_list)
                formatted_line = f"{offset:08X}  {hex_str:<47}  {ascii_str}"

                # Replace the entire line
                editor.delete(f"{current_line}.0", f"{current_line}.end")
                editor.insert(f"{current_line}.0", formatted_line)

                # Move to next line
                current_line += 1
                current_byte_pos = 0

            self.status_var.set(f"Pasted {len(hex_bytes)} bytes")
            
        except Exception as e:
            self.status_var.set(f"Paste error: {str(e)}")

    def extract_hex_data(self, text):
        """Extract hex values from text selection"""
        hex_data = []
        for line in text.strip().splitlines():
            parts = line.split()
            if len(parts) > 1:
                hex_values = parts[1:17]  # Get hex values between offset and ASCII
                hex_data.extend(hex_values)
        return "".join(hex_data)

    def on_selection_change(self, event=None):
        """Track selection changes and update status"""
        try:
            editor = self.window.focus_get()
            if not isinstance(editor, tk.Text):
                return

            if editor.tag_ranges("sel"):
                # Get selection indices
                start = editor.index("sel.first")
                end = editor.index("sel.last")
                
                # Convert text positions to line and column
                start_line, start_col = map(int, start.split('.'))
                end_line, end_col = map(int, end.split('.'))
                
                # Calculate byte offsets
                start_offset = (start_line - 1) * 16
                end_offset = (end_line - 1) * 16
                
                # Format offsets
                start_hex = self.format_hex_offset(start_offset)
                end_hex = self.format_hex_offset(end_offset)
                
                # Update status and range inputs
                self.status_var.set(f"Selection: {start_hex} to {end_hex}")
                
                # Update appropriate range inputs
                if editor == self.sty_editor:
                    self.sty_start_offset.delete(0, tk.END)
                    self.sty_start_offset.insert(0, start_hex)
                    self.sty_end_offset.delete(0, tk.END)
                    self.sty_end_offset.insert(0, end_hex)
                else:
                    self.aus_start_offset.delete(0, tk.END)
                    self.aus_start_offset.insert(0, start_hex)
                    self.aus_end_offset.delete(0, tk.END)
                    self.aus_end_offset.insert(0, end_hex)
            else:
                self.status_var.set("No selection")
        except Exception as e:
            self.status_var.set(f"Selection error: {str(e)}")

    def select_hex_range(self, editor, start_entry, end_entry):
        """Select hex range in specified editor"""
        try:
            start_hex = start_entry.get().strip().upper().replace('0X', '')
            end_hex = end_entry.get().strip().upper().replace('0X', '')
            
            # Convert hex to int
            start_offset = int(start_hex, 16)
            end_offset = int(end_hex, 16)
            
            # Calculate lines to select
            start_line = (start_offset // 16) + 1
            end_line = (end_offset // 16) + 1
            
            # Select the range
            editor.tag_remove('sel', '1.0', 'end')
            editor.tag_add('sel', f"{start_line}.0", f"{end_line}.0")
            editor.see(f"{start_line}.0")
            
            # Update status
            self.status_var.set(f"Selected range: {self.format_hex_offset(start_offset)} to {self.format_hex_offset(end_offset)}")
            
        except ValueError:
            self.status_var.set("Invalid hex value. Please enter valid hex numbers.")
        except Exception as e:
            self.status_var.set(f"Error selecting range: {str(e)}")

    def format_hex_offset(self, offset):
        """Format hex offset as 8 digits with leading zeros"""
        return f"{offset:08X}"

    def apply_and_close(self):
        """Apply changes and close the window"""
        try:
            # Get final STY data
            sty_content = self.sty_editor.get(1.0, tk.END)
            final_data = self.get_hex_data(sty_content)
            
            # Update parent's STY data
            self.parent.sty_data = final_data
            
            # Log success
            self.parent.log(f"Applied changes to STY data ({len(final_data):,} bytes)")
            
            # Close window
            self.window.destroy()
            
        except Exception as e:
            self.parent.log(f"Error applying changes: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply changes: {str(e)}")

    def get_hex_data(self, text):
        """Convert text content back to bytes with improved performance"""
        try:
            hex_data = []
            for line in text.strip().splitlines():
                parts = line.split()
                if len(parts) > 1:
                    # Get hex values between offset and ASCII (parts[1:17])
                    hex_values = ''.join(parts[1:17])
                    hex_data.append(hex_values.replace(" ", ""))
            
            return bytes.fromhex(''.join(hex_data))
            
        except Exception as e:
            self.parent.log(f"Error converting hex data: {str(e)}")
            raise

    def append_aus_to_sty(self):
        """Append the copied AUS data to STY"""
        if not self.aus_copied_data:
            messagebox.showerror("Error", "No AUS data to append. Please select and copy data from AUS file first.")
            return
        if not self.sty_data:
            messagebox.showerror("Error", "No STY data to append to. Please load STY file first.")
            return
            
        try:
            # Create new combined data
            new_data = self.sty_data + self.aus_copied_data
            
            # Update STY data
            self.sty_data = new_data
            
            # Log the operation
            self.log(f"Successfully appended {len(self.aus_copied_data)} bytes from AUS to STY data")
            self.log(f"New STY data size: {len(self.sty_data)} bytes")
            
            messagebox.showinfo("Success", f"Successfully appended {len(self.aus_copied_data)} bytes to STY data")
        except Exception as e:
            self.log(f"Error appending AUS data: {str(e)}")
            messagebox.showerror("Error", f"Failed to append AUS data: {str(e)}")

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        editor = event.widget
        if editor == self.sty_editor:
            delta = -1 if event.delta > 0 else 1
            max_start = max(0, self.sty_total_lines - self.sty_visible_lines)
            new_start = max(0, min(self.sty_current_start + delta, max_start))
            if new_start != self.sty_current_start:
                self.sty_current_start = new_start
                self.load_sty_data()
        else:
            delta = -1 if event.delta > 0 else 1
            max_start = max(0, self.aus_total_lines - self.aus_visible_lines)
            new_start = max(0, min(self.aus_current_start + delta, max_start))
            if new_start != self.aus_current_start:
                self.aus_current_start = new_start
                self.load_aus_data()

    def toggle_hex_mode(self):
        """Toggle between hex and ASCII paste modes"""
        if self.parent.clipboard_data and isinstance(self.parent.clipboard_data, dict):
            current_format = self.parent.clipboard_data.get('format', 'hex')
            self.parent.clipboard_data['format'] = 'ascii' if current_format == 'hex' else 'hex'
            self.status_var.set(f"Paste mode: {self.parent.clipboard_data['format'].upper()}")

    def save_changes(self):
        """Save changes to the parent's data"""
        try:
            self.parent.sty_data = bytes(self.sty_data)
            self.status_var.set("Changes saved successfully")
        except Exception as e:
            self.status_var.set(f"Error saving changes: {str(e)}")

    def reload_data(self):
        """Reload data from parent"""
        try:
            self.sty_data = bytearray(self.parent.sty_data if self.parent.sty_data else bytes())
            self.load_data()
            self.status_var.set("Data reloaded successfully")
        except Exception as e:
            self.status_var.set(f"Error reloading data: {str(e)}")

    def copy_selection(self, event=None):
        """Copy selected data to clipboard"""
        try:
            if not self.hex_editor.tag_ranges("sel"):
                return "break"
                
            selection = self.hex_editor.get("sel.first", "sel.last")
            start_index = self.hex_editor.index("sel.first")
            start_line, start_col = map(int, start_index.split('.'))
            
            # Determine if selection started in ASCII section
            is_ascii_selection = start_col >= 61
            
            lines = selection.strip().splitlines()
            hex_data = []
            ascii_data = []
            
            for line in lines:
                if len(line) >= 61:  # Make sure line is long enough
                    if is_ascii_selection:
                        # Get ASCII part (after column 61)
                        ascii_part = line[61:77].rstrip()
                        ascii_data.append(ascii_part)
                        # Convert ASCII to hex
                        hex_data.extend(ord(c) for c in ascii_part)
                    else:
                        # Get hex values (between offset and ASCII)
                        hex_values = line[10:57].split()
                        hex_data.extend(int(h, 16) for h in hex_values if h)
                        # Get corresponding ASCII
                        ascii_part = line[61:77].rstrip()
                        ascii_data.append(ascii_part)
            
            # Store both hex and ASCII data
            self.parent.clipboard_data = {
                'hex': bytes(hex_data),
                'ascii': "".join(ascii_data)
            }
            
            self.status_var.set(f"Copied {len(hex_data)} bytes")
            return "break"
        except Exception as e:
            self.status_var.set(f"Copy error: {str(e)}")
            return "break"

    def cut_selection(self, event=None):
        """Cut selected data"""
        if not self.hex_editor.tag_ranges("sel"):
            return "break"
            
        # First copy
        self.copy_selection()
        
        # Then delete
        self.hex_editor.delete("sel.first", "sel.last")
        
        return "break"

    def paste_at_cursor(self, event=None):
        """Paste data at cursor position"""
        try:
            if not self.parent.clipboard_data:
                return "break"

            # Get cursor position
            cursor_pos = self.hex_editor.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # Determine if we're in the ASCII section (col >= 61)
            is_ascii_section = col >= 61

            # If there's a selection, replace it
            if self.hex_editor.tag_ranges("sel"):
                self.hex_editor.delete("sel.first", "sel.last")

            # Get the data to paste
            paste_data = self.parent.clipboard_data
            
            # Handle different paste formats
            if isinstance(paste_data, dict):
                hex_bytes = paste_data['hex']
            elif isinstance(paste_data, (bytes, bytearray)):
                hex_bytes = paste_data
            else:
                self.status_var.set("Invalid clipboard data format")
                return "break"

            # Calculate byte position based on cursor
            if is_ascii_section:
                byte_pos = min(15, col - 61)  # ASCII section starts at column 61
            else:
                byte_pos = min(15, (col - 10) // 3)  # Hex section starts at column 10

            # Process data line by line
            remaining_bytes = hex_bytes
            current_line = line
            current_byte_pos = byte_pos

            while remaining_bytes:
                # Get current line content
                try:
                    line_content = self.hex_editor.get(f"{current_line}.0", f"{current_line}.end")
                except tk.TclError:
                    line_content = ""

                # Parse or create line components
                if line_content and len(line_content) >= 61:
                    try:
                        offset = int(line_content[:8], 16)
                        hex_values = line_content[10:57].split()
                        ascii_part = line_content[61:77]
                    except (ValueError, IndexError):
                        offset = (current_line - 1) * 16
                        hex_values = ["00"] * 16
                        ascii_part = "." * 16
                else:
                    offset = (current_line - 1) * 16
                    hex_values = ["00"] * 16
                    ascii_part = "." * 16

                # Convert components to lists for modification
                hex_list = hex_values if len(hex_values) == 16 else ["00"] * 16
                ascii_list = list(ascii_part.ljust(16, '.'))

                # Calculate how many bytes to process in this line
                bytes_in_line = min(16 - current_byte_pos, len(remaining_bytes))
                chunk = remaining_bytes[:bytes_in_line]
                remaining_bytes = remaining_bytes[bytes_in_line:]

                # Update hex and ASCII representations
                for i, b in enumerate(chunk):
                    pos = current_byte_pos + i
                    if pos < 16:
                        hex_list[pos] = f"{b:02X}"
                        ascii_list[pos] = chr(b) if 32 <= b <= 126 else '.'

                # Format the line with strict spacing
                hex_str = " ".join(hex_list)
                ascii_str = "".join(ascii_list)
                formatted_line = f"{offset:08X}  {hex_str:<47}  {ascii_str}"

                # Replace the entire line
                self.hex_editor.delete(f"{current_line}.0", f"{current_line}.end")
                self.hex_editor.insert(f"{current_line}.0", formatted_line)

                # Move to next line
                current_line += 1
                current_byte_pos = 0

            self.status_var.set(f"Pasted {len(hex_bytes)} bytes")
            return "break"
            
        except Exception as e:
            self.status_var.set(f"Paste error: {str(e)}")
            return "break"

    def show_replace_dialog(self):
        """Show replace dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Replace")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Find frame
        find_frame = ttk.LabelFrame(dialog, text="Find")
        find_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(find_frame, text="Find what:").pack(side="left", padx=5)
        find_entry = ttk.Entry(find_frame, width=40)
        find_entry.pack(side="left", padx=5)
        
        # Replace frame
        replace_frame = ttk.LabelFrame(dialog, text="Replace")
        replace_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(replace_frame, text="Replace with:").pack(side="left", padx=5)
        replace_entry = ttk.Entry(replace_frame, width=40)
        replace_entry.pack(side="left", padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(dialog, text="Options")
        options_frame.pack(fill="x", padx=5, pady=5)
        
        hex_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(options_frame, text="Hex", variable=hex_var, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(options_frame, text="Text", variable=hex_var, value=False).pack(side="left", padx=5)
        
        def replace():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            
            if hex_var.get():
                # Convert hex strings to bytes
                try:
                    find_bytes = bytes.fromhex(find_text.replace(" ", ""))
                    replace_bytes = bytes.fromhex(replace_text.replace(" ", ""))
                except ValueError:
                    messagebox.showerror("Error", "Invalid hex values")
                    return
            else:
                # Convert text to bytes
                find_bytes = find_text.encode('ascii', errors='ignore')
                replace_bytes = replace_text.encode('ascii', errors='ignore')
            
            # Search and replace in data
            pos = 0
            count = 0
            while True:
                pos = self.sty_data.find(find_bytes, pos)
                if pos < 0:
                    break
                    
                # Replace bytes
                self.sty_data[pos:pos + len(find_bytes)] = replace_bytes
                pos += len(replace_bytes)
                count += 1
            
            # Reload data display
            self.load_data()
            self.status_var.set(f"Replaced {count} occurrences")
            
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Replace All", command=replace).pack(side="right", padx=5)
        
        find_entry.focus_set()

    def on_click(self, event):
        """Handle mouse click events"""
        index = self.hex_editor.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split('.'))
        
        # Determine if click is in hex or ASCII section
        if col >= 61:
            # ASCII section
            self.is_hex_mode = False
            byte_pos = col - 61
        elif col >= 10 and col < 58:
            # Hex section
            self.is_hex_mode = True
            byte_pos = (col - 10) // 3
        else:
            # Clicked in offset area or between sections
            return "break"
            
        # Calculate absolute position
        abs_pos = ((line - 1) * self.bytes_per_line) + byte_pos
        
        # Update status
        self.update_status()
        
        # Allow normal processing
        return None

    def undo_change(self, event=None):
        """Undo last change"""
        try:
            self.hex_editor.edit_undo()
            self.status_var.set("Undo")
        except tk.TclError:
            self.status_var.set("Nothing to undo")
        return "break"

    def redo_change(self, event=None):
        """Redo last undone change"""
        try:
            self.hex_editor.edit_redo()
            self.status_var.set("Redo")
        except tk.TclError:
            self.status_var.set("Nothing to redo")
        return "break"

    def calculate_visible_lines(self):
        """Calculate visible lines for both editors"""
        font_height = self.sty_editor.tk.call("font", "metrics", self.sty_editor.cget("font"), "-linespace")
        sty_height = self.sty_editor.winfo_height()
        aus_height = self.aus_editor.winfo_height()
        
        self.sty_visible_lines = max(1, sty_height // font_height)
        self.aus_visible_lines = max(1, aus_height // font_height)
        
    def on_editor_resize(self, event):
        """Handle editor resize events"""
        self.calculate_visible_lines()
        if event.widget == self.sty_editor:
            self.load_sty_data()
        else:
            self.load_aus_data()
            
    def show_find_dialog(self):
        """Show find dialog for searching hex or text"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Find")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()

        # Search frame
        search_frame = ttk.Frame(dialog)
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Search for:").pack(side="left", padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.focus_set()

        # Options frame
        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill="x", padx=5, pady=5)

        search_type = tk.StringVar(value="hex")
        ttk.Radiobutton(options_frame, text="Hex", variable=search_type, value="hex").pack(side="left", padx=5)
        ttk.Radiobutton(options_frame, text="Text", variable=search_type, value="text").pack(side="left", padx=5)

        def find():
            search_text = search_var.get().strip()
            if not search_text:
                return

            editor = self.window.focus_get()
            if not isinstance(editor, tk.Text):
                editor = self.sty_editor  # Default to STY editor

            # Convert search text based on type
            try:
                if search_type.get() == "hex":
                    search_bytes = bytes.fromhex(search_text.replace(" ", ""))
                else:
                    search_bytes = search_text.encode('ascii', errors='ignore')

                # Remove previous highlights
                editor.tag_remove("found", "1.0", tk.END)

                # Search in visible text
                start_pos = "1.0"
                while True:
                    start_pos = editor.search(search_text, start_pos, tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    editor.tag_add("found", start_pos, end_pos)
                    editor.tag_config("found", background="yellow")
                    start_pos = end_pos

                editor.tag_raise("found")
                self.status_var.set(f"Found matches for: {search_text}")

            except ValueError:
                self.status_var.set("Invalid search value")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(button_frame, text="Find", command=find).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="right", padx=5)

        # Bind Enter key
        dialog.bind("<Return>", lambda e: find())

    def show_goto_dialog(self):
        """Show dialog for jumping to specific offset"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Go to Offset")
        dialog.geometry("300x120")
        dialog.transient(self.window)
        dialog.grab_set()

        # Input frame
        input_frame = ttk.Frame(dialog)
        input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(input_frame, text="Offset (hex):").pack(side="left", padx=5)
        offset_var = tk.StringVar()
        offset_entry = ttk.Entry(input_frame, textvariable=offset_var, width=20)
        offset_entry.pack(side="left", padx=5)
        offset_entry.focus_set()

        def goto():
            try:
                offset = int(offset_var.get().strip().replace("0x", ""), 16)
                editor = self.window.focus_get()
                if not isinstance(editor, tk.Text):
                    editor = self.sty_editor  # Default to STY editor

                # Calculate line and column
                line = (offset // 16) + 1
                col = 10 + (offset % 16) * 3  # Position in hex section

                # Ensure the line is visible
                editor.see(f"{line}.0")
                editor.mark_set(tk.INSERT, f"{line}.{col}")
                
                # Highlight the position
                editor.tag_remove("found", "1.0", tk.END)
                editor.tag_add("found", f"{line}.{col}", f"{line}.{col+2}")
                editor.tag_config("found", background="yellow")

                self.status_var.set(f"Moved to offset: {offset:08X}")
                dialog.destroy()

            except ValueError:
                self.status_var.set("Invalid offset value")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(button_frame, text="Go", command=goto).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)

        # Bind Enter key
        dialog.bind("<Return>", lambda e: goto())

    def show_replace_dialog(self):
        """Show dialog for find and replace operations"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Find and Replace")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()

        # Find frame
        find_frame = ttk.LabelFrame(dialog, text="Find")
        find_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(find_frame, text="Find what:").pack(side="left", padx=5)
        find_var = tk.StringVar()
        find_entry = ttk.Entry(find_frame, textvariable=find_var, width=40)
        find_entry.pack(side="left", padx=5)

        # Replace frame
        replace_frame = ttk.LabelFrame(dialog, text="Replace")
        replace_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(replace_frame, text="Replace with:").pack(side="left", padx=5)
        replace_var = tk.StringVar()
        replace_entry = ttk.Entry(replace_frame, textvariable=replace_var, width=40)
        replace_entry.pack(side="left", padx=5)

        # Options frame
        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill="x", padx=5, pady=5)

        replace_type = tk.StringVar(value="hex")
        ttk.Radiobutton(options_frame, text="Hex", variable=replace_type, value="hex").pack(side="left", padx=5)
        ttk.Radiobutton(options_frame, text="Text", variable=replace_type, value="text").pack(side="left", padx=5)

        def replace_all():
            find_text = find_var.get().strip()
            replace_text = replace_var.get().strip()
            if not find_text:
                return

            editor = self.window.focus_get()
            if not isinstance(editor, tk.Text):
                editor = self.sty_editor  # Default to STY editor

            try:
                # Convert search and replace text based on type
                if replace_type.get() == "hex":
                    find_bytes = bytes.fromhex(find_text.replace(" ", ""))
                    replace_bytes = bytes.fromhex(replace_text.replace(" ", ""))
                else:
                    find_bytes = find_text.encode('ascii', errors='ignore')
                    replace_bytes = replace_text.encode('ascii', errors='ignore')

                # Perform replacement
                content = editor.get("1.0", tk.END)
                new_content = content.replace(find_text, replace_text)
                
                if new_content != content:
                    editor.delete("1.0", tk.END)
                    editor.insert("1.0", new_content)
                    self.status_var.set(f"Replaced all occurrences of {find_text}")
                else:
                    self.status_var.set("No matches found")

            except ValueError:
                self.status_var.set("Invalid hex values")

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(button_frame, text="Replace All", command=replace_all).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side="right", padx=5)

        find_entry.focus_set()

    def delete_selection(self, editor):
        """Delete selected data while maintaining line structure and preventing overlaps"""
        try:
            if not editor.tag_ranges("sel"):
                self.status_var.set("No selection to delete")
                return

            # Get selection range
            sel_start = editor.index("sel.first")
            sel_end = editor.index("sel.last")
            start_line, start_col = map(int, sel_start.split('.'))
            end_line, end_col = map(int, sel_end.split('.'))

            # Process each line in the selection
            for line in range(start_line, end_line + 1):
                # Get current line content
                line_content = editor.get(f"{line}.0", f"{line}.end")
                if not line_content or len(line_content) < 8:  # Ensure minimum length for offset
                    continue

                # Parse line components
                try:
                    # Extract offset
                    offset = int(line_content[:8], 16)
                    
                    # Extract hex values (columns 10-57)
                    hex_part = line_content[10:58] if len(line_content) >= 58 else ""
                    hex_values = hex_part.split()
                    
                    # Ensure we have exactly 16 hex values
                    hex_values.extend(["00"] * (16 - len(hex_values)))
                    
                    # Extract ASCII part (columns 61-77)
                    ascii_part = line_content[61:77] if len(line_content) >= 77 else ""
                    ascii_list = list(ascii_part.ljust(16, '.'))
                    
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line {line}: {str(e)}")
                    continue

                # Calculate byte positions to delete based on selection
                if line == start_line and line == end_line:
                    # Single line selection
                    if start_col >= 61:  # ASCII section
                        start_byte = min(15, start_col - 61)
                        end_byte = min(16, end_col - 61)
                    else:  # Hex section
                        start_byte = min(15, (start_col - 10) // 3)
                        end_byte = min(16, (end_col - 10) // 3 + 1)
                elif line == start_line:
                    # First line of multi-line selection
                    if start_col >= 61:
                        start_byte = min(15, start_col - 61)
                    else:
                        start_byte = min(15, (start_col - 10) // 3)
                    end_byte = 16
                elif line == end_line:
                    # Last line of multi-line selection
                    start_byte = 0
                    if end_col >= 61:
                        end_byte = min(16, end_col - 61)
                    else:
                        end_byte = min(16, (end_col - 10) // 3 + 1)
                else:
                    # Middle lines - delete entire line
                    start_byte = 0
                    end_byte = 16

                # Ensure valid byte range
                start_byte = max(0, min(start_byte, 15))
                end_byte = max(start_byte + 1, min(end_byte, 16))

                # Replace selected bytes with zeros
                for i in range(start_byte, end_byte):
                    hex_values[i] = "00"
                    ascii_list[i] = "."

                # Format the line with strict spacing
                hex_str = " ".join(hex_values)
                ascii_str = "".join(ascii_list[:16])
                
                # Ensure proper spacing in the formatted line
                new_line = f"{offset:08X}  {hex_str:<47}  {ascii_str}"

                # Replace the line content
                editor.delete(f"{line}.0", f"{line}.end")
                editor.insert(f"{line}.0", new_line)

            self.status_var.set("Selection deleted")

        except Exception as e:
            self.status_var.set(f"Delete error: {str(e)}")
            print(f"Delete error details: {str(e)}")  # For debugging

    def paste_at_cursor(self, editor):
        """Paste data at cursor position with improved ASCII handling"""
        try:
            if not self.parent.clipboard_data:
                self.status_var.set("No data to paste")
                return

            # Get cursor position
            cursor_pos = editor.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # Determine if we're in the ASCII section (col >= 61)
            is_ascii_section = col >= 61

            # If there's a selection, replace it
            if editor.tag_ranges("sel"):
                editor.delete("sel.first", "sel.last")

            # Get the data to paste
            paste_data = self.parent.clipboard_data
            
            # Handle different paste formats
            if isinstance(paste_data, dict):
                hex_bytes = paste_data['hex']
            elif isinstance(paste_data, (bytes, bytearray)):
                hex_bytes = paste_data
            else:
                self.status_var.set("Invalid clipboard data format")
                return

            # Calculate byte position based on cursor
            if is_ascii_section:
                byte_pos = min(15, col - 61)  # ASCII section starts at column 61
            else:
                byte_pos = min(15, (col - 10) // 3)  # Hex section starts at column 10

            # Process data line by line
            remaining_bytes = hex_bytes
            current_line = line
            current_byte_pos = byte_pos

            while remaining_bytes:
                # Get current line content
                try:
                    line_content = editor.get(f"{current_line}.0", f"{current_line}.end")
                except tk.TclError:
                    line_content = ""

                # Parse or create line components
                if line_content and len(line_content) >= 61:
                    try:
                        offset = int(line_content[:8], 16)
                        hex_values = line_content[10:57].split()
                        ascii_part = line_content[61:77]
                    except (ValueError, IndexError):
                        offset = (current_line - 1) * 16
                        hex_values = ["00"] * 16
                        ascii_part = "." * 16
                else:
                    offset = (current_line - 1) * 16
                    hex_values = ["00"] * 16
                    ascii_part = "." * 16

                # Convert components to lists for modification
                hex_list = hex_values if len(hex_values) == 16 else ["00"] * 16
                ascii_list = list(ascii_part.ljust(16, '.'))

                # Calculate how many bytes to process in this line
                bytes_in_line = min(16 - current_byte_pos, len(remaining_bytes))
                chunk = remaining_bytes[:bytes_in_line]
                remaining_bytes = remaining_bytes[bytes_in_line:]

                # Update hex and ASCII representations
                for i, b in enumerate(chunk):
                    pos = current_byte_pos + i
                    if pos < 16:  # Ensure we don't spill over
                        hex_list[pos] = f"{b:02X}"
                        ascii_list[pos] = chr(b) if 32 <= b <= 126 else '.'

                # Format the line with strict spacing
                hex_str = " ".join(hex_list)
                ascii_str = "".join(ascii_list[:16])  # Limit ASCII to 16 characters
                formatted_line = f"{offset:08X}  {hex_str:<47}  {ascii_str}"

                # Replace the line
                editor.delete(f"{current_line}.0", f"{current_line}.end")
                editor.insert(f"{current_line}.0", formatted_line)

                # Move to next line
                current_line += 1
                current_byte_pos = 0

            self.status_var.set(f"Pasted {len(hex_bytes)} bytes")

        except Exception as e:
            self.status_var.set(f"Paste error: {str(e)}")

    def replace_sty_header_with_aus(self):
        """Replace the STY file structure with AUS file header"""
        try:
            # Get the AUS header (first 170 bytes)
            aus_header = self.aus_data[:170]
            
            # Get the STY data after the header (after 170 bytes)
            sty_data_after_header = self.sty_data[170:]
            
            # Combine AUS header with remaining STY data
            self.sty_data = bytearray(aus_header) + bytearray(sty_data_after_header)
            
            # Update the STY editor display
            self.sty_current_start = 0
            self.load_sty_data()
            
            # Update status
            self.status_var.set(f"Replaced STY header with AUS header. New STY size: {len(self.sty_data):,} bytes")
            self.parent.log("Successfully replaced STY header with AUS header")
            
        except Exception as e:
            self.parent.log(f"Error replacing STY header with AUS header: {str(e)}")
            messagebox.showerror("Error", f"Failed to replace STY header with AUS header: {str(e)}")

class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AUS to STY Converter")
        self.root.geometry("600x400")
        
        # Variables
        self.aus_path = tk.StringVar()
        self.sty_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.aus_data = None
        self.sty_data = None
        self.aus_copied_data = None
        self.clipboard_data = None
        
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Step 1: File Selection
        files_frame = ttk.LabelFrame(main_frame, text="Step 1: Select Files", padding=5)
        files_frame.pack(fill="x", pady=5)
        
        # AUS file
        ttk.Label(files_frame, text="AUS File:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(files_frame, textvariable=self.aus_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=self.browse_aus).grid(row=0, column=2, padx=5)
        ttk.Button(files_frame, text="Preview", command=self.preview_aus).grid(row=0, column=3, padx=5)
        
        # STY file
        ttk.Label(files_frame, text="STY File:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Entry(files_frame, textvariable=self.sty_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=self.browse_sty).grid(row=1, column=2, padx=5)
        
        # Output file
        ttk.Label(files_frame, text="Output:").grid(row=2, column=0, sticky="w", padx=5)
        ttk.Entry(files_frame, textvariable=self.output_path, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(files_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5)
        
        # Step 2-4: Data Operations
        ops_frame = ttk.LabelFrame(main_frame, text="Step 2-4: Data Operations", padding=5)
        ops_frame.pack(fill="x", pady=5)
        
        # Add Append button
        ttk.Button(ops_frame, text="Append AUS Data to STY", command=self.append_aus_to_sty).pack(fill="x", pady=2)
        ttk.Button(ops_frame, text="Open Combined Editor", command=self.open_combined_editor).pack(fill="x", pady=2)
        
        # Step 5: Export
        export_frame = ttk.LabelFrame(main_frame, text="Step 5: Export", padding=5)
        export_frame.pack(fill="x", pady=5)
        
        ttk.Button(export_frame, text="Export STY File", command=self.export_sty).pack(fill="x", pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=5)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, width=60)
        self.log_text.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def browse_aus(self):
        filepath = filedialog.askopenfilename(filetypes=[("AUS Files", "*.aus")])
        if filepath:
            self.aus_path.set(filepath)
            with open(filepath, 'rb') as f:
                self.aus_data = f.read()
            self.log(f"Loaded AUS file: {filepath}")
            
    def browse_sty(self):
        filepath = filedialog.askopenfilename(filetypes=[("STY Files", "*.sty")])
        if filepath:
            self.sty_path.set(filepath)
            with open(filepath, 'rb') as f:
                self.sty_data = f.read()
            self.log(f"Loaded STY file: {filepath}")
            
    def browse_output(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".sty", filetypes=[("STY Files", "*.sty")])
        if filepath:
            self.output_path.set(filepath)
            self.log(f"Set output file: {filepath}")
            
    def preview_aus(self):
        if not self.aus_data:
            messagebox.showerror("Error", "Please load an AUS file first")
            return
        AUSPreviewWindow(self, self.aus_data)
        
    def open_combined_editor(self):
        """Open combined editor with appended STY and AUS data"""
        if not self.aus_data:
            messagebox.showerror("Error", "Please load an AUS file first")
            return

        # Initialize STY data if needed
        if not self.sty_data:
            self.sty_data = bytes()
            self.log("Created new STY data buffer")

        # Create temporary appended data for editing
        appended_sty = bytearray(self.sty_data + self.aus_data)

        # Create the editor window
        editor = CombinedPreviewWindow(self)
        
        # Configure window for maximum visibility
        if sys.platform == "win32":
            editor.window.state('zoomed')  # Maximize on Windows
        else:
            editor.window.attributes('-zoomed', True)  # Maximize on Unix
            
        # Update editor data
        editor.sty_data = appended_sty  # Load appended STY data
        editor.aus_data = self.aus_data  # Load full AUS data for reference
        
        # Calculate total lines
        editor.sty_total_lines = (len(editor.sty_data) + 15) // 16
        editor.aus_total_lines = (len(editor.aus_data) + 15) // 16
        
        # Reset scroll positions
        editor.sty_current_start = 0
        editor.aus_current_start = 0
        
        # Force window to update before calculating visible lines
        editor.window.update_idletasks()
        
        # Calculate visible lines after window is shown
        editor.calculate_visible_lines()
        
        # Set up copy/paste bindings for both editors
        editor.sty_editor.bind('<Control-c>', lambda e: editor.copy_selection(editor.sty_editor))
        editor.sty_editor.bind('<Control-v>', lambda e: editor.paste_at_cursor(editor.sty_editor))
        editor.aus_editor.bind('<Control-c>', lambda e: editor.copy_selection(editor.aus_editor))
        editor.aus_editor.bind('<Control-v>', lambda e: editor.paste_at_cursor(editor.aus_editor))
        
        # Load initial data chunks with ASCII representation
        editor.load_sty_data()
        editor.load_aus_data()
        
        # Update status with data sizes
        editor.status_var.set(f"Loaded appended STY ({len(editor.sty_data):,} bytes) and AUS ({len(editor.aus_data):,} bytes)")
        
        # Log operation
        self.log(f"Opened combined editor with appended STY ({len(editor.sty_data):,} bytes) and AUS ({len(editor.aus_data):,} bytes)")

    def export_sty(self):
        if not self.sty_data:
            messagebox.showerror("Error", "No STY data to export")
            return
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output file")
            return
            
        try:
            with open(self.output_path.get(), 'wb') as f:
                f.write(self.sty_data)
            self.log(f"Successfully exported to {self.output_path.get()}")
            messagebox.showinfo("Success", "File exported successfully!")
        except Exception as e:
            self.log(f"Error exporting file: {str(e)}")
            messagebox.showerror("Error", f"Failed to export file: {str(e)}")

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def append_aus_to_sty(self):
        """Append the copied AUS data to STY"""
        if not self.aus_copied_data:
            messagebox.showerror("Error", "No AUS data to append. Please select and copy data from AUS file first.")
            return
        if not self.sty_data:
            messagebox.showerror("Error", "No STY data to append to. Please load STY file first.")
            return
            
        try:
            # Create new combined data
            new_data = self.sty_data + self.aus_copied_data
            
            # Update STY data
            self.sty_data = new_data
            
            # Log the operation
            self.log(f"Successfully appended {len(self.aus_copied_data)} bytes from AUS to STY data")
            self.log(f"New STY data size: {len(self.sty_data)} bytes")
            
            messagebox.showinfo("Success", f"Successfully appended {len(self.aus_copied_data)} bytes to STY data")
        except Exception as e:
            self.log(f"Error appending AUS data: {str(e)}")
            messagebox.showerror("Error", f"Failed to append AUS data: {str(e)}")

    def load_hex_file(self):
        """Load a hex file and convert it to binary"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Hex files", "*.hex"), ("All files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            # Read the hex file
            with open(file_path, 'r') as f:
                hex_data = f.read()
            
            # Convert hex to binary
            binary_data = bytearray()
            for line in hex_data.splitlines():
                if line.startswith(':'):
                    # Intel HEX format
                    line = line[1:]  # Remove ':'
                    byte_count = int(line[:2], 16)
                    address = int(line[2:6], 16)
                    record_type = int(line[6:8], 16)
                    data = line[8:8+byte_count*2]
                    
                    if record_type == 0:  # Data record
                        for i in range(0, len(data), 2):
                            byte = int(data[i:i+2], 16)
                            binary_data.append(byte)
                else:
                    # Plain hex format
                    parts = line.split()
                    for part in parts:
                        if len(part) == 2:
                            try:
                                byte = int(part, 16)
                                binary_data.append(byte)
                            except ValueError:
                                continue
            
            # Store the binary data
            self.hex_data = binary_data
            self.log(f"Successfully loaded hex file: {file_path}")
            self.log(f"File size: {len(binary_data)} bytes")
            
            # Show success message
            messagebox.showinfo("Success", f"Successfully loaded hex file: {file_path}")
            
        except Exception as e:
            self.log(f"Error loading hex file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load hex file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()