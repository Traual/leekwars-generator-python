_templates = {}


def getInvocationTemplate(id_: int):
    return _templates.get(id_)


def addInvocationTemplate(invocation) -> None:
    _templates[invocation.getId()] = invocation
