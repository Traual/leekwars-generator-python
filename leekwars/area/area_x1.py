from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaX1(MaskArea):

    _area = MaskAreaCell.generateXMask(1)

    def __init__(self, attack):
        super().__init__(attack, AreaX1._area)
