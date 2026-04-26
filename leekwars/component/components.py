from ..items import items as Items


_components = {}


def addComponent(component) -> None:
    _components[component.getTemplate()] = component
    Items.addComponent(component.getTemplate())


def getComponent(id_: int):
    return _components.get(id_)


def getTemplates():
    return _components
