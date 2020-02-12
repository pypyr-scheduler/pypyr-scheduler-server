import logging

apscheduler = {
    'apscheduler.jobstores.default': {
        'type': 'memory',
        # 'url': 'sqlite:///jobs.sqlite'
    },
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '20'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC',
}

pypyr = {
    'pipelines.base_path': 'pipelines',
    'pipelines.log_path': 'logs',
    'pipelines.log_level': logging.INFO,
    'server_port': 12345,
}

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
            'stream': 'ext://sys.stdout', 
        },        
    },
    'loggers': { 
        'pyrsched': { 
            'handlers': ['default', ],
            'level': 'INFO',
            'propagate': False
        },
        'apscheduler': {
            'handlers': ['default', ],
            'level': 'INFO',
            'propagate': False            
        },
    } 
}