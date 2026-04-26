from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaCircle1(MaskArea):

    _area = MaskAreaCell.generateCircleMask(0, 1)

    def __init__(self, attack):
        super().__init__(attack, AreaCircle1._area)
