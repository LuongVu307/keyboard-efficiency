import matplotlib.pyplot as plt
import numpy as np

def draw_and_save_line_graph(x, y, output_image_path):
    """
    Draws a line graph of the provided x and y data and saves it as an image file.
    
    Parameters:
    - x: Data for the x-axis.
    - y: Data for the y-axis.
    - output_image_path: Path where the output image will be saved.
    """
    # Create the line plot
    plt.plot(x, y, linestyle='-', color='b', label='Line')
    
    # Add titles and labels
    plt.title('Line Graph')
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.legend()
    
    # Save the plot to an image file
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()  # Close the figure to free up memory

    print(f"Line graph saved as {output_image_path}")

# Example usage
x = np.linspace(0, 10, 100)  # Generate 100 points from 0 to 10
y = np.sin(x)  # Compute the sine of these points
output_image_path = 'line_graph.png'

draw_and_save_line_graph(x, y, output_image_path)
