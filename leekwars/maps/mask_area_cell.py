class MaskAreaCell:

    @staticmethod
    def generateMask(launchType: int, min_: int, max_: int):
        if min_ > max_:
            return []

        cells = []
        if launchType == 9 or launchType == 10:
            length = max_
        elif (launchType & 1) != 0:
            length = max_
        elif (launchType & 4) != 0:
            length = max_ - 1
        else:
            length = max_ // 2

        for i in range(length * 2 + 1):
            for j in range(length * 2 + 1):
                x = i - length
                y = j - length
                in_range = abs(x) + abs(y) <= max_ and abs(x) + abs(y) >= min_
                condition = (((launchType & 1) != 0) and (x == 0 or y == 0)) \
                    or (((launchType & 2) != 0) and abs(x) == abs(y)) \
                    or (((launchType & 4) != 0) and ((x == 0 and y == 0) or (abs(x) != abs(y) and x != 0 and y != 0)))
                if in_range and condition:
                    cells.append([x, y])
        return cells

    @staticmethod
    def generateCircleMask(min_: int, max_: int):
        if min_ > max_:
            return None

        nbCells = 2 * (min_ + max_) * (max_ - min_ + 1)
        if min_ == 0:
            nbCells += 1
        retour = [[0, 0] for _ in range(nbCells)]

        index = 0
        if min_ == 0:
            # Center first
            retour[index] = [0, 0]
            index += 1

        # Go from cells closer to the center to the farther ones
        start_size = 1 if min_ < 1 else min_
        for size in range(start_size, max_ + 1):
            # Add cells counter-clockwise
            for i in range(size):
                retour[index] = [size - i, -i]
                index += 1
            for i in range(size):
                retour[index] = [-i, -(size - i)]
                index += 1
            for i in range(size):
                retour[index] = [-(size - i), i]
                index += 1
            for i in range(size):
                retour[index] = [i, size - i]
                index += 1
        return retour

    @staticmethod
    def generatePlusMask(radius: int):
        nbCells = 1 + radius * 4
        retour = [[0, 0] for _ in range(nbCells)]

        # Center first
        retour[0] = [0, 0]

        index = 1
        for size in range(1, radius + 1):
            retour[index] = [size, 0]
            index += 1
            retour[index] = [0, -size]
            index += 1
            retour[index] = [-size, 0]
            index += 1
            retour[index] = [0, size]
            index += 1
        return retour

    @staticmethod
    def generateXMask(radius: int):
        nbCells = 1 + radius * 4
        retour = [[0, 0] for _ in range(nbCells)]

        # Center first
        retour[0] = [0, 0]

        index = 1
        for size in range(1, radius + 1):
            retour[index] = [size, -size]
            index += 1
            retour[index] = [-size, -size]
            index += 1
            retour[index] = [-size, size]
            index += 1
            retour[index] = [size, size]
            index += 1
        return retour

    @staticmethod
    def generateSquareMask(radius: int):
        nbCells = (1 + 2 * radius) * (1 + 2 * radius)
        retour = [[0, 0] for _ in range(nbCells)]

        # Go from cells closer to the center to the farther ones
        # First, add cells in the inscribed circle
        index = 0
        for cell in MaskAreaCell.generateCircleMask(0, radius):
            retour[index] = cell
            index += 1
        # Then, the corners
        for d in range(radius):
            for i in range(1, radius - d + 1):
                retour[index] = [radius + 1 - i, -(d + i)]
                index += 1
            for i in range(1, radius - d + 1):
                retour[index] = [-(d + i), -(radius + 1 - i)]
                index += 1
            for i in range(1, radius - d + 1):
                retour[index] = [-(radius + 1 - i), d + i]
                index += 1
            for i in range(1, radius - d + 1):
                retour[index] = [d + i, radius + 1 - i]
                index += 1
        return retour
