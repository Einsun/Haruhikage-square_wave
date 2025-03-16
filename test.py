import numpy as np
import time
i=0
a=time.time()
for _ in range(500):
    print(i)
    for _ in range(1000):
        for _ in range(1000):
            i+=1

b=time.time()
print(b-a)