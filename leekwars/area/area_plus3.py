from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaPlus3(MaskArea):

    _area = MaskAreaCell.generatePlusMask(3)

    def __init__(self, attack):
        super().__init__(attack, AreaPlus3._area)
