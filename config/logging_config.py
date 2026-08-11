import logging
import logging.handlers
import os


def setup_logging(app):
    """
    Configura o sistema de logging estruturado para a aplicação.

    Cria:
    - Logger para console (DEBUG em desenvolvimento, INFO em produção)
    - Logger para arquivo (todos os níveis)
    - Formato consistente com timestamp, nível, módulo e mensagem
    """

    # Criar diretório de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Nível baseado no ambiente
    log_level = logging.DEBUG if app.debug else logging.INFO

    # Formato de log estruturado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capturar tudo internamente

    # Handler para Console (apenas em desenvolvimento ou nivel INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Handler para arquivo - todos os logs
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Handler específico para erros
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Criar loggers específicos para módulos principais
    auth_logger = logging.getLogger('auth')
    study_logger = logging.getLogger('study')
    user_logger = logging.getLogger('user')
    validation_logger = logging.getLogger('validation')
    service_logger = logging.getLogger('service')

    app.logger.info(f"Sistema de logging iniciado - Nível: {logging.getLevelName(log_level)}")

    return {
        'auth': auth_logger,
        'study': study_logger,
        'user': user_logger,
        'validation': validation_logger,
        'service': service_logger,
    }


def get_logger(name):
    """Função helper para obter logger por nome"""
    return logging.getLogger(name)