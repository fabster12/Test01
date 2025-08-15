from ai_booksmith.app import create_app

if __name__ == '__main__':
    """
    Main entry point for the application.
    Loads configuration and runs the Flask app.
    """
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5003)
