import sys

file_to_find = sys.argv[1]
file_to_replace = sys.argv[2]
file_to_update = sys.argv[3]

with open(file_to_find) as f:
    text_find = f.read()
    
with open(file_to_replace) as f:
    text_replace = f.read()    
    
with open(file_to_update) as f:
    text_update = f.read()
    
pos = text_update.find(text_find)    
if pos != -1:
    text_new = text_update[0:pos]
    text_new += text_replace
    text_new += text_update[pos+len(text_find):]
    with open(file_to_update, 'w') as f:
        f.write(text_new)
else:
    print("Could not update ", file_to_update)    
            