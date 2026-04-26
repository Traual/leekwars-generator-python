"""Python port of NetworkClass."""

from ..fight.entity.entity_ai import LeekMessage
from ..state.entity import Entity


def sendTo(ai, target, type_, message) -> bool:
    if target == ai.getEntity().getFId():
        return False
    l = ai.getFight().getEntity(target)
    if l is None:
        return False
    if l.getAI() is not None:
        l.getAI().addMessage(LeekMessage(ai.getEntity().getFId(), type_, message))
    return True


def sendAll(ai, type_, message) -> None:
    for e in ai.getState().getTeamEntities(ai.getEntity().getTeam()):
        if e.getFId() == ai.getEntity().getFId():
            continue
        if e.getAI() is not None:
            e.getAI().addMessage(LeekMessage(ai.getEntity().getFId(), type_, message))


def getMessages(ai, target_leek=None):
    if target_leek is None:
        target_leek = ai.getEntity().getFId()
    l = ai.getEntity()
    if target_leek != -1 and target_leek != l.getFId():
        l = ai.getFight().getEntity(target_leek)
        if l is None:
            return None
    lia = l.getAI()
    messages = []
    if l.getType() == Entity.TYPE_MOB and l is not ai.getEntity():
        return messages
    if lia is not None:
        for message in lia.getMessages():
            messages.append([message.getAuthor(), message.getType(), message.getMessage()])
    return messages


def getMessageAuthor(ai, message):
    if len(message) == 3:
        return message[0]
    return 0


def getMessageType(ai, message):
    if len(message) == 3:
        return message[1]
    return 0


def getMessageParams(ai, message):
    if len(message) == 3:
        return message[2]
    return None
