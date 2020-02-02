log_config = {
    'version': 1,    
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': { 
        # never ever touch the root logger until youn know exactly the implications
        # (here pypyr uses it to manage per-pipeline logs)
        # '': {  # root logger
        #     'handlers': ['default'],
        #     'level': 'INFO',
        #     'propagate': False
        # },
        'pyrsched': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'apscheduler': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False            
        },
        # 'pypyr': {
        #     'handlers': ['default'],
        #     'level': 'DEBUG',
        #     'propagate': False            
        # },
    } 
}