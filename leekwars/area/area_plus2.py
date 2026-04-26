from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaPlus2(MaskArea):

    _area = MaskAreaCell.generatePlusMask(2)

    def __init__(self, attack):
        super().__init__(attack, AreaPlus2._area)
