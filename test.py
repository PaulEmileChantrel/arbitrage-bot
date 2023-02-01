def reverse_list(list,start,end):
    if start+1>=end:
        return list

    for i in range((end-start)//2):

        end_index = end-i-1
        list[start+i],list[end_index] = list[end_index],list[start+i]

    return list

print(reverse_list([1,2,3],1,3))
