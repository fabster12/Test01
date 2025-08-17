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
    config['ssl_cert_file'] = os.environ.get(
        'SSL_CERT_FILE',
        config.get('ssl_cert_file')
    )

    ssl_cert_file = config['ssl_cert_file']
    if ssl_cert_file:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"file_dir {file_dir}")
        # If absolute, keep it. If relative, resolve against file_dir
        if os.path.isabs(ssl_cert_file):
            print(f"ABSOLUTEfile_dir")
            fullpath = ssl_cert_file
        else:
            print(f"not ABSOLUTEfile_dir")
            print(f"file_dir {file_dir}")
            print(f"ssl_cert_file {ssl_cert_file}")
            fullpath = os.path.abspath(os.path.join(file_dir, ssl_cert_file))
            print(f"fullpath {fullpath}")

        # Update config and environment variable
        config['ssl_cert_file'] = fullpath
        os.environ['SSL_CERT_FILE'] = fullpath

        print("ssl_cert_file normalized to:", fullpath)
        print("SSL CERT:", os.environ['SSL_CERT_FILE'])

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

