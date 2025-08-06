import numpy as np
import matplotlib.pyplot as plt

# Taken from Claude, might need optimization at some point
class SpanSelector():

    def select_x_span(self, xdata, ydata, title="Select X-Span"):
        """
        Plot x,y data and allow interactive selection of x-span.

        Parameters:
        xdata (np-array)
        ydata (np-array)
        title (str): Text to display on the prompt

        Returns:
        tuple : (start_idx, end_idx) First and last indices of x-data within selected range
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(xdata, ydata, 'b-', linewidth=1)
        ax.set_title(f"{title}\nClick and drag to select range, then press Enter or close plot")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.grid(True, alpha=0.3)

        # Variables to store selection
        selection = {'x1': None, 'x2': None, 'active': False}
        span_line = None

        def on_press(event):
            if event.inaxes == ax and event.button == 1:  # Left mouse button
                selection['x1'] = event.xdata
                selection['active'] = True

        def on_motion(event):
            nonlocal span_line
            if selection['active'] and event.inaxes == ax:
                selection['x2'] = event.xdata

                # Remove previous span visualization
                if span_line is not None:
                    span_line.remove()

                # Draw current selection
                x1, x2 = sorted([selection['x1'], selection['x2']])
                span_line = ax.axvspan(x1, x2, alpha=0.3, color='red',
                                       label=f'Selected: [{x1:.3f}, {x2:.3f}]')
                ax.legend()
                fig.canvas.draw()

        def on_release(event):
            if selection['active'] and event.inaxes == ax:
                selection['x2'] = event.xdata
                selection['active'] = False

        def on_key(event):
            if event.key == 'enter':
                plt.close(fig)

        # Connect event handlers
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('key_press_event', on_key)

        plt.show()

        # Process selection
        if selection['x1'] is not None and selection['x2'] is not None:
            x_min, x_max = sorted([selection['x1'], selection['x2']])

            # Find indices
            start_idx = np.argmax(xdata >= x_min)
            end_idx = len(xdata) - 1 - np.argmax(xdata[::-1] <= x_max)

            print(f"Selected range: [{x_min:.3f}, {x_max:.3f}]")
            print(f"Indices: [{start_idx}, {end_idx}]")
            print(f"Data points in range: {end_idx - start_idx + 1}")

            return start_idx, end_idx
        else:
            print("No selection made")
            return None, None
