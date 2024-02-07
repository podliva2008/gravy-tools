def _on_exception(exc):
    """Exceptions handling"""

    try:
        import traceback
        import sys
    except ImportError as e:
        # In case even standart libraries cannot be imported
        print('Ошибка при импорте. Установлена ли программа правильно?')
        print(e)
        print(exc)
    else:
        traceback.print_exception(exc)
    input('Для продолжения нажмите ENTER...')
    sys.exit(1)


try:
    import os
    import platformdirs

    # Checking Python version
    import sys
    if sys.version_info[:2] < (3, 10):
        raise Exception("Версия Python должна быть 3.10 или выше")
except Exception as e:
    _on_exception(e)


def main():
    try:
        # Initialising default paths
        config_dir = platformdirs.user_config_dir(
            'gravy-tools', 'podliva_2008'
            )
        os.environ.setdefault('CONFIG_DIR', config_dir)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        cache_dir = platformdirs.user_cache_dir(
            'gravy-tools', 'podliva_2008'
            )
        os.environ.setdefault('CACHE_DIR', cache_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        from app import start_app

    except Exception as e:
        _on_exception(e)
    else:
        try:
            # TODO: insert server startup on this line
            start_app()
        except Exception as e:
            _on_exception(e)

    sys.exit(0)  # Exit with error code 0 once finished without exceptions


if __name__ == '__main__':
    main()