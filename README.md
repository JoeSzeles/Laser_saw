Laser Drawing and Engraving Application

Description:

The Laser Drawing and Engraving Application is a versatile tool designed to facilitate the creation and engraving of shapes and designs using a laser engraver. Built with Python and Tkinter, this application provides a user-friendly interface for drawing shapes, saving them as G-code files, and engraving them onto various materials.

Features:

    Drawing Shapes: Users can draw basic shapes such as rectangles and circles directly on the canvas using the left mouse button. The application supports dynamic resizing of shapes by dragging the mouse.

    Engraving: Once shapes are drawn, users can engrave them onto materials using a connected laser engraver. The application generates G-code files containing the necessary commands for precise engraving.

    Customization: Users can customize engraving parameters such as speed and power directly within the application. This allows for fine-tuning of the engraving process based on material properties and desired results.

    Material and Machine Setup: The application provides options for setting up machine dimensions and material dimensions, ensuring accurate placement and sizing of designs on the canvas.

    Save and Load: Users can save their designs as G-code files for future use or share them with others. Additionally, the application supports loading existing G-code files for engraving.

Usage:

    Setting up Machine and Material Dimensions: Specify the dimensions of the engraving machine and the material to be engraved on using the input fields provided.

    Drawing Shapes: Choose the desired shape (rectangle or circle) from the toolbar and click and drag on the canvas to draw the shape. Release the mouse button to finalize the shape.

    Engraving: After drawing shapes, configure engraving parameters such as speed and power. Click the "Engrave" button to send the design to the laser engraver for engraving.

    Saving and Loading: Use the "Save G-code" button to save the design as a G-code file. To engrave an existing design, click the "Cut" button and select the desired G-code file.

    Additional Functions: The application includes buttons for homing the laser, setting zero coordinates, and clearing the canvas for convenience.

Requirements:

    Python 3.x
    Tkinter
    PySerial
