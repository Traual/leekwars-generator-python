from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaSquare1(MaskArea):

    _area = MaskAreaCell.generateSquareMask(1)

    def __init__(self, attack):
        super().__init__(attack, AreaSquare1._area)
