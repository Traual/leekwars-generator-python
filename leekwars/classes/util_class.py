"""Python port of UtilClass."""

from ..action.action_show_cell import ActionShowCell
from ..state.entity import Entity


def getRegisters(ai):
    if ai.getEntity().isSummon():
        registers = ai.getEntity().getSummoner().getAllRegisters()
    else:
        registers = ai.getEntity().getAllRegisters()
    return dict(registers)


def getRegister(ai, key):
    keyString = str(key)
    if ai.getEntity().isSummon():
        return ai.getEntity().getSummoner().getRegister(keyString)
    return ai.getEntity().getRegister(keyString)


def setRegister(ai, key, value) -> bool:
    keyString = str(key)
    valueString = str(value)
    if ai.getEntity().isSummon():
        return ai.getEntity().getSummoner().setRegister(keyString, valueString)
    return ai.getEntity().setRegister(keyString, valueString)


def deleteRegister(ai, key) -> None:
    keyString = str(key)
    if ai.getEntity().isSummon():
        ai.getEntity().getSummoner().deleteRegister(keyString)
    else:
        ai.getEntity().deleteRegister(keyString)


def pause(ai) -> None:
    ai.getLogs().addPause()


def mark(ai, cell, color: int = 0x000000, duration: int = 1) -> bool:
    if isinstance(cell, int):
        if ai.getState().getMap().getCell(cell) is None:
            return False
        cells = [cell]
    elif isinstance(cell, list):
        cells = []
        for value in cell:
            if ai.getState().getMap().getCell(int(value)) is None:
                continue
            cells.append(int(value))
        if len(cells) == 0:
            return False
    else:
        return False
    ai.getLogs().addCell(cells, int(color), int(duration))
    return True


def clearMarks(ai) -> None:
    ai.getLogs().addClearCells()


def markText(ai, cell, text="X", color: int = 0xffffff, duration: int = 1) -> bool:
    # If cell is a dict treat it as map<cell, text>
    if isinstance(cell, dict):
        for k, v in cell.items():
            cellText = str(v)
            finalText = cellText[:10]
            ai.getLogs().addCellText([int(k)], finalText, int(color), int(duration))
        return True

    if isinstance(cell, int):
        if ai.getState().getMap().getCell(cell) is None:
            return False
        cells = [cell]
    elif isinstance(cell, list):
        cells = []
        for value in cell:
            if ai.getState().getMap().getCell(int(value)) is None:
                continue
            cells.append(int(value))
        if len(cells) == 0:
            return False
    else:
        return False
    userText = str(text)
    finalText = userText[:10]
    ai.getLogs().addCellText(cells, finalText, int(color), int(duration))
    return True


def show(ai, cell: int, color: int = 0xffffff) -> bool:
    if ai.getState().getMap().getCell(int(cell)) is None:
        return False
    if ai.getEntity().getTP() < 1:
        return False
    if ai.getEntity().showsTurn >= Entity.SHOW_LIMIT_TURN:
        return False
    ai.getEntity().useTP(1)
    ai.getEntity().showsTurn += 1
    ai.getFight().log(ActionShowCell(int(cell), int(color)))
    ai.getFight().getState().statistics.show(ai.getEntity(), int(cell))
    return True
