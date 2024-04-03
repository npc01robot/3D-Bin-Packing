from py3dbp import Packer, Bin, Item, Painter
import time
start = time.time()

'''

This case is used to demonstrate an example of a packing complex situation.

'''

# init packing function
packer = Packer()
#  init bin
box = Bin('example2',(10, 10, 10), 99,0,1)
packer.addBin(box)
#  add item
packer.addItem(Item('test1', 'test','cube',(1, 2, 3), 1, 1, 100, True,'red'))
packer.addItem(Item('test1', 'test','cube',(1, 2, 3), 1, 1, 100, True,'red'))
packer.addItem(Item('test1', 'test','cube',(1, 2, 3), 1, 1, 100, True,'red'))


packer.addItem(Item('test2', 'test','cube',(4, 5, 5), 1, 1, 100, True,'blue'))
packer.addItem(Item('test2', 'test','cube',(4, 5, 5), 1, 1, 100, True,'blue'))
packer.addItem(Item('test2', 'test','cube',(4, 5, 5), 1, 1, 100, True,'blue'))
packer.addItem(Item('test2', 'test','cube',(4, 5, 5), 1, 1, 100, True,'blue'))
packer.addItem(Item('test3', 'test','cube',(1, 1, 1), 1, 1, 100, True,'gray'))
packer.addItem(Item('test3', 'test','cube',(1, 1, 1), 1, 1, 100, True,'gray'))
packer.addItem(Item('test3', 'test','cube',(1, 1, 1), 1, 1, 100, True,'gray'))
packer.addItem(Item('test4', 'test','cube',(2, 2, 2), 1, 1, 100, True,'orange'))
packer.addItem(Item('test4', 'test','cube',(2, 2, 2), 1, 1, 100, True,'orange'))
packer.addItem(Item('test5', 'test','cube',(4, 5, 2), 1, 1, 100, True,'lawngreen'))
packer.addItem(Item('test5', 'test','cube',(4, 5, 2), 1, 1, 100, True,'lawngreen'))


# calculate packing
packer.pack(
    bigger_first=True,
    distribute_items=100,
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
b = packer.bins[0]
volume = b.width * b.height * b.depth
print(":::::::::::", b.string())

print("FITTED ITEMS:")
volume_t = 0
volume_f = 0
unfitted_name = ''
for item in b.items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("position : ",item.position)
    print("rotation type : ",item.rotation_type)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_t += float(item.width) * float(item.height) * float(item.depth)
    print("***************************************************")
print("***************************************************")
print("UNFITTED ITEMS:")
for item in b.unfitted_items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_f += float(item.width) * float(item.height) * float(item.depth)
    unfitted_name += '{},'.format(item.partno)
    print("***************************************************")
print("***************************************************")
print('space utilization : {}%'.format(round(volume_t / float(volume) * 100 ,2)))
print('residual volumn : ', float(volume) - volume_t )
print('unpack item : ',unfitted_name)
print('unpack item volumn : ',volume_f)
print("gravity distribution : ",b.gravity)
stop = time.time()
print('used time : ',stop - start)

# draw results
painter = Painter(b)
fig = painter.plotBoxAndItems(
    title=b.partno,
    alpha=0.8,
    write_num=False,
    fontsize=10
)
fig.show()