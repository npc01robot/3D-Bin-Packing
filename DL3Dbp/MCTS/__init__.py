import numpy as np

from utils.auxiliary_methods import can_place

# 示例的 containers 和 items
containers = np.array([
    [0, 0, 0, 1, 1, 1, 1, 1, 1,0,0],
    [1, 1, 1, 2, 2, 2, 1, 1, 1,0,0]
])

# [x1,y1,z1,x2,y2,z2,w,h,d,axis,rotation_type]

items = np.array([
    [0, 2, 2, 2],
    [1, 3, 3, 3]
])
results = []

for i in range(3):  # axis x,y,z 轴扩展
    positions = containers.copy()  # 复制 containers
    positions[:, i] += positions[:, i + 6]
    positions[:,3:6] = positions[:,:3] + items[:,1:]
    positions[:,6:9] = items[:,1:]
    positions[:,-2] = i
    positions[:,-1] = items[:,0]
    results.append(positions)
    # for item in items:
    #     tmp = positions.copy()
    #     tmp[:,3:6] = tmp[:,:3] + item[1:]
    #     tmp[:,6:]= item[1:]
    #     results.append(tmp)
result_array = np.array(results).reshape(-1, containers.shape[1])

print(result_array)

print(can_place(containers, result_array))