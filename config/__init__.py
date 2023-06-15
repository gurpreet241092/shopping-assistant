import os


def load_config(env=os.environ.get('FLASK_ENV')):
    """Load config."""
    try:
        if env == 'prod':
            from .production import ProductionConfig
            return ProductionConfig
        elif env == 'staging':
            from .staging import StagingConfig
            return StagingConfig
        else:
            from .default import Config
            return Config
    except ImportError:
        from .default import Config
        return Config
