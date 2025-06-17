#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Viewer Module - Handles loading and displaying PDF documents.
"""

import io
import tkinter as tk
from tkinter import messagebox

# Modified import for compatibility with installed PyMuPDF version
try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:
    # Try alternative import for older versions
    from PyMuPDF import fitz


class PdfViewer:
    """
    PdfViewer class for loading and displaying PDF documents.

    Provides functionality to:
    - Load PDF from file path or bytes
    - Render PDF pages as images on a canvas
    - Navigate through pages with previous/next functionality
    - Zoom in/out and scroll through the PDF page
    """

    def __init__(self, canvas, page_label):
        """
        Initialize the PDF viewer.

        Args:
            canvas (tk.Canvas): The canvas widget to render PDF pages on.
            page_label (tk.Label): The label widget to display page information.
        """
        self.canvas = canvas
        self.page_label = page_label
        self.doc = None
        self.current_page_idx = 0
        self.total_pages = 0
        self.img_id = None
        self.tk_image = None

        # Add zoom level and scrolling support
        self.zoom_level = 1.0  # Default zoom level
        self.min_zoom = 0.5    # Minimum zoom level
        self.max_zoom = 5.0    # Maximum zoom level
        self.zoom_step = 0.25  # Zoom step for each zoom in/out action

        # Add scrolling support
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)    # Linux scroll down

        # For tracking mouse movement for scrolling
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_drag_x = 0
        self.last_drag_y = 0

    def load_pdf(self, file_path=None, pdf_bytes=None):
        """
        Load a PDF document from a file path or bytes.

        Args:
            file_path (str, optional): Path to PDF file.
            pdf_bytes (bytes, optional): PDF content as bytes.

        Returns:
            bool: True if PDF was loaded successfully, False otherwise.
        """
        try:
            # Close any open document
            if self.doc:
                self.doc.close()

            # Load the new document
            if file_path:
                self.doc = fitz.open(file_path)
            elif pdf_bytes:
                # Create a memory stream that won't be closed prematurely
                stream = io.BytesIO(pdf_bytes)
                self.doc = fitz.open(stream=stream, filetype="pdf")
            else:
                messagebox.showerror("Error", "No PDF source provided.")
                return False

            # Set initial state
            self.current_page_idx = 0
            self.total_pages = len(self.doc)

            # Display the first page
            if self.total_pages > 0:
                self.display_page(0)
                return True
            else:
                messagebox.showerror("Error", "The PDF file contains no pages.")
                return False

        except Exception as e:
            import traceback
            print("Error loading PDF:")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            return False

    def display_page(self, page_idx):
        """
        Display a specific page of the PDF document.

        Args:
            page_idx (int): Index of the page to display.

        Returns:
            bool: True if page was displayed successfully, False otherwise.
        """
        if not self.doc or page_idx < 0 or page_idx >= self.total_pages:
            return False

        try:
            # Update current page index
            self.current_page_idx = page_idx

            # Get the page
            page = self.doc[page_idx]

            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Ensure the canvas has a reasonable size
            if canvas_width < 50 or canvas_height < 50:
                canvas_width = 800
                canvas_height = 600

            # Clear the canvas
            self.canvas.delete("all")

            # Set background color
            self.canvas.config(bg="#f0f0f0")

            # Calculate base zoom to fit the page
            page_rect = page.rect
            width_ratio = (canvas_width - 60) / page_rect.width
            height_ratio = (canvas_height - 60) / page_rect.height
            base_zoom = min(width_ratio, height_ratio)

            # Apply user zoom level
            zoom_factor = base_zoom * self.zoom_level

            # Create transformation matrix with improved quality
            mat = fitz.Matrix(zoom_factor, zoom_factor)

            # Render page to pixmap - explicitly without alpha to avoid errors
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert to PhotoImage format
            try:
                img_data = pix.tobytes("ppm")
                self.tk_image = tk.PhotoImage(data=img_data)
            except Exception as e:
                print(f"Error creating image: {str(e)}")
                # Try alternative approach
                try:
                    from PIL import Image, ImageTk
                    import tempfile

                    # Save pixmap to a temporary PNG file
                    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    temp_filename = temp_file.name
                    temp_file.close()

                    pix.save(temp_filename)

                    # Open with PIL and convert to Tkinter PhotoImage
                    pil_img = Image.open(temp_filename)
                    self.tk_image = ImageTk.PhotoImage(pil_img)

                    # Clean up the temp file
                    try:
                        import os
                        os.unlink(temp_filename)
                    except:
                        pass
                except Exception as e2:
                    print(f"Alternative image creation also failed: {str(e2)}")
                    raise e  # Re-raise the original error if the alternative also fails

            # Calculate centering coordinates
            x = max(0, (canvas_width - self.tk_image.width()) // 2)
            y = max(0, (canvas_height - self.tk_image.height()) // 2)

            # Create a frame in the canvas that's the size of the zoomed image
            self.canvas.config(scrollregion=(0, 0,
                               max(canvas_width, self.tk_image.width() + 20),
                               max(canvas_height, self.tk_image.height() + 20)))

            # Display the image
            self.img_id = self.canvas.create_image(
                x, y,
                anchor=tk.NW,
                image=self.tk_image
            )

            # Add a simple border
            self.canvas.create_rectangle(
                x - 1, y - 1,
                x + self.tk_image.width() + 1,
                y + self.tk_image.height() + 1,
                outline="#000000",
                width=1
            )

            # Update zoom info in page label
            self.update_page_label()

            # Reset the cursor when a new page is displayed
            self.canvas.config(cursor="arrow")

            return True

        except Exception as e:
            import traceback
            print("Error displaying page:")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
            return False

    def update_page_label(self):
        """Update the page label to show current page and total pages."""
        if self.doc:
            self.page_label.config(text=f"Page {self.current_page_idx + 1} of {self.total_pages}")

    def next_page(self):
        """
        Navigate to the next page.

        Returns:
            bool: True if navigation was successful, False otherwise.
        """
        if self.doc and self.current_page_idx < self.total_pages - 1:
            return self.display_page(self.current_page_idx + 1)
        return False

    def prev_page(self):
        """
        Navigate to the previous page.

        Returns:
            bool: True if navigation was successful, False otherwise.
        """
        if self.doc and self.current_page_idx > 0:
            return self.display_page(self.current_page_idx - 1)
        return False

    def get_current_page_index(self):
        """
        Get the current page index.

        Returns:
            int: Current page index (0-based).
        """
        return self.current_page_idx

    def get_total_pages(self):
        """
        Get the total number of pages in the document.

        Returns:
            int: Total number of pages.
        """
        return self.total_pages

    def close(self):
        """Close the document and release resources."""
        if self.doc:
            self.doc.close()
            self.doc = None

    def zoom_in(self):
        """Increase the zoom level and redisplay the current page."""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_step)
            return self.display_page(self.current_page_idx)
        return False

    def zoom_out(self):
        """Decrease the zoom level and redisplay the current page."""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_step)
            return self.display_page(self.current_page_idx)
        return False

    def reset_zoom(self):
        """Reset zoom to the default level."""
        self.zoom_level = 1.0
        return self.display_page(self.current_page_idx)

    def _on_mouse_down(self, event):
        """Handle mouse button press for scrolling."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.last_drag_x = event.x
        self.last_drag_y = event.y
        self.canvas.config(cursor="fleur")  # Change cursor to indicate drag mode

    def _on_mouse_drag(self, event):
        """Handle mouse drag for scrolling."""
        if self.zoom_level > 1.0:  # Only enable scrolling when zoomed in
            # Calculate movement delta
            delta_x = event.x - self.last_drag_x
            delta_y = event.y - self.last_drag_y

            # Scroll the canvas
            self.canvas.xview_scroll(-delta_x, "units")
            self.canvas.yview_scroll(-delta_y, "units")

            # Update last position
            self.last_drag_x = event.x
            self.last_drag_y = event.y

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming."""
        # Detect direction of scroll
        if event.num == 5 or event.delta < 0:
            self.zoom_out()  # Scroll down = zoom out
        elif event.num == 4 or event.delta > 0:
            self.zoom_in()   # Scroll up = zoom in

