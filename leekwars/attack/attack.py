from ..effect.effect_parameters import EffectParameters


class Attack:

    # Attack use result constants
    USE_CRITICAL = 2
    USE_SUCCESS = 1
    USE_FAILED = 0
    USE_INVALID_TARGET = -1
    USE_NOT_ENOUGH_TP = -2
    USE_INVALID_COOLDOWN = -3
    USE_INVALID_POSITION = -4
    USE_TOO_MANY_SUMMONS = -5
    USE_RESURRECT_INVALID_ENTIITY = -6
    USE_MAX_USES = -7

    # Launch types
    LAUNCH_TYPE_LINE = 1
    LAUNCH_TYPE_DIAGONAL = 2
    LAUNCH_TYPE_STAR = 3
    LAUNCH_TYPE_STAR_INVERTED = 4
    LAUNCH_TYPE_DIAGONAL_INVERTED = 5
    LAUNCH_TYPE_LINE_INVERTED = 6
    LAUNCH_TYPE_CIRCLE = 7

    # Attack types
    TYPE_WEAPON = 1
    TYPE_CHIP = 2

    def __init__(self, minRange, maxRange, launchType, area, los, effects, attackType, itemID, maxUses):
        from ..area.area import Area
        from ..effect.effect import Effect

        self.minRange = minRange
        self.maxRange = maxRange
        self.launchType = launchType
        self.los = los
        self.attackType = attackType
        self.itemID = itemID
        self.maxUses = maxUses

        self.healAttack = 0
        self.dammageAttack = 0
        self.item = None

        self.areaID = area
        self.area = Area.getAreaForType(self, area)

        self.effects = []
        for effect in effects:
            type_ = effect["id"]
            value1 = effect["value1"]
            value2 = effect["value2"]
            turns = effect["turns"]
            targets = effect["targets"]
            modifiers = effect["modifiers"]
            if type_ == Effect.TYPE_HEAL:
                self.healAttack |= targets
            if type_ == Effect.TYPE_DAMAGE or type_ == Effect.TYPE_POISON:
                self.dammageAttack |= targets
            self.effects.append(EffectParameters(type_, value1, value2, turns, targets, modifiers))

    def getArea(self) -> int:
        return self.areaID

    def getTargetCells(self, map_, caster_or_cast_cell, target):
        # Two overloads:
        # (Map, Leek caster, Cell target)
        # (Map, Cell cast_cell, Cell target)
        from ..leek.leek import Leek
        if isinstance(caster_or_cast_cell, Leek):
            caster = caster_or_cast_cell
            return self.area.getArea(map_, caster.getCell(), target, caster)
        cast_cell = caster_or_cast_cell
        return self.area.getArea(map_, cast_cell, target, None)

    def getWeaponTargets(self, state, caster, target):
        from ..effect.effect import Effect

        returnEntities = []
        targetCells = self.area.getArea(state.getMap(), caster.getCell(), target, caster)
        targetEntities = []

        for cell in targetCells:
            if cell.getPlayer(state.getMap()) is not None:
                targetEntities.append(cell.getPlayer(state.getMap()))

        for parameters in self.effects:
            for targetLeek in targetEntities:
                if targetLeek.isDead():
                    continue
                if not self.filterTarget(parameters.getTargets(), caster, targetLeek):
                    continue
                if targetLeek not in returnEntities:
                    returnEntities.append(targetLeek)
            # Always caster?
            if (parameters.getModifiers() & Effect.MODIFIER_ON_CASTER) != 0 and caster not in returnEntities:
                returnEntities.append(caster)
        return returnEntities

    def applyOnCell(self, state, caster, target, critical):
        from ..effect.effect import Effect

        returnEntities = []
        targetCells = self.area.getArea(state.getMap(), caster.getCell(), target, caster)
        targetEntities = []
        areaFactors = {}

        for cell in targetCells:
            player = cell.getPlayer(state.getMap())
            if player is not None and player.isAlive():
                targetEntities.append(player)
                areaFactors[player.getFId()] = self.getPowerForCell(target, cell)

        # Define the jet (random throw)
        jet = state.getRandom().get_double()

        previousEffectTotalValue = 0
        propagate = 0

        for parameters in self.effects:
            if caster.isDead():
                continue

            if parameters.getId() == Effect.TYPE_ATTRACT:
                for entity in targetEntities:
                    destination = state.getMap().getAttractLastAvailableCell(entity.getCell(), target, caster.getCell())
                    state.slideEntity(entity, destination, caster)
            elif parameters.getId() == Effect.TYPE_PUSH:
                for entity in targetEntities:
                    destination = state.getMap().getPushLastAvailableCell(entity.getCell(), target, caster.getCell())
                    state.slideEntity(entity, destination, caster)

            if parameters.getId() == Effect.TYPE_TELEPORT:
                state.teleportEntity(caster, target, caster, self.itemID)
                returnEntities.append(caster)
            elif parameters.getId() == Effect.TYPE_PROPAGATION:
                propagate = int(parameters.getValue1())
            else:
                modifiers = parameters.getModifiers()
                onCaster = (modifiers & Effect.MODIFIER_ON_CASTER) != 0
                stackable = (modifiers & Effect.MODIFIER_STACKABLE) != 0
                effectTotalValue = 0
                multiplied_by_target_count = (modifiers & Effect.MODIFIER_MULTIPLIED_BY_TARGETS) != 0
                not_replaceable = (modifiers & Effect.MODIFIER_NOT_REPLACEABLE) != 0
                effectTargetEntities = []

                for targetEntity in targetEntities:
                    if targetEntity.isDead():
                        continue
                    if not self.filterTarget(parameters.getTargets(), caster, targetEntity):
                        continue
                    if onCaster and targetEntity is caster:
                        continue
                    if not_replaceable and targetEntity.hasEffect(self.itemID):
                        continue
                    if targetEntity not in returnEntities:
                        returnEntities.append(targetEntity)
                    effectTargetEntities.append(targetEntity)

                targetCount = len(effectTargetEntities) if multiplied_by_target_count else 1

                if not onCaster:
                    for targetEntity in effectTargetEntities:
                        aoe = areaFactors[targetEntity.getFId()]
                        effectTotalValue += Effect.createEffect(state, parameters.getId(), parameters.getTurns(), aoe,
                                                                parameters.getValue1(), parameters.getValue2(), critical,
                                                                targetEntity, caster, self, jet, stackable,
                                                                previousEffectTotalValue, targetCount, propagate, modifiers)

                # Always caster
                if onCaster:
                    returnEntities.append(caster)
                    Effect.createEffect(state, parameters.getId(), parameters.getTurns(), 1,
                                        parameters.getValue1(), parameters.getValue2(), critical,
                                        caster, caster, self, jet, stackable,
                                        previousEffectTotalValue, targetCount, propagate, modifiers)

                previousEffectTotalValue = effectTotalValue
        return returnEntities

    def filterTarget(self, targets, caster, target) -> bool:
        from ..effect.effect import Effect

        # Enemies
        if (targets & Effect.TARGET_ENEMIES) == 0 and caster.getTeam() != target.getTeam():
            return False
        # Allies
        if (targets & Effect.TARGET_ALLIES) == 0 and caster.getTeam() == target.getTeam():
            return False
        # Caster
        if (targets & Effect.TARGET_CASTER) == 0 and caster is target:
            return False
        # Non-Summons
        if (targets & Effect.TARGET_NON_SUMMONS) == 0 and not target.isSummon():
            return False
        # Summons
        if (targets & Effect.TARGET_SUMMONS) == 0 and target.isSummon():
            return False
        return True

    def getPowerForCell(self, target_cell, current_cell) -> float:
        from ..area.area_laser_line import AreaLaserLine
        from ..area.area_first_in_line import AreaFirstInLine
        from ..area.area_allies import AreaAllies
        from ..area.area_enemies import AreaEnemies
        from ..maps.pathfinding import Pathfinding

        if isinstance(self.area, (AreaLaserLine, AreaFirstInLine, AreaAllies, AreaEnemies)):
            return 1.0
        dist = Pathfinding.getCaseDistance(target_cell, current_cell)
        return 1 - dist * 0.2

    def getMinRange(self) -> int:
        return self.minRange

    def getMaxRange(self) -> int:
        return self.maxRange

    def getLaunchType(self) -> int:
        return self.launchType

    def needLos(self) -> bool:
        return self.los

    def getEffects(self):
        return self.effects

    def getEffectParametersByType(self, type_):
        for ep in self.effects:
            if ep.getId() == type_:
                return ep
        return None

    def isHealAttack(self, target) -> bool:
        return (self.healAttack & target) != 0

    def isDamageAttack(self, target) -> bool:
        return (self.dammageAttack & target) != 0

    def getItemId(self) -> int:
        return self.itemID

    def getType(self) -> int:
        return self.attackType

    def needsEmptyCell(self) -> bool:
        from ..effect.effect import Effect
        for ep in self.effects:
            if ep.getId() == Effect.TYPE_TELEPORT or ep.getId() == Effect.TYPE_SUMMON or ep.getId() == Effect.TYPE_RESURRECT:
                return True
        return False

    def setItem(self, item) -> None:
        self.item = item

    def getItem(self):
        return self.item

    def getMaxUses(self) -> int:
        return self.maxUses
