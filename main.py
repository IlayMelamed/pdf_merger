#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Page Merger - A desktop application for merging PDF files.

This application allows users to:
1. Open and display a PDF file one page at a time
2. Navigate through the pages with previous/next buttons
3. Select a second PDF file to insert
4. Merge the second PDF after the currently displayed page
5. Save the final merged PDF to a new file
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pdf_viewer import PdfViewer
from pdf_merger import PdfMerger


class PdfMergerApp:
    """
    Main application class for the PDF Page Merger.

    Provides a GUI for interacting with the PDF viewer and merger functionality.
    """

    def __init__(self, root):
        """
        Initialize the application.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("PDF Page Merger")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Initialize PDF merger
        self.pdf_merger = PdfMerger()

        # Setup the UI
        self._setup_ui()

        # Bind window resize event
        self.root.bind("<Configure>", self._on_window_resize)

    def _setup_ui(self):
        """Set up the user interface components."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top button frame
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Open PDF button
        self.open_btn = ttk.Button(
            top_frame,
            text="Open Main PDF...",
            command=self._open_main_pdf
        )
        self.open_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Select PDF to insert button
        self.select_insert_btn = ttk.Button(
            top_frame,
            text="Select PDF to Insert...",
            command=self._select_insert_pdf
        )
        self.select_insert_btn.pack(side=tk.LEFT, padx=5)

        # Merge here button (initially disabled)
        self.merge_btn = ttk.Button(
            top_frame,
            text="Merge Here",
            command=self._merge_pdfs,
            state=tk.DISABLED
        )
        self.merge_btn.pack(side=tk.LEFT, padx=5)

        # Save as button (initially disabled)
        self.save_btn = ttk.Button(
            top_frame,
            text="Save As...",
            command=self._save_merged_pdf,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # PDF display frame
        display_frame = ttk.Frame(main_frame, borderwidth=2, relief=tk.GROOVE)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add scrollbars for the canvas
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for PDF display with scrollbars
        self.canvas = tk.Canvas(
            display_frame,
            bg="white",
            highlightthickness=0,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Connect scrollbars to canvas
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)

        # Bottom navigation frame
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        # Previous page button
        self.prev_btn = ttk.Button(
            nav_frame,
            text="Previous",
            command=self._prev_page,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT)

        # Page label
        self.page_label = ttk.Label(nav_frame, text="Page 0 of 0")
        self.page_label.pack(side=tk.LEFT, padx=20)

        # Next page button
        self.next_btn = ttk.Button(
            nav_frame,
            text="Next",
            command=self._next_page,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT)

        # Add separator
        ttk.Separator(nav_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        # Zoom control buttons
        zoom_frame = ttk.Frame(nav_frame)
        zoom_frame.pack(side=tk.LEFT, padx=5)

        # Zoom out button
        self.zoom_out_btn = ttk.Button(
            zoom_frame,
            text="🔍-",
            width=3,
            command=self._zoom_out,
            state=tk.DISABLED
        )
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)

        # Reset zoom button
        self.reset_zoom_btn = ttk.Button(
            zoom_frame,
            text="100%",
            width=5,
            command=self._reset_zoom,
            state=tk.DISABLED
        )
        self.reset_zoom_btn.pack(side=tk.LEFT, padx=2)

        # Zoom in button
        self.zoom_in_btn = ttk.Button(
            zoom_frame,
            text="🔍+",
            width=3,
            command=self._zoom_in,
            state=tk.DISABLED
        )
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready. Open a PDF to begin.")
        self.status_label.pack(side=tk.LEFT)

        # Selected insert PDF label
        self.insert_pdf_label = ttk.Label(status_frame, text="")
        self.insert_pdf_label.pack(side=tk.RIGHT)

        # Initialize PDF viewer
        self.pdf_viewer = PdfViewer(self.canvas, self.page_label)

    def _open_main_pdf(self):
        """Open and display the main PDF file."""
        file_path = filedialog.askopenfilename(
            title="Open Main PDF",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )

        if file_path:
            # Set the main PDF in the merger
            if self.pdf_merger.set_main_pdf(file_path=file_path):
                # Load the PDF in the viewer
                if self.pdf_viewer.load_pdf(file_path=file_path):
                    self._update_ui_state()
                    self.status_label.config(
                        text=f"Loaded: {os.path.basename(file_path)}"
                    )

    def _select_insert_pdf(self):
        """Select a PDF file to insert."""
        file_path = filedialog.askopenfilename(
            title="Select PDF to Insert",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )

        if file_path:
            if self.pdf_merger.set_insert_pdf(file_path):
                self._update_ui_state()
                self.insert_pdf_label.config(
                    text=f"Insert PDF: {os.path.basename(file_path)}"
                )

    def _merge_pdfs(self):
        """Merge the insert PDF after the current page of the main PDF."""
        current_page = self.pdf_viewer.get_current_page_index()

        # Perform the merge
        merged_bytes = self.pdf_merger.merge_after_page(current_page)

        if merged_bytes:
            try:
                # Reload the PDF viewer with the merged content
                if self.pdf_viewer.load_pdf(pdf_bytes=merged_bytes):
                    # Navigate to the first page of the inserted document,
                    # which is right after the page where we clicked "Merge Here"
                    self.pdf_viewer.display_page(current_page + 1)

                    # Update UI state
                    self._update_ui_state()
                    self.status_label.config(text="PDFs merged successfully. Showing first page of inserted document.")
                else:
                    self.status_label.config(text="Error: Failed to reload the merged PDF.")
            except Exception as e:
                import traceback
                print("Error reloading merged PDF:")
                print(traceback.format_exc())
                self.status_label.config(text=f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to display merged PDF: {str(e)}")
        else:
            self.status_label.config(text="Error: Merge operation failed.")

    def _save_merged_pdf(self):
        """Save the merged PDF to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )

        if file_path:
            if self.pdf_merger.save_to_file(file_path):
                self.status_label.config(
                    text=f"Saved merged PDF to: {os.path.basename(file_path)}"
                )

    def _next_page(self):
        """Navigate to the next page."""
        if self.pdf_viewer.next_page():
            self._update_ui_state()

    def _prev_page(self):
        """Navigate to the previous page."""
        if self.pdf_viewer.prev_page():
            self._update_ui_state()

    def _zoom_in(self):
        """Zoom in the PDF view."""
        if self.pdf_viewer.zoom_in():
            self._update_ui_state()

    def _zoom_out(self):
        """Zoom out the PDF view."""
        if self.pdf_viewer.zoom_out():
            self._update_ui_state()

    def _reset_zoom(self):
        """Reset the zoom level of the PDF view."""
        if self.pdf_viewer.reset_zoom():
            self._update_ui_state()

    def _update_ui_state(self):
        """Update the state of UI elements based on the current application state."""
        has_main_pdf = self.pdf_merger.has_main_pdf()
        has_insert_pdf = self.pdf_merger.has_insert_pdf()
        is_modified = self.pdf_merger.is_modified()
        current_page = self.pdf_viewer.get_current_page_index()
        total_pages = self.pdf_viewer.get_total_pages()

        # Update navigation buttons
        self.prev_btn.config(state=tk.NORMAL if has_main_pdf and current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if has_main_pdf and current_page < total_pages - 1 else tk.DISABLED)

        # Update merge button
        self.merge_btn.config(state=tk.NORMAL if has_main_pdf and has_insert_pdf else tk.DISABLED)

        # Update save button
        self.save_btn.config(state=tk.NORMAL if is_modified else tk.DISABLED)

        # Update zoom buttons
        self.zoom_in_btn.config(state=tk.NORMAL if has_main_pdf else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if has_main_pdf else tk.DISABLED)
        self.reset_zoom_btn.config(state=tk.NORMAL if has_main_pdf else tk.DISABLED)

    def _on_window_resize(self, event):
        """Handle window resize event."""
        # Only redraw if the event is for the root window and we have a loaded PDF
        if event.widget == self.root and self.pdf_merger.has_main_pdf():
            # Redisplay the current page to fit the new canvas size
            self.pdf_viewer.display_page(self.pdf_viewer.get_current_page_index())


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = PdfMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
