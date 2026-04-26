from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaSquare2(MaskArea):

    _area = MaskAreaCell.generateSquareMask(2)

    def __init__(self, attack):
        super().__init__(attack, AreaSquare2._area)
