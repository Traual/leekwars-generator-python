from .action import Action


class ActionAddEffect(Action):

    @staticmethod
    def createEffect(logs, type_, itemID, caster, target, effectID, value, turns, modifiers):
        r = logs.getEffectId()
        effect = ActionAddEffect(type_, itemID, r, caster.getFId(), target.getFId(), effectID, value, turns, modifiers)
        logs.log(effect)
        return r

    def __init__(self, type_, itemID, id, caster, target, effectID, value, turns, modifiers):
        # Imports kept inline to avoid cycles
        from ..attack.attack_constants import ATTACK_TYPE_CHIP, ATTACK_TYPE_WEAPON
        if type_ == ATTACK_TYPE_CHIP:
            self.type = Action.ADD_CHIP_EFFECT
        elif type_ == ATTACK_TYPE_WEAPON:
            self.type = Action.ADD_WEAPON_EFFECT
        else:
            self.type = type_
        self.itemID = itemID
        self.id = id
        self.caster = caster
        self.target = target
        self.effectID = effectID
        self.value = value
        self.turns = turns
        self.modifiers = modifiers

    def getJSON(self):
        retour = []
        retour.append(self.type)
        retour.append(self.itemID)
        retour.append(self.id)
        retour.append(self.caster)
        retour.append(self.target)
        retour.append(self.effectID)
        retour.append(self.value)
        retour.append(self.turns)
        if self.modifiers != 0:
            retour.append(self.modifiers)
        return retour
