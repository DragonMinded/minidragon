class AssemblerException(Exception):
    pass


class InvalidInstructionException(AssemblerException):
    pass


class DuplicateLabelDefinitionException(AssemblerException):
    pass


class InvalidLabelDefinitionException(AssemblerException):
    pass


class InvalidParameterException(AssemblerException):
    pass


class ParameterOutOfRangeException(AssemblerException):
    pass


class CodeOutOfRangeException(AssemblerException):
    pass
