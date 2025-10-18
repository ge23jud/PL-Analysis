import numpy as np
import matplotlib.pyplot as plt

# Taken from Claude, might need optimization at some point
class Interactor():

    def __init__(self, xdata, ydata):
        """
        Initialize the plot window with data.

        Parameters
        ----------
        xdata : array-like
            X coordinates of the data
        ydata : array-like
            Y coordinates of the data
        """
        self.xdata = np.array(xdata)
        self.ydata = np.array(ydata)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.data_line, = self.ax.plot(self.xdata, self.ydata, 'b-', linewidth=2, label='Data')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        plt.show(block=False)
        plt.pause(1)  # Give window time to render

    def change_plot(self, xdata, ydata):
        """
        Replace the current data with new data.

        Parameters
        ----------
        xdata : array-like
            New X coordinates
        ydata : array-like
            New Y coordinates
        """
        self.xdata = np.array(xdata)
        self.ydata = np.array(ydata)
        self.data_line.set_xdata(self.xdata)
        self.data_line.set_ydata(self.ydata)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
        plt.pause(1)

    def set_limits(self, xlim=None, ylim=None):
        """
        Set the axis limits of the plot.

        Parameters
        ----------
        xlim : tuple or None, optional
            Tuple of (xmin, xmax) for x-axis limits. If None, x-limits are unchanged.
        ylim : tuple or None, optional
            Tuple of (ymin, ymax) for y-axis limits. If None, y-limits are unchanged.
        """
        if xlim is not None:
            self.ax.set_xlim(xlim)
        if ylim is not None:
            self.ax.set_ylim(ylim)
        self.fig.canvas.draw_idle()


    def kill(self):
        """Close the plot window entirely."""
        plt.close(self.fig)

    def select_x_values(self, title):
        """
        Allow user to select x-values by clicking on the existing plot.

        Parameters
        ----------
        title : str
            Title for the plot

        Returns
        -------
        numpy.ndarray
            Array of selected x-values

        Usage
        -----
        - Click to add a vertical line at any x position
        - Click and drag a line to move it
        - Press Enter to confirm selection
        """
        # Local state variables
        selected_x = []
        lines = []
        dragging = [None]
        drag_offset = [0]
        finished = [False]  # Flag to track when user presses Enter

        # Update title
        self.ax.set_title(f'{title}\nClick to add lines | Drag to move | Enter to confirm')
        self.fig.canvas.draw_idle()

        # Local event handler functions
        def on_click(event):
            """Handle mouse click events."""
            if event.inaxes != self.ax or event.button != 1:
                return

            x_click = event.xdata
            if x_click is None:
                return

            # Check if clicking near an existing line (within 2% of x-range)
            x_range = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
            tolerance = 0.02 * x_range

            for i, (line, x_val) in enumerate(zip(lines, selected_x)):
                if abs(x_click - x_val) < tolerance:
                    # Start dragging this line
                    dragging[0] = i
                    drag_offset[0] = x_click - x_val
                    line.set_color('orange')
                    line.set_linewidth(2.5)
                    self.fig.canvas.draw_idle()
                    return

            # No line nearby, create a new one
            line = self.ax.axvline(x=x_click, color='red', linestyle='--',
                                   linewidth=2, alpha=0.7)
            lines.append(line)
            selected_x.append(x_click)
            self.fig.canvas.draw_idle()

        def on_motion(event):
            """Handle mouse motion for dragging lines."""
            if dragging[0] is None or event.inaxes != self.ax:
                return

            x_new = event.xdata
            if x_new is None:
                return

            # Update line position
            x_new -= drag_offset[0]
            lines[dragging[0]].set_xdata([x_new, x_new])
            selected_x[dragging[0]] = x_new
            self.fig.canvas.draw_idle()

        def on_release(event):
            """Handle mouse button release."""
            if dragging[0] is not None:
                # Reset line appearance
                lines[dragging[0]].set_color('red')
                lines[dragging[0]].set_linewidth(2)
                dragging[0] = None
                self.fig.canvas.draw_idle()

        def on_key(event):
            """Handle key press events."""
            if event.key == 'enter':
                finished[0] = True

        # Connect event handlers
        cid_click = self.fig.canvas.mpl_connect('button_press_event', on_click)
        cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        cid_release = self.fig.canvas.mpl_connect('button_release_event', on_release)
        cid_key = self.fig.canvas.mpl_connect('key_press_event', on_key)

        # Wait for user to press Enter or close window
        while not finished[0] and plt.fignum_exists(self.fig.number):
            plt.pause(0.1)

        # Disconnect event handlers
        self.fig.canvas.mpl_disconnect(cid_click)
        self.fig.canvas.mpl_disconnect(cid_motion)
        self.fig.canvas.mpl_disconnect(cid_release)
        self.fig.canvas.mpl_disconnect(cid_key)

        # Remove the vertical lines
        for line in lines:
            line.remove()

        # Reset title
        self.ax.set_title('')
        self.fig.canvas.draw_idle()

        return np.array(sorted(selected_x))

    def select_x_span(self, title="Select X-Span"):
        """
        Allow user to select an x-span by clicking and dragging on the existing plot.

        Parameters
        ----------
        title : str
            Title for the plot

        Returns
        -------
        tuple
            (start_idx, end_idx) First and last indices of x-data within selected range,
            or (None, None) if no selection was made

        Usage
        -----
        - Click and drag to select a range
        - Press Enter to confirm selection
        """
        # Local state variables
        selection = {'x1': None, 'x2': None, 'active': False}
        span_line = [None]  # Use list for mutable reference
        legend_obj = [None]
        finished = [False]

        # Update title
        original_title = self.ax.get_title()
        self.ax.set_title(f'{title}\nClick and drag to select range | Enter to confirm')
        self.fig.canvas.draw_idle()

        # Local event handler functions
        def on_press(event):
            """Handle mouse press events."""
            if event.inaxes == self.ax and event.button == 1:  # Left mouse button
                selection['x1'] = event.xdata
                selection['active'] = True

        def on_motion(event):
            """Handle mouse motion for dragging."""
            if selection['active'] and event.inaxes == self.ax:
                selection['x2'] = event.xdata

                # Remove previous span visualization
                if span_line[0] is not None:
                    span_line[0].remove()
                if legend_obj[0] is not None:
                    legend_obj[0].remove()

                # Draw current selection
                x1, x2 = sorted([selection['x1'], selection['x2']])
                span_line[0] = self.ax.axvspan(x1, x2, alpha=0.3, color='red',
                                               label=f'Selected: [{x1:.3f}, {x2:.3f}]')
                legend_obj[0] = self.ax.legend()
                self.fig.canvas.draw_idle()

        def on_release(event):
            """Handle mouse button release."""
            if selection['active'] and event.inaxes == self.ax:
                selection['x2'] = event.xdata
                selection['active'] = False

        def on_key(event):
            """Handle key press events."""
            if event.key == 'enter':
                finished[0] = True

        # Connect event handlers
        cid_press = self.fig.canvas.mpl_connect('button_press_event', on_press)
        cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        cid_release = self.fig.canvas.mpl_connect('button_release_event', on_release)
        cid_key = self.fig.canvas.mpl_connect('key_press_event', on_key)

        # Wait for user to press Enter or close window
        while not finished[0] and plt.fignum_exists(self.fig.number):
            plt.pause(0.1)

        # Disconnect event handlers
        self.fig.canvas.mpl_disconnect(cid_press)
        self.fig.canvas.mpl_disconnect(cid_motion)
        self.fig.canvas.mpl_disconnect(cid_release)
        self.fig.canvas.mpl_disconnect(cid_key)

        # Remove the span visualization
        if span_line[0] is not None:
            span_line[0].remove()
        if legend_obj[0] is not None:
            legend_obj[0].remove()

        # Restore original legend
        self.ax.legend()

        # Reset title
        self.ax.set_title(original_title)
        self.fig.canvas.draw_idle()

        # Process selection
        if selection['x1'] is not None and selection['x2'] is not None:
            x_min, x_max = sorted([selection['x1'], selection['x2']])

            return x_min, x_max
        else:
            print("No selection made")
            return None, None