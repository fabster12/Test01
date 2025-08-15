from ai_booksmith.app import create_app, load_config

if __name__ == '__main__':
    """
    Main entry point for the application.
    Loads configuration and runs the Flask app.
    """
    config = load_config()
    app = create_app(config)
    app.run(debug=True, host='0.0.0.0', port=5003)
