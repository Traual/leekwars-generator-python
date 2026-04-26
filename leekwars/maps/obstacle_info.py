class ObstacleInfo:

    _obstacles = {}

    def __init__(self, size: int):
        self.size = size

    @staticmethod
    def get(id_: int):
        return ObstacleInfo._obstacles.get(id_)


# Static initialization (matching Java static block)
ObstacleInfo._obstacles[5] = ObstacleInfo(1)
ObstacleInfo._obstacles[20] = ObstacleInfo(1)
ObstacleInfo._obstacles[21] = ObstacleInfo(1)
ObstacleInfo._obstacles[22] = ObstacleInfo(1)
ObstacleInfo._obstacles[38] = ObstacleInfo(1)
ObstacleInfo._obstacles[40] = ObstacleInfo(1)
ObstacleInfo._obstacles[41] = ObstacleInfo(1)
ObstacleInfo._obstacles[42] = ObstacleInfo(1)
ObstacleInfo._obstacles[48] = ObstacleInfo(1)
ObstacleInfo._obstacles[50] = ObstacleInfo(1)
ObstacleInfo._obstacles[63] = ObstacleInfo(1)
ObstacleInfo._obstacles[66] = ObstacleInfo(1)
ObstacleInfo._obstacles[53] = ObstacleInfo(1)
ObstacleInfo._obstacles[55] = ObstacleInfo(1)
ObstacleInfo._obstacles[57] = ObstacleInfo(1)
ObstacleInfo._obstacles[59] = ObstacleInfo(1)
ObstacleInfo._obstacles[62] = ObstacleInfo(1)
ObstacleInfo._obstacles[32] = ObstacleInfo(1)

ObstacleInfo._obstacles[11] = ObstacleInfo(2)
ObstacleInfo._obstacles[17] = ObstacleInfo(2)
ObstacleInfo._obstacles[18] = ObstacleInfo(2)
ObstacleInfo._obstacles[34] = ObstacleInfo(2)
ObstacleInfo._obstacles[43] = ObstacleInfo(2)
ObstacleInfo._obstacles[44] = ObstacleInfo(2)
ObstacleInfo._obstacles[45] = ObstacleInfo(2)
ObstacleInfo._obstacles[46] = ObstacleInfo(2)
ObstacleInfo._obstacles[47] = ObstacleInfo(2)
ObstacleInfo._obstacles[49] = ObstacleInfo(2)
ObstacleInfo._obstacles[64] = ObstacleInfo(2)
ObstacleInfo._obstacles[65] = ObstacleInfo(2)
ObstacleInfo._obstacles[52] = ObstacleInfo(2)
ObstacleInfo._obstacles[54] = ObstacleInfo(2)
ObstacleInfo._obstacles[56] = ObstacleInfo(2)
ObstacleInfo._obstacles[58] = ObstacleInfo(2)
ObstacleInfo._obstacles[61] = ObstacleInfo(2)
ObstacleInfo._obstacles[31] = ObstacleInfo(1)

ObstacleInfo._obstacles[51] = ObstacleInfo(3)
ObstacleInfo._obstacles[39] = ObstacleInfo(4)
ObstacleInfo._obstacles[60] = ObstacleInfo(5)
