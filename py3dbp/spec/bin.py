import copy

import numpy as np

from py3dbp.spec.item import Item
from py3dbp.utils.auxiliary_methods import set2Decimal, intersect
from py3dbp.utils.constants import DEFAULT_NUMBER_OF_DECIMALS, RotationType


class Bin:

    def __init__(self, partno, WHD, max_weight, corner=0, put_type=1):
        """ """
        self.partno = partno
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.max_weight = max_weight
        self.corner = corner
        self.items = []
        self.fit_items = np.array([[0, WHD[0], 0, WHD[1], 0, 0]])
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.fix_point = False
        self.check_stable = False
        self.support_surface_ratio = 0
        self.put_type = put_type
        # used to put gravity distribution
        self.gravity = []

    def formatNumbers(self, number_of_decimals):
        """ """
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.max_weight = set2Decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        """ """
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.partno,
            self.width,
            self.height,
            self.depth,
            self.max_weight,
            self.getVolume(),
        )

    def getVolume(self):
        """ """
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def getTotalWeight(self):
        """ """
        total_weight = 0

        for item in self.items:
            total_weight += item.weight

        return set2Decimal(total_weight, self.number_of_decimals)

    def putItem(self, item, pivot, axis=None):
        """put item in bin"""
        fit = False
        valid_item_position = item.position
        item.position = pivot
        rotate = RotationType.ALL if item.updown == True else RotationType.Notupdown
        for i in range(0, len(rotate)):
            item.rotation_type = i
            dimension = item.getDimension()
            # rotatate
            if (
                    self.width < pivot[0] + dimension[0]
                    or self.height < pivot[1] + dimension[1]
                    or self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                # cal total weight
                if self.getTotalWeight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                # fix point float prob
                if self.fix_point == True:

                    [w, h, d] = dimension
                    [x, y, z] = [float(pivot[0]), float(pivot[1]), float(pivot[2])]

                    for i in range(3):
                        # fix height
                        y = self.checkHeight(
                            [x, x + float(w), y, y + float(h), z, z + float(d)]
                        )
                        # fix width
                        x = self.checkWidth(
                            [x, x + float(w), y, y + float(h), z, z + float(d)]
                        )
                        # fix depth
                        z = self.checkDepth(
                            [x, x + float(w), y, y + float(h), z, z + float(d)]
                        )

                    # check stability on item
                    # rule :
                    # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
                    # 2. If there is no support under any vertices of the bottom of the item, then fit = False.
                    if self.check_stable == True:
                        # Cal the surface area of ​​item.
                        item_area_lower = int(dimension[0] * dimension[1])
                        # Cal the surface area of ​​the underlying support.
                        support_area_upper = 0
                        for i in self.fit_items:
                            # Verify that the lower support surface area is greater than the upper support surface area * support_surface_ratio.
                            if z == i[5]:
                                area = len(
                                    set([j for j in range(int(x), int(x + int(w)))])
                                    & set([j for j in range(int(i[0]), int(i[1]))])
                                ) * len(
                                    set([j for j in range(int(y), int(y + int(h)))])
                                    & set([j for j in range(int(i[2]), int(i[3]))])
                                )
                                support_area_upper += area

                        # If not , get four vertices of the bottom of the item.
                        if (
                                support_area_upper / item_area_lower
                                < self.support_surface_ratio
                        ):
                            four_vertices = [
                                [x, y],
                                [x + float(w), y],
                                [x, y + float(h)],
                                [x + float(w), y + float(h)],
                            ]
                            #  If any vertices is not supported, fit = False.
                            c = [False, False, False, False]
                            for i in self.fit_items:
                                if z == i[5]:
                                    for jdx, j in enumerate(four_vertices):
                                        if (i[0] <= j[0] <= i[1]) and (
                                                i[2] <= j[1] <= i[3]
                                        ):
                                            c[jdx] = True
                            if False in c:
                                item.position = valid_item_position
                                fit = False
                                return fit

                    self.fit_items = np.append(
                        self.fit_items,
                        np.array([[x, x + float(w), y, y + float(h), z, z + float(d)]]),
                        axis=0,
                    )
                    item.position = [set2Decimal(x), set2Decimal(y), set2Decimal(z)]

                if fit:
                    self.items.append(copy.deepcopy(item))

            else:
                item.position = valid_item_position

            return fit

        else:
            item.position = valid_item_position

        return fit

    def checkDepth(self, unfix_point):
        """fix item position z"""
        z_ = [[0, 0], [float(self.depth), float(self.depth)]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
            # find intersection on x set and y set.
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0:
                z_.append([float(j[4]), float(j[5])])
        top_depth = unfix_point[5] - unfix_point[4]
        # find diff set on z_.
        z_ = sorted(z_, key=lambda z_: z_[1])
        for j in range(len(z_) - 1):
            if z_[j + 1][0] - z_[j][1] >= top_depth:
                return z_[j][1]
        return unfix_point[4]

    def checkWidth(self, unfix_point):
        """fix item position x"""
        x_ = [[0, 0], [float(self.width), float(self.width)]]
        for j in self.fit_items:
            # creat z set
            z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
            # find intersection on z set and y set.
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0:
                x_.append([float(j[0]), float(j[1])])
        top_width = unfix_point[1] - unfix_point[0]
        # find diff set on x_bottom and x_top.
        x_ = sorted(x_, key=lambda x_: x_[1])
        for j in range(len(x_) - 1):
            if x_[j + 1][0] - x_[j][1] >= top_width:
                return x_[j][1]
        return unfix_point[0]

    def checkHeight(self, unfix_point):
        """fix item position y"""
        y_ = [[0, 0], [float(self.height), float(self.height)]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
            # creat z set
            z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
            # find intersection on x set and z set.
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0:
                y_.append([float(j[2]), float(j[3])])
        top_height = unfix_point[3] - unfix_point[2]
        # find diff set on y_bottom and y_top.
        y_ = sorted(y_, key=lambda y_: y_[1])
        for j in range(len(y_) - 1):
            if y_[j + 1][0] - y_[j][1] >= top_height:
                return y_[j][1]

        return unfix_point[2]

    def addCorner(self):
        """add container coner"""
        if self.corner != 0:
            corner = set2Decimal(self.corner)
            corner_list = []
            for i in range(8):
                a = Item(
                    partno="corner{}".format(i),
                    name="corner",
                    typeof="cube",
                    WHD=(corner, corner, corner),
                    weight=0,
                    level=0,
                    loadbear=0,
                    updown=True,
                    color="#000000",
                )

                corner_list.append(a)
            return corner_list

    def putCorner(self, info, item):
        """put coner in bin"""
        fit = False
        x = set2Decimal(self.width - self.corner)
        y = set2Decimal(self.height - self.corner)
        z = set2Decimal(self.depth - self.corner)
        pos = [
            [0, 0, 0],
            [0, 0, z],
            [0, y, z],
            [0, y, 0],
            [x, y, 0],
            [x, 0, 0],
            [x, 0, z],
            [x, y, z],
        ]
        item.position = pos[info]
        self.items.append(item)

        corner = [
            float(item.position[0]),
            float(item.position[0]) + float(self.corner),
            float(item.position[1]),
            float(item.position[1]) + float(self.corner),
            float(item.position[2]),
            float(item.position[2]) + float(self.corner),
        ]

        self.fit_items = np.append(self.fit_items, np.array([corner]), axis=0)
        return

    def clearBin(self):
        """clear item which in bin"""
        self.items = []
        self.fit_items = np.array([[0, self.width, 0, self.height, 0, 0]])
        return