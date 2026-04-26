from .mask_area import MaskArea
from ..maps.mask_area_cell import MaskAreaCell


class AreaCircle3(MaskArea):

    _area = MaskAreaCell.generateCircleMask(0, 3)

    def __init__(self, attack):
        super().__init__(attack, AreaCircle3._area)
