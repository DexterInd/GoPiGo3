import pickle
import json

serial_file = "list_of_serial_numbers.pkl"
with open(serial_file, 'rb') as f:
    serial_list = pickle.load(f)

refurb = []
with open('16TickRedboardCodes.txt') as f:
    for line in f:
        refurb.append(f.readline().strip('\n'))


print(len(refurb))
print(len(serial_list))
print(len(serial_list)-len(refurb))

for item in refurb:
    if item in serial_list:
        serial_list.remove(item)
print(len(serial_list))

print(serial_list[:5])
for _ in range(4):
    serial_list.pop(0)
print(serial_list[:5])

with open('list_of_serial_numbers.pkl', 'wb') as handle:
    pickle.dump(serial_list, handle, protocol=pickle.HIGHEST_PROTOCOL)