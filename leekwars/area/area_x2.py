from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaX2(MaskArea):

    _area = MaskAreaCell.generateXMask(2)

    def __init__(self, attack):
        super().__init__(attack, AreaX2._area)
