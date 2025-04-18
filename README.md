# SNotesApp: Streamlit-powered Note-Taking Application

A flexible and intuitive note-taking application built with Streamlit that supports both text and image content. Create, edit, save, and export your notes with ease!

## Features

- **Rich Content Support**: Create notes with both text (Markdown) and image blocks
- **Drawing Canvas**: Built-in drawing functionality for creating sketches and diagrams
- **Edit Mode**: Toggle between viewing and editing modes for a distraction-free experience
- **Markdown Support**: Format your notes with Markdown syntax
- **File Management**: Save, open, and create new note files with ease
- **PDF Export**: Export your notes to PDF format for sharing or printing
- **Block Operations**: Add, edit, and delete blocks with simple controls

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/snotesapp.git
   cd snotesapp
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run snotesapp.py
   ```

2. The app will open in your default web browser at `http://localhost:8501`

3. Basic workflow:
   - Create a new note or open an existing one using the sidebar controls
   - Add text or image blocks using the "Add new block" button
   - Toggle "Edit mode" in the sidebar to switch between viewing and editing
   - Save your notes using the save button in the sidebar

## Project Structure

- `snotesapp.py`: Main application file
- `scanvas.py`: Drawing canvas functionality
- `sprinting.py`: PDF export functionality
- `template.typ`: Template for PDF export
- `data/`: Directory for storing note files
- `cache/`: Temporary files for PDF generation

## Configuration

Change the settings in the `secrets.toml` file.

## Contributing

Contributions are welcome! Here's how you can help improve SNotesApp:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please make sure to follow the code style of the project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

Future improvements planned for SNotesApp:

- Cloud storage integration (Dropbox API)
- Block reordering functionality
- Undo/redo functionality
- Periodic auto-save and backup
- Improved PDF export with customizable templates
- File management interface for renaming and deleting notes
