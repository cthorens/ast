import random
import os

path_bugs = "bug_collection"

f = open("lines.txt","r")
inject_pot = f.readlines()

count = -1

if os.path.exists(path_bugs):
    os.mkdir(path_bugs)

for ip in inject_pot:
    count += 1

    ip_clean = ip.strip("\n").split(":")
    ip_file = ip_clean[0]
    ip_number = int(ip_clean[1]) - 1

    f2 = open(ip_file,"r")
    f2_lines = f2.readlines()
    bug_line = f2_lines[ip_number]
    
    if " = " in bug_line:
        print(bug_line)
        lop = bug_line.split(" = ")[0]
        print(lop)
        var_name = lop.split(" ")[-1]
        print(var_name)
        
        rand_b = random.randint(0,255) 
        bug_str = "if " + var_name + " as u8 == "+ str(rand_b) + " { panic!(\"Bug found\") }"
        f2_lines.insert(ip_number+1,bug_str+"\n")

        if not os.path.exists(path_bugs):
            os.makedirs(path_bugs)
        new_f2 = open(path_bugs+"/"+ip_file.replace("/","|")+"__"+str(count)+".rs","w")

        f2_lines = "".join(f2_lines)
        new_f2.write(f2_lines)
        
        

        new_f2.close()

    f2.close()

f.close()
