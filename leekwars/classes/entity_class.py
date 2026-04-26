"""Python port of EntityClass.

Most functions follow a pattern: ``f(ai, value=None)`` returns the
attribute for ``ai.getEntity()`` when ``value`` is None, or for the entity
identified by ``value`` otherwise. The Python version exposes both
overloads through a single signature.
"""

from ..attack.entity_state import EntityState
from ..effect.effect import Effect
from ..weapons import weapons as Weapons
from ..action.action_lama import ActionLama
from ..action.action_say import ActionSay
from ..action.action_set_weapon import ActionSetWeapon
from ..entity.say import Say
from ..censorship import check_string


SAY_LENGTH_LIMIT = 100


def _resolve(ai, value):
    if value is None:
        return ai.getEntity()
    return ai.getFight().getEntity(int(value))


def getLife(ai, value=None):
    e = _resolve(ai, value)
    return e.getLife() if e is not None else None


def getForce(ai, value=None):
    e = _resolve(ai, value)
    return e.getStrength() if e is not None else None


def getStrength(ai, value=None):
    return getForce(ai, value)


def getWisdom(ai, value=None):
    e = _resolve(ai, value)
    return e.getWisdom() if e is not None else None


def getResistance(ai, value=None):
    e = _resolve(ai, value)
    return e.getResistance() if e is not None else None


def getAgility(ai, value=None):
    e = _resolve(ai, value)
    return e.getAgility() if e is not None else None


def getScience(ai, value=None):
    e = _resolve(ai, value)
    return e.getScience() if e is not None else None


def getMagic(ai, value=None):
    e = _resolve(ai, value)
    return e.getMagic() if e is not None else None


def getAbsoluteShield(ai, value=None):
    e = _resolve(ai, value)
    return e.getAbsoluteShield() if e is not None else None


def getRelativeShield(ai, value=None):
    e = _resolve(ai, value)
    return e.getRelativeShield() if e is not None else None


def getDamageReturn(ai, value=None):
    e = _resolve(ai, value)
    return e.getDamageReturn() if e is not None else None


def getFrequency(ai, value=None):
    e = _resolve(ai, value)
    return e.getFrequency() if e is not None else None


def getTotalLife(ai, value=None):
    e = _resolve(ai, value)
    return e.getTotalLife() if e is not None else None


def getMP(ai, value=None):
    e = _resolve(ai, value)
    return e.getMP() if e is not None else None


def getTP(ai, value=None):
    e = _resolve(ai, value)
    return e.getTP() if e is not None else None


def getTotalMP(ai, value=None):
    e = _resolve(ai, value)
    return e.getTotalMP() if e is not None else None


def getTotalTP(ai, value=None):
    e = _resolve(ai, value)
    return e.getTotalTP() if e is not None else None


def getCell(ai, value=None):
    e = _resolve(ai, value)
    if e is None or e.getCell() is None:
        return None
    return e.getCell().getId()


def getLevel(ai, value=None):
    e = _resolve(ai, value)
    return e.getLevel() if e is not None else None


def getName(ai, value=None):
    e = _resolve(ai, value)
    return e.getName() if e is not None else None


def getEntityType(ai, value=None):
    e = _resolve(ai, value)
    return e.getType() if e is not None else None


def getTeam(ai, value=None):
    e = _resolve(ai, value)
    return e.getTeam() if e is not None else None


def getTeamID(ai, value=None):
    e = _resolve(ai, value)
    return e.getTeamId() if e is not None else None


def getTeamName(ai, value=None):
    e = _resolve(ai, value)
    return e.getTeamName() if e is not None else None


def getAIID(ai, value=None):
    e = _resolve(ai, value)
    return e.getAIId() if e is not None else None


def getAIName(ai, value=None):
    e = _resolve(ai, value)
    return e.getAIName() if e is not None else None


def getFarmer(ai, value=None):
    e = _resolve(ai, value)
    return e.getFarmer() if e is not None else None


def getFarmerName(ai, value=None):
    e = _resolve(ai, value)
    return e.getFarmerName() if e is not None else None


def getFarmerCountry(ai, value=None):
    e = _resolve(ai, value)
    return e.getFarmerCountry() if e is not None else None


