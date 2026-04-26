from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaCircle2(MaskArea):

    _area = MaskAreaCell.generateCircleMask(0, 2)

    def __init__(self, attack):
        super().__init__(attack, AreaCircle2._area)
