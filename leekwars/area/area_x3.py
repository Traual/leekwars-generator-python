from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaX3(MaskArea):

    _area = MaskAreaCell.generateXMask(3)

    def __init__(self, attack):
        super().__init__(attack, AreaX3._area)