def getCores(ai, value=None):
    e = _resolve(ai, value)
    return e.getCores() if e is not None else None


def getRAM(ai, value=None):
    e = _resolve(ai, value)
    return e.getRAM() if e is not None else None


def isDead(ai, value=None):
    e = _resolve(ai, value)
    return e.isDead() if e is not None else None


def isAlive(ai, value=None):
    e = _resolve(ai, value)
    return e.isAlive() if e is not None else None


def isSummon(ai, value=None):
    e = _resolve(ai, value)
    return e.isSummon() if e is not None else None


def getSummoner(ai, value=None):
    e = _resolve(ai, value)
    if e is None:
        return None
    summoner = e.getSummoner()
    return summoner.getFId() if summoner is not None else None


def getEntityID(ai):
    return ai.getEntity().getFId()


def getCurrentWeapon(ai):
    weapon = ai.getEntity().getWeapon()
    if weapon is None:
        return None
    return weapon.getId()


def getWeapon(ai, value=None):
    if value is None:
        weapon = ai.getEntity().getWeapon()
    else:
        e = ai.getFight().getEntity(int(value))
        if e is None:
            return None
        weapon = e.getWeapon()
    if weapon is None:
        return None
    return weapon.getId()


def getWeapons(ai, value=None):
    e = _resolve(ai, value)
    if e is None:
        return None
    return [w.getId() for w in e.getWeapons()]


def getChips(ai, value=None):
    e = _resolve(ai, value)
    if e is None:
        return None
    return [c.getId() for c in e.getChips()]


def setWeapon(ai, weapon_id) -> bool:
    weapon = Weapons.getWeapon(int(weapon_id))
    if weapon is None or not ai.getEntity().hasWeapon(int(weapon_id)):
        return False
    return ai.getState().setWeapon(ai.getEntity(), weapon)


def say(ai, message) -> None:
    if ai.getEntity().saysTurn >= 2:  # SAY_LIMIT_TURN
        return
    if message is None:
        message = "null"
    message = str(message)
    if len(message) > SAY_LENGTH_LIMIT:
        message = message[:SAY_LENGTH_LIMIT]
    message = check_string(ai.getFight(), message)
    ai.getState().getActions().log(ActionSay(message))
    ai.getState().statistics.say(ai.getEntity(), message)
    ai.getEntity().saysTurn += 1
    ai.getSays().append(Say(ai.getEntity().getFId(), message))


def lama(ai) -> None:
    ai.getState().getActions().log(ActionLama())


def hasState(ai, state, target=None) -> bool:
    e = _resolve(ai, target)
    if e is None:
        return False
    if isinstance(state, int):
        try:
            state = EntityState(state)
        except ValueError:
            return False
    return e.hasState(state)


def getState(ai, target=None):
    e = _resolve(ai, target)
    if e is None:
        return None
    return [s.value for s in e.getStates()]


def getEffects(ai, target=None):
    e = _resolve(ai, target)
    if e is None:
        return None
    result = []
    for ef in e.getEffects():
        result.append([ef.getId(), ef.value, ef.getCaster().getFId(), ef.getTurns(),
                       ef.isCritical(), 0 if ef.getAttack() is None else ef.getAttack().getItemId(),
                       ef.getTarget().getFId(), ef.modifiers])
    return result


def getLaunchedEffects(ai, target=None):
    e = _resolve(ai, target)
    if e is None:
        return None
    result = []
    for ef in e.getLaunchedEffects():
        result.append([ef.getId(), ef.value, ef.getCaster().getFId(), ef.getTurns(),
                       ef.isCritical(), 0 if ef.getAttack() is None else ef.getAttack().getItemId(),
                       ef.getTarget().getFId(), ef.modifiers])
    return result


def getCooldown(ai, chip_id, target=None):
    """Forwarder to ChipClass.getCooldown for entity cooldowns."""
    from . import chip_class
    return chip_class.getCooldown(ai, chip_id, target)


def getRegister(ai, key):
    return ai.getEntity().getRegister(key)


def setRegister(ai, key, value) -> bool:
    return ai.getEntity().setRegister(key, str(value))


def deleteRegister(ai, key) -> None:
    ai.getEntity().deleteRegister(key)


def getRegisters(ai):
    return dict(ai.getEntity().getAllRegisters())
