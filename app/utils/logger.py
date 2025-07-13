import logging
import sys
from datetime import datetime
from app.config import settings


class ColoredFormatter(logging.Formatter):
     """Custom Formatter with colors for different log levels"""

     COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
     
     def format(self, record):
          color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
          reset =self.COLORS['RESET']

          timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

          log_message = f"{color}[{timestamp}] {record.levelname:8s} {record.name:20s} | {record.getMessage()}{reset}"

          if record.exc_info:
               log_message += f"\n{self.formatException(record.exc_info)}"
          
          return log_message

def setup_logger(name: str = __name__):
     logger = logging.getLogger(name)
     if logger.handlers:
          return logger

     level = logging.DEBUG if settings.DEBUG else logging.INFO
     logger.setLevel(level)

     print(level)

     console_handler = logging.StreamHandler(sys.stdout)
     console_handler.setLevel(level)

     formatter = ColoredFormatter()
     console_handler.setFormatter(formatter)

     logger.addHandler(console_handler)

     if not settings.DEBUG:
          file_handler = logging.FileHandler('app.log')
          file_handler.setLevel(logging.INFO)
          file_formatter = logging.Formatter(
               '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
          )

          file_handler.setFormatter(file_formatter)
          logger.addHandler(file_handler)
     
     return logger

logger = setup_logger()