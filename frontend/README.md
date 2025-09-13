# Frontend Project Documentation

## Overview
This project is a full-stack application that features a modern user interface for managing and displaying properties in Georgia. It includes a chatbot system that allows users to query property information and fetch address details, along with a property gallery to showcase all available properties.

## Features
- **Chatbot System**: 
  - **Query Mode**: Users can ask questions about properties, and the chatbot will generate SQL queries to fetch relevant data.
  - **Address Details Mode**: Users can input an address to retrieve detailed information about specific properties.

- **Property Gallery**: A visually appealing gallery that displays all properties with essential details, allowing users to browse through available listings.

## Project Structure
The project is organized into several directories and files, each serving a specific purpose:

- **public/**: Contains static files such as the main HTML file and favicon.
- **src/**: The main source code directory, which includes:
  - **components/**: Reusable components for the chatbot, property gallery, layout, and UI elements.
  - **pages/**: Different pages of the application, including the dashboard and chat interface.
  - **services/**: Functions for API calls and handling data.
  - **hooks/**: Custom hooks for managing state and side effects.
  - **utils/**: Utility functions for formatting and other helper tasks.
  - **styles/**: CSS files for global and component-specific styles.
  - **App.jsx**: The main application component that sets up routing and layout.
  - **index.js**: The entry point for the React application.

## Installation
To set up the project locally, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the frontend directory:
   ```
   cd frontend
   ```

3. Install the dependencies:
   ```
   npm install
   ```

4. Start the development server:
   ```
   npm start
   ```

## Usage
Once the application is running, you can interact with the chatbot to ask questions about properties or fetch details by entering an address. The property gallery will display all available properties, allowing for easy browsing.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.