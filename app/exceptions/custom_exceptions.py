class LogisticsException(Exception):
    pass


class LogisticsNotFoundError(LogisticsException):
    pass


class LogisticsValidationError(LogisticsException):
    pass


class LogisticsBusinessLogicError(LogisticsException):
    pass

