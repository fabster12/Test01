import os
import yaml
from flask import current_app, g

def load_config():
    """
    Loads configuration from config.yaml, models.yaml, and environment variables.
    Environment variables have the highest priority.
    """
    # Base config from file
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Load models config
    with open('models.yaml', 'r') as f:
        model_config = yaml.safe_load(f)
    config['models'] = model_config

    # Override with environment variables
    config['openai_api_key'] = os.environ.get('OPENAI_API_KEY', config.get('openai_api_key'))
    config['leonardo_api_key'] = os.environ.get('LEONARDO_API_KEY', config.get('leonardo_api_key'))
    config['flask_secret_key'] = os.environ.get('FLASK_SECRET_KEY', config.get('flask_secret_key'))
    config['active_openai_model'] = os.environ.get('ACTIVE_OPENAI_MODEL', config.get('active_openai_model'))
    config['active_leonardo_model'] = os.environ.get('ACTIVE_LEONARDO_MODEL', config.get('active_leonardo_model'))
    config['generated_books_dir'] = os.environ.get('GENERATED_BOOKS_DIR', config.get('generated_books_dir', 'generated_books'))
    config['ssl_cert_file'] = os.environ.get('SSL_CERT_FILE', config.get('ssl_cert_file'))

    return config

def init_config(app):
    with app.app_context():
        if 'config' not in g:
            g.config = load_config()

def get_config():
    return g.config

def get_model_config():
    return get_config().get('models', {})

def get_available_models(provider):
    """Returns a list of available models for a given provider (e.g., 'openai')."""
    model_config = get_model_config()
    return model_config.get(provider, [])

def set_active_model(provider, model_name):
    """Sets the active model for a given provider."""
    config = get_config()
    if provider == 'openai':
        config['active_openai_model'] = model_name
    elif provider == 'leonardo':
        config['active_leonardo_model'] = model_name
